
"""
Sale reversal utilities for handling invoice cancellations and returns
"""

from utils.inventory_manager import InventoryManager

class SaleReversalManager:
    """Handle sale reversals and returns"""
    
    def __init__(self, db_handler):
        self.db = db_handler
        self.inventory_manager = InventoryManager(db_handler)
    
    def reverse_sale(self, sale_id):
        """Reverse a complete sale and restore inventory"""
        try:
            # Begin transaction
            self.db.begin()
            
            # Get sale details
            sale = self.db.fetchone("SELECT * FROM sales WHERE id = ?", (sale_id,))
            if not sale:
                raise ValueError(f"Sale {sale_id} not found")
            
            # Get sale items
            sale_items = self.db.fetchall("""
                SELECT si.*, b.id as batch_id 
                FROM sale_items si
                LEFT JOIN batches b ON si.product_id = b.product_id
                WHERE si.sale_id = ?
            """, (sale_id,))
            
            # Reverse inventory changes
            for item in sale_items:
                if item[-1]:  # batch_id exists
                    batch_id = item[-1]
                    quantity = item[5]  # quantity column
                    
                    # Restore quantity to batch
                    self.inventory_manager.update_batch_quantity(
                        batch_id=batch_id,
                        quantity_change=quantity,
                        transaction_type="SALE_REVERSAL",
                        reference_type="SALE_REVERSAL",
                        reference_id=sale_id,
                        notes=f"Sale reversal for sale {sale_id}"
                    )
            
            # Mark sale as cancelled
            self.db.update("sales", {"payment_status": "CANCELLED"}, f"id = {sale_id}")
            
            # Commit transaction
            self.db.commit()
            
            return True
            
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            print(f"Error reversing sale: {e}")
            return False
    
    def process_return(self, sale_id, return_items):
        """Process partial returns for specific items"""
        try:
            # Begin transaction
            self.db.begin()
            
            for item in return_items:
                batch_id = item.get("batch_id")
                return_quantity = item.get("return_quantity", 0)
                
                if batch_id and return_quantity > 0:
                    # Restore quantity to batch
                    self.inventory_manager.update_batch_quantity(
                        batch_id=batch_id,
                        quantity_change=return_quantity,
                        transaction_type="RETURN",
                        reference_type="RETURN",
                        reference_id=sale_id,
                        notes=f"Return of {return_quantity} units from sale {sale_id}"
                    )
            
            # Commit transaction
            self.db.commit()
            
            return True
            
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            print(f"Error processing return: {e}")
            return False
