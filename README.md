# Shopify Taxonomy Super Classifier

An AI-powered product classification system that combines the best features from 6 different Shopify taxonomy classifiers into one comprehensive solution.

## Features

### Core Classification
- **Hybrid Classification Engine**: Combines lexical, semantic, and image-based classification
- **Multi-Provider LLM Support**: Groq (LLaMA3), Gemini, Qwen2.5-VL, and local models
- **Semantic Candidate Retrieval**: Uses SentenceTransformers for fast category matching
- **Confidence Scoring**: Calibrated confidence with review thresholds
- **Alternative Category Suggestions**: Top-3 alternative categories with scores

### Advanced Analytics
- **Vertical Mismatch Detection**: Domain-aware penalties for cross-category errors
- **Indoor/Outdoor Detection**: Automatic product environment classification
- **Head-Noun Weighting**: Linguistic-aware term weighting for better accuracy
- **Accessory Penalty**: Smart detection of product vs. accessory classification

### Data Processing
- **Batch Processing**: Handle 10,000+ products with Celery background workers
- **Resumable Classification**: Resume failed jobs without restarting
- **Hash-Based Idempotency**: Prevent duplicate classifications
- **Graceful Fallbacks**: Automatic fallback on API rate limits

### Image Analysis
- **CLIP Embeddings**: Visual similarity matching
- **Multi-Modal Classification**: Combine text and image signals
- **Image Validation**: Handle missing/broken images gracefully

### Web Interface
- **Modern Dashboard**: React frontend with visualizations
- **Product Review Queue**: Human-in-the-loop approval system
- **Real-Time Metrics**: Live classification statistics
- **Responsive Design**: Mobile-friendly interface

### API & Integration
- **REST API**: Django REST Framework endpoints
- **Batch Import/Export**: Excel/CSV support
- **Multiple Database Support**: SQLite, PostgreSQL, MariaDB, SQL Server

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.0 + Django REST Framework |
| **Frontend** | React 18 |
| **Classification** | SentenceTransformers + CLIP + LLM APIs |
| **Task Queue** | Celery + Redis |
| **Database** | PostgreSQL (default) + SQLite (dev) |
| **Deployment** | Docker + Docker Compose |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis
- PostgreSQL (or SQLite for development)

### Installation

```bash
# Clone the repository
git clone https://github.com/niyas-adam/shopify-taxonomy-super-classifier.git
cd shopify-taxonomy-super-classifier

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Run migrations
python manage.py migrate

# Import taxonomy data
python manage.py import_taxonomy

# Start the development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A config worker -l info
```

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API: http://localhost:8000/api/
```

## Configuration

### Environment Variables

```bash
# LLM API Keys
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Classification Settings
MIN_CONFIDENCE_THRESHOLD=0.3
REVIEW_THRESHOLD=0.7
MAX_ALTERNATIVES=3
```

## Classification Algorithm

### Multi-Signal Scoring

1. **Lexical Similarity** (TF-IDF): Fast keyword matching
2. **Semantic Similarity** (SentenceTransformers): Contextual understanding
3. **Image Similarity** (CLIP): Visual matching
4. **Product Type Hints**: Category-level signals
5. **Vertical Constraints**: Domain-aware penalties

### Decision Rules

- **Score > 0.7**: Auto-classified
- **Score 0.3 - 0.7**: Low confidence (flagged for review)
- **Score < 0.3**: No match (requires manual classification)

## API Endpoints

### Classification
- `POST /api/classify/` - Classify a single product
- `POST /api/classify/batch/` - Batch classification
- `GET /api/classifications/` - List classifications
- `POST /api/classifications/{id}/approve/` - Approve classification
- `POST /api/classifications/{id}/reject/` - Reject classification

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `POST /api/products/import/` - Import from Excel/CSV
- `GET /api/products/export/` - Export classified products

### Taxonomy
- `GET /api/taxonomy/` - Get taxonomy tree
- `GET /api/taxonomy/categories/` - List categories
- `GET /api/taxonomy/attributes/` - List attributes

### Analytics
- `GET /api/stats/` - Classification statistics
- `GET /api/stats/confidence/` - Confidence distribution
- `GET /api/stats/categories/` - Category distribution

## Project Structure

```
shopify-taxonomy-super-classifier/
├── config/                 # Django project settings
├── classification/         # Classification engine
│   ├── services/           # Core classification logic
│   │   ├── hybrid_classifier.py
│   │   ├── semantic_retriever.py
│   │   ├── image_analyzer.py
│   │   ├── confidence_engine.py
│   │   └── llm_classifier.py
│   ├── models.py           # Classification models
│   └── api.py              # REST API
├── frontend/               # React frontend
│   └── src/
├── docker-compose.yml      # Docker configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Acknowledgments

This project combines the best features from:
- abhishekkv660/shopify-taxonomy-classifier
- alan-j-w/shopify-taxonomy-classifier
- Suhailsulaiman2103/shopify-product-taxonomy-classifier
- Sreehari937/shopify_taxonomy_system
- losers-start/shopify-product-classifier
- ahsanalatheef31/ClassifyAI