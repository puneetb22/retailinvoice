
"""
Centralized inventory management utilities
Handles all batch-level inventory operations
"""

import datetime
from decimal import Decimal

class InventoryManager:
    """Centralized inventory management for batch operations"""
    
    def __init__(self, db_handler):
        self.db = db_handler
    
    def get_available_batches(self, product_id):
        """Get all available batches for a product with FEFO ordering"""
        query = """
            SELECT b.id, b.batch_number, b.quantity, b.expiry_date, 
                   b.cost_price, b.manufacturing_date, 
                   COALESCE(b.selling_price, p.selling_price) as selling_price
            FROM batches b
            JOIN products p ON b.product_id = p.id
            WHERE b.product_id = ? AND b.quantity > 0
            ORDER BY 
                CASE WHEN b.expiry_date IS NULL THEN 1 ELSE 0 END,
                b.expiry_date ASC,
                b.manufacturing_date ASC
        """
        return self.db.fetchall(query, (product_id,))
    
    def get_batch_details(self, batch_id):
        """Get detailed information about a specific batch"""
        query = """
            SELECT b.id, b.batch_number, b.quantity, b.expiry_date, 
                   b.cost_price, b.manufacturing_date, 
                   COALESCE(b.selling_price, p.selling_price) as selling_price, 
                   p.name, b.product_id
            FROM batches b
            JOIN products p ON b.product_id = p.id
            WHERE b.id = ?
        """
        return self.db.fetchone(query, (batch_id,))
    
    def update_batch_quantity(self, batch_id, quantity_change, transaction_type, reference_type=None, reference_id=None, notes=None):
        """Update batch quantity and log the transaction"""
        try:
            # Get current batch info
            batch = self.get_batch_details(batch_id)
            if not batch:
                raise ValueError(f"Batch {batch_id} not found")
            
            current_quantity = batch[2]
            new_quantity = current_quantity + quantity_change
            
            if new_quantity < 0:
                raise ValueError(f"Insufficient stock. Available: {current_quantity}, Required: {abs(quantity_change)}")
            
            # Update batch quantity
            self.db.execute(
                "UPDATE batches SET quantity = ? WHERE id = ?",
                (new_quantity, batch_id)
            )
            
            # Log the transaction
            log_data = {
                "batch_id": batch_id,
                "product_id": batch[0] if len(batch) > 7 else None,  # Assuming product_id is in the batch info
                "transaction_type": transaction_type,
                "quantity_change": quantity_change,
                "quantity_before": current_quantity,
                "quantity_after": new_quantity,
                "reference_type": reference_type,
                "reference_id": reference_id,
                "notes": notes
            }
            
            # Get product_id if not available
            if not log_data["product_id"]:
                product_query = "SELECT product_id FROM batches WHERE id = ?"
                product_result = self.db.fetchone(product_query, (batch_id,))
                log_data["product_id"] = product_result[0] if product_result else None
            
            self.db.insert("stock_log", log_data)
            
            return True
            
        except Exception as e:
            print(f"Error updating batch quantity: {e}")
            return False
    
    def find_or_create_batch(self, product_id, batch_number, expiry_date, cost_price, manufacturing_date=None, selling_price=None):
        """Find existing batch or create new one"""
        # Try to find existing batch with same criteria
        query = """
            SELECT id, quantity FROM batches 
            WHERE product_id = ? AND batch_number = ? 
            AND (expiry_date = ? OR (expiry_date IS NULL AND ? IS NULL))
            AND cost_price = ?
        """
        existing = self.db.fetchone(query, (product_id, batch_number, expiry_date, expiry_date, cost_price))
        
        if existing:
            return existing[0], existing[1]  # batch_id, current_quantity
        else:
            # Create new batch
            batch_data = {
                "product_id": product_id,
                "batch_number": batch_number,
                "quantity": 0,  # Will be updated by caller
                "expiry_date": expiry_date,
                "cost_price": cost_price,
                "manufacturing_date": manufacturing_date,
                "purchase_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add selling price if provided
            if selling_price is not None:
                batch_data["selling_price"] = selling_price
            
            batch_id = self.db.insert("batches", batch_data)
            return batch_id, 0  # new batch_id, 0 quantity
    
    def get_total_stock(self, product_id):
        """Get total stock across all batches for a product"""
        query = "SELECT COALESCE(SUM(quantity), 0) FROM batches WHERE product_id = ?"
        result = self.db.fetchone(query, (product_id,))
        return result[0] if result else 0
    
    def process_sale(self, cart_items, sale_id):
        """Process inventory reduction for a sale"""
        try:
            for item in cart_items:
                batch_id = item.get("batch_id")
                quantity = item.get("quantity", 0)
                
                if batch_id and quantity > 0:
                    success = self.update_batch_quantity(
                        batch_id=batch_id,
                        quantity_change=-quantity,
                        transaction_type="SALE",
                        reference_type="SALE",
                        reference_id=sale_id,
                        notes=f"Sale of {quantity} units"
                    )
                    
                    if not success:
                        raise Exception(f"Failed to update batch {batch_id}")
            
            return True
        except Exception as e:
            print(f"Error processing sale inventory: {e}")
            return False
    
    def reverse_sale(self, sale_id):
        """Reverse inventory changes for a cancelled sale"""
        try:
            # Get all stock log entries for this sale
            query = """
                SELECT batch_id, quantity_change FROM stock_log 
                WHERE reference_type = 'SALE' AND reference_id = ?
            """
            sale_logs = self.db.fetchall(query, (sale_id,))
            
            for log in sale_logs:
                batch_id, original_change = log
                # Reverse the change
                self.update_batch_quantity(
                    batch_id=batch_id,
                    quantity_change=-original_change,
                    transaction_type="SALE_REVERSAL",
                    reference_type="SALE_REVERSAL",
                    reference_id=sale_id,
                    notes=f"Reversal of sale {sale_id}"
                )
            
            return True
        except Exception as e:
            print(f"Error reversing sale: {e}")
            return False
