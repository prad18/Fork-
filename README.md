# Fork+ - AI-Powered Sustainability Assistant for Restaurants

Fork+ is a comprehensive full-stack web application that helps restaurants reduce their environmental impact through AI-driven analysis of invoices and menus, carbon footprint tracking, and sustainable ingredient recommendations.

## 🌟 Features

### Phase 1 (Current Implementation)
- **🧾 Invoice and Menu Analyzer**
  - Upload invoices (PDF, images) with drag-and-drop interface
  - OCR text extraction using PaddleOCR (high accuracy)
  - LLM-based parsing for robust ingredient extraction
  - Automatic categorization of ingredients (proteins, vegetables, dairy, grains)
  - Fallback to regex-based parsing for offline scenarios

- **🌍 Carbon Footprint Tracker**
  - Calculate CO₂ emissions by mapping ingredients to carbon intensity database
  - Break down emissions into Scope 1, 2, and 3
  - Interactive dashboard with visualizations
  - Real-time insights and recommendations

- **📊 Dashboard & Analytics**
  - Modern React dashboard with real-time data
  - Beautiful charts using Recharts
  - Progress tracking and statistics
  - Quick action buttons for common tasks

- **🔐 Authentication & Security**
  - JWT-based authentication
  - Secure file upload with validation
  - User-specific data isolation

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database for structured data
- **SQLAlchemy** - ORM for database operations
- **PaddleOCR** - High-accuracy text extraction from images/PDFs
- **Ollama + Llama 3.2** - Local LLM for robust invoice parsing
- **JWT** - Authentication and authorization
- **Celery + Redis** - Background task processing (ready for scaling)

### Frontend
- **React** with TypeScript
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Data visualization
- **React Dropzone** - File upload interface

### AI/ML
- **OCR Service** - PaddleOCR for highly accurate text extraction
- **LLM Service** - Local Ollama (Llama 3.2) for robust invoice parsing
- **Fallback Parser** - Regex-based parsing for offline scenarios
- **Carbon Calculator** - Emission calculation engine

## 🏗️ Project Structure

```
Fork+/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration and settings
│   │   ├── models.py       # SQLAlchemy database models
│   │   ├── routers/        # API route handlers
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── invoice.py  # Invoice upload and processing
│   │   │   ├── menu.py     # Menu management
│   │   │   └── carbon.py   # Carbon footprint endpoints
│   │   └── services/       # Business logic services
│   │       ├── ocr_service.py      # Text extraction
│   │       ├── nlp_service.py      # Invoice parsing
│   │       └── carbon_service.py   # Emission calculations
│   ├── requirements.txt    # Python dependencies
│   └── main.py            # FastAPI application entry point
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context for state management
│   │   └── App.tsx        # Main application component
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- PaddleOCR (automatically installed)
- Ollama (for LLM parsing) - Optional but recommended

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your database credentials and API keys
   ```

5. **Run the server**
   ```bash
   python main.py
   ```

### LLM Setup (Recommended for Best Results)

Fork+ now includes an advanced LLM-based invoice parser that provides much more accurate results than regex-based parsing. This is optional but highly recommended.

1. **Run the automated setup script**
   ```bash
   # From the Fork+ root directory
   setup-llm.bat
   ```

2. **Manual setup (if script fails)**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then install a model:
   ollama pull llama3.2:latest    # Recommended (2GB)
   # OR
   ollama pull llama3.1:latest    # Good alternative (4.7GB)
   # OR  
   ollama pull phi3:latest        # Lightweight option (2.3GB)
   ```

3. **Start Ollama service**
   ```bash
   ollama serve
   ```

4. **Test the setup**
   ```bash
   # From Fork+ root directory
   python test_invoice_processing.py
   ```

The LLM parser provides:
- ✅ **Much higher accuracy** for complex invoices
- ✅ **Better handling** of table layouts and formatting
- ✅ **Automatic categorization** of ingredients
- ✅ **Robust parsing** of prices, quantities, and units
- ✅ **Local processing** - no external API calls needed

**Note:** The system will automatically fall back to regex-based parsing if the LLM is not available.

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 📱 Usage

1. **Register/Login** - Create an account for your restaurant
2. **Upload Invoices** - Drag and drop PDF or image invoices
3. **View Processing** - Watch as AI extracts and categorizes ingredients
4. **Analyze Carbon Footprint** - View emissions breakdown and insights
5. **Track Progress** - Monitor your sustainability metrics over time

## 🔮 Upcoming Features (Next Phases)

### Phase 2: Enhanced AI & Recommendations
- **🥕 Sustainable Ingredient Recommender**
  - AI-powered alternative ingredient suggestions
  - Local sourcing recommendations
  - Seasonal ingredient optimization
  - Cost-benefit analysis

### Phase 3: Gamification & Engagement
- **🏆 Gamification Engine**
  - Achievement badges and milestones
  - Progress tracking and leaderboards
  - Monthly challenges and goals
  - Social sharing features

### Phase 4: Advanced Analytics
- **🗺️ Net-Zero Roadmap Generator**
  - Personalized action plans
  - Timeline-based sustainability goals
  - Budget-conscious recommendations
  - Integration with vendor systems

### Phase 5: Market Integration
- **📊 Vendor Comparison Tool**
  - Side-by-side vendor analysis
  - Real-time pricing and emission data
  - Certification tracking
  - Automated ordering suggestions

- **🔁 Offset Integration**
  - Carbon offset marketplace integration
  - Automated offset purchasing
  - Impact tracking and verification

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Invoice Processing Tests
```bash
# Test the complete pipeline
python test_invoice_processing.py

# Test with a specific image file
python test_invoice_processing.py path/to/invoice.jpg
```

## 🛠️ API Endpoints

### Invoice Processing
- `POST /api/invoices/upload` - Upload and process invoice
- `GET /api/invoices/service/status` - Check service status
- `POST /api/invoices/test/parse-text` - Test LLM parser with text
- `POST /api/invoices/{id}/reprocess-with-llm` - Reprocess with LLM
- `GET /api/invoices/{id}/analysis` - Get comprehensive analysis

### Example API Usage
```bash
# Check if services are ready
curl http://localhost:8000/api/invoices/service/status

# Test LLM parser
curl -X POST http://localhost:8000/api/invoices/test/parse-text \
  -H "Content-Type: application/json" \
  -d '{"text": "INVOICE\nVendor: Test Company\n1 lb Organic Carrots $2.50"}'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🌱 Environmental Impact

Fork+ is designed to help restaurants achieve:
- **30-50% reduction** in supply chain emissions
- **20-30% cost savings** through optimized sourcing
- **Net-zero goals** through systematic tracking and improvement
- **Compliance** with sustainability regulations and certifications

---

*Built with 💚 for a more sustainable restaurant industry*
