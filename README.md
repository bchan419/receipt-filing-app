# Receipt OCR App - Full Stack

A complete receipt processing application with React frontend and FastAPI backend, powered by Google Cloud Vision AI.

## 🚀 Features

- **AI-Powered OCR**: Google Cloud Vision API for accurate text extraction
- **Multi-Format Support**: JPG, PNG, WebP, HEIC images
- **Multi-Currency**: Automatic detection of NTD, HKD, USD
- **Smart Categorization**: Configurable expense categories with keyword matching
- **Batch Processing**: Upload multiple receipts at once
- **Editable Results**: Review and modify extracted data
- **Export Options**: CSV, Excel, and Google Sheets compatible
- **Real-Time Processing**: Live upload progress and status updates

## 📁 Project Structure

```
receipt-filing-app/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── services/api.js  # API integration layer
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
├── src/                     # FastAPI backend
│   ├── main.py             # API server
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   ├── config/             # Configuration
│   └── utils/              # Utilities
├── tests/                  # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── start_fullstack.sh     # One-click startup script
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Vision API credentials

### 1. Clone and Setup Backend
```bash
# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Google Cloud Vision API
cp .env.example .env
# Edit .env with your Google Cloud credentials
```

### 2. Setup Frontend
```bash
cd frontend
npm install
```

### 3. Quick Start
```bash
# Start both frontend and backend
./start_fullstack.sh
```

**Access your app:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Manual Setup

### Backend Only
```bash
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
export GOOGLE_CLOUD_PROJECT=your-project-id
cd src && python main.py
```

### Frontend Only
```bash
cd frontend
npm run dev
```

## 📋 Usage

1. **Upload Receipts**: Drag and drop or click to select receipt images
2. **AI Processing**: Google Cloud Vision AI extracts text and data
3. **Review Results**: Edit any incorrectly extracted information
4. **Categorize**: Automatic categorization with custom category support
5. **Export**: Download CSV/Excel or copy to Google Sheets

## 🧪 Testing

```bash
# Run comprehensive test suite
python run_tests.py

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py coverage
```

## 🔑 API Endpoints

- `POST /upload` - Process receipt images
- `GET /categories` - Get expense categories
- `POST /export/csv` - Export to CSV
- `POST /export/excel` - Export to Excel
- `POST /summary` - Get statistics

## 🌐 Environment Variables

**Backend (.env):**
```bash
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
API_HOST=0.0.0.0
API_PORT=8000
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
```

## 📊 Supported Data

**Currencies**: USD, NTD, HKD
**Categories**: Food & Dining, Transportation, Shopping, Utilities, Healthcare, Entertainment, Office Supplies, Other
**Languages**: English, Traditional Chinese
**Formats**: JPG, JPEG, PNG, WebP, HEIC

## 🔒 Security

- Input validation for all file uploads
- File size limits (10MB per image)
- CORS configuration for frontend integration
- Error handling without exposing sensitive data

## 💰 Costs

- **Development**: Free (local development)
- **Google Cloud Vision**: ~$1.50 per 1000 images
- **Deployment**: Variable (depending on hosting choice)

## 🚨 Troubleshooting

**Common Issues:**

1. **API Connection Failed**
   - Ensure backend is running on port 8000
   - Check CORS settings
   - Verify network connectivity

2. **Google Cloud Vision Errors**
   - Verify credentials file path
   - Check API key permissions
   - Ensure Vision API is enabled

3. **Upload Failures**
   - Check file format (JPG/PNG/WebP/HEIC only)
   - Verify file size (under 10MB)
   - Ensure stable internet connection

## 🔄 Development

**Frontend Development:**
```bash
cd frontend
npm run dev  # Development server with hot reload
npm run build  # Production build
```

**Backend Development:**
```bash
cd src
python main.py  # Development server with auto-reload
```

## 📈 Performance

- **Frontend**: React with Vite for fast development
- **Backend**: FastAPI with async processing
- **OCR**: Google Cloud Vision optimized for receipts
- **Export**: Efficient CSV/Excel generation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Run tests to verify setup
- Check Google Cloud Vision API status