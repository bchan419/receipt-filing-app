import csv
import io
import pandas as pd
from typing import List
from fastapi.responses import StreamingResponse
from models.receipt import ReceiptData

class ExportService:
    """Service for exporting receipt data to various formats"""
    
    def export_to_csv(self, receipts: List[ReceiptData]) -> StreamingResponse:
        """Export receipts to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Merchant', 'Category', 'Amount', 'Currency', 'Items'])
        
        # Write data
        for receipt in receipts:
            writer.writerow([
                receipt.date.strftime('%Y-%m-%d') if receipt.date else '',
                receipt.merchant or '',
                receipt.category or '',
                str(receipt.amount) if receipt.amount else '',
                receipt.currency or '',
                '; '.join(receipt.items) if receipt.items else ''
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename=receipts.csv'}
        )
    
    def export_to_excel(self, receipts: List[ReceiptData]) -> StreamingResponse:
        """Export receipts to Excel format"""
        # Convert to DataFrame
        data = []
        for receipt in receipts:
            data.append({
                'Date': receipt.date.strftime('%Y-%m-%d') if receipt.date else '',
                'Merchant': receipt.merchant or '',
                'Category': receipt.category or '',
                'Amount': float(receipt.amount) if receipt.amount else 0,
                'Currency': receipt.currency or '',
                'Items': '; '.join(receipt.items) if receipt.items else ''
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Receipts', index=False)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename=receipts.xlsx'}
        )
    
    def get_summary_stats(self, receipts: List[ReceiptData]) -> dict:
        """Get summary statistics for receipts"""
        if not receipts:
            return {}
        
        total_amount = sum(r.amount for r in receipts if r.amount)
        categories = {}
        currencies = {}
        
        for receipt in receipts:
            if receipt.category:
                categories[receipt.category] = categories.get(receipt.category, 0) + 1
            if receipt.currency and receipt.amount:
                currencies[receipt.currency] = currencies.get(receipt.currency, 0) + float(receipt.amount)
        
        return {
            'total_receipts': len(receipts),
            'total_amount': float(total_amount),
            'categories': categories,
            'currencies': currencies
        }