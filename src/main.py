from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

from services.ocr_service import OCRService
from services.export_service import ExportService
from models.receipt import ReceiptData, ProcessingResult, ExportRequest
from utils.file_handler import FileHandler
from config.categories import CategoryConfig

load_dotenv()

app = FastAPI(title="Receipt OCR App", version="1.0.0")

# CORS middleware for frontend integration (mobile-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (mobile testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
export_service = ExportService()
file_handler = FileHandler()
category_config = CategoryConfig()

@app.get("/")
async def root():
    return {"message": "Receipt OCR App API"}

@app.post("/upload", response_model=List[ProcessingResult])
async def upload_receipts(files: List[UploadFile] = File(...)):
    """Process multiple receipt images and extract data"""
    results = []
    
    for file in files:
        try:
            # Validate file type
            if not file_handler.is_valid_image(file.filename):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type: {file.filename}"
                )
            
            # Read file content
            file_content = await file.read()
            
            # Process with OCR
            extracted_data = await ocr_service.extract_receipt_data(file_content)
            
            # Categorize
            category = category_config.categorize_receipt(extracted_data)
            extracted_data.category = category
            
            results.append(ProcessingResult(
                filename=file.filename,
                status="success",
                data=extracted_data
            ))
            
        except Exception as e:
            results.append(ProcessingResult(
                filename=file.filename,
                status="error",
                error=str(e)
            ))
    
    return results

@app.get("/categories")
async def get_categories():
    """Get available expense categories"""
    return category_config.get_all_categories()

@app.post("/export/csv")
async def export_csv(request: ExportRequest):
    """Export receipt data to CSV format"""
    return export_service.export_to_csv(request.receipts)

@app.post("/export/excel")
async def export_excel(request: ExportRequest):
    """Export receipt data to Excel format"""
    return export_service.export_to_excel(request.receipts)

@app.post("/summary")
async def get_summary(receipts: List[ReceiptData]):
    """Get summary statistics for receipts"""
    return export_service.get_summary_stats(receipts)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)