# Development Guide

## Prerequisites

- Python 3.13+
- Git
- Docker (optional, for containerized development)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/voltforge.git
cd voltforge
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Environment Configuration
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# API Configuration
API_HOST=localhost
API_PORT=8000
API_KEY=your-development-api-key

# Database Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# AI Services
OPENAI_API_KEY=your-openai-api-key
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Development
DEBUG=true
LOG_LEVEL=DEBUG
```

### 5. Initialize Database
```bash
python -m backend.src.main --init-db
```

## Development Workflow

### Running the Development Server
```bash
# Using the development script
./scripts/dev-start.sh  # On Windows: scripts\dev-start.bat

# Or directly with uvicorn
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend/src --cov-report=html

# Run specific test file
pytest backend/tests/test_vector_db.py

# Run with verbose output
pytest -v
```

### Code Quality

#### Linting
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
flake8 backend/src
black backend/src --check
isort backend/src --check-only
```

#### Formatting
```bash
# Format code
black backend/src
isort backend/src
```

#### Type Checking
```bash
mypy backend/src
```

## Project Structure

```
voltforge/
├── backend/
│   ├── src/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   ├── middleware/    # API middleware
│   │   └── main.py        # Application entry point
│   ├── tests/             # Test files
│   └── examples/          # Example scripts
├── docs/                  # Documentation
├── scripts/               # Development scripts
├── data/                  # Data storage
├── .github/               # GitHub workflows
└── pyproject.toml         # Project configuration
```

## Adding New Features

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Implement Feature
- Add code in appropriate modules
- Follow existing patterns and conventions
- Add comprehensive tests
- Update documentation

### 3. Testing
```bash
# Run tests for your changes
pytest backend/tests/test_your_feature.py

# Run full test suite
pytest

# Check coverage
pytest --cov=backend/src
```

### 4. Documentation
- Update API documentation if adding endpoints
- Add docstrings to new functions/classes
- Update README if needed

### 5. Submit Pull Request
- Ensure all tests pass
- Include clear description of changes
- Reference any related issues

## Database Management

### Adding New Collections
```python
# In your service file
from backend.src.services.vector_db import VectorDBService

vector_db = VectorDBService()
collection = vector_db.get_or_create_collection("new_collection")
```

### Data Migration
```bash
# Create migration script in scripts/migrations/
python scripts/migrations/001_add_new_field.py
```

## API Development

### Adding New Endpoints
1. Define models in `backend/src/models/`
2. Add endpoint in appropriate API module
3. Add validation and error handling
4. Write tests
5. Update API documentation

### Example Endpoint
```python
from fastapi import APIRouter, HTTPException
from backend.src.models.core import YourModel

router = APIRouter()

@router.post("/your-endpoint")
async def create_item(item: YourModel):
    try:
        # Your logic here
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing Guidelines

### Test Structure
```python
import pytest
from backend.src.services.your_service import YourService

class TestYourService:
    @pytest.fixture
    def service(self):
        return YourService()
    
    def test_your_method(self, service):
        # Arrange
        input_data = "test"
        
        # Act
        result = service.your_method(input_data)
        
        # Assert
        assert result is not None
```

### Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test service interactions
- **API Tests**: Test HTTP endpoints
- **Performance Tests**: Test response times and throughput

## Debugging

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Debug information")
logger.error("Error occurred", exc_info=True)
```

### Debug Mode
Set `DEBUG=true` in your `.env` file for detailed error messages.

### Profiling
```bash
# Profile API performance
python -m cProfile -o profile.stats backend/src/main.py
```

## Common Issues

### ChromaDB Permission Errors (Windows)
If you encounter file permission errors during tests:
```bash
# Run tests with cleanup disabled
pytest --no-cov backend/tests/ -k "not integration"
```

### Embedding Model Download
First run may be slow due to model download:
```python
# Pre-download models
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### Memory Issues
For large datasets, consider:
- Batch processing
- Streaming data processing
- Increasing system memory limits

## Contributing

1. Follow the existing code style
2. Write comprehensive tests
3. Update documentation
4. Use meaningful commit messages
5. Keep pull requests focused and small