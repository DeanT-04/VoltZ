# Testing Guide

## Overview

VoltForge uses a comprehensive testing strategy with multiple levels of testing to ensure reliability and maintainability.

## Testing Strategy

### Test Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Few, high-level integration tests
    ├─────────────────┤
    │ Integration     │  ← Service interaction tests
    │     Tests       │
    ├─────────────────┤
    │   Unit Tests    │  ← Many, fast, isolated tests
    └─────────────────┘
```

### Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test service interactions
3. **API Tests**: Test HTTP endpoints and contracts
4. **Performance Tests**: Test response times and throughput
5. **End-to-End Tests**: Test complete user workflows

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest backend/tests/test_vector_db.py

# Run specific test class
pytest backend/tests/test_vector_db.py::TestVectorDBService

# Run specific test method
pytest backend/tests/test_vector_db.py::TestVectorDBService::test_add_documents
```

### Test Coverage
```bash
# Run tests with coverage
pytest --cov=backend/src

# Generate HTML coverage report
pytest --cov=backend/src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Testing
```bash
# Run performance tests only
pytest -m performance

# Run with timing information
pytest --durations=10
```

## Test Structure

### Directory Structure
```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_models.py           # Model validation tests
├── test_validators.py       # Input validation tests
├── test_api_contracts.py    # API endpoint tests
├── test_embeddings.py       # Embedding service tests
├── test_vector_db.py        # Vector database tests
├── test_datasheet_ingestion.py  # Ingestion service tests
├── test_planner.py          # Planning service tests
└── test_vector_db_integration.py  # Integration tests
```

### Test Naming Convention
```python
# Test files: test_*.py
# Test classes: Test*
# Test methods: test_*

class TestVectorDBService:
    def test_add_documents_success(self):
        """Test successful document addition."""
        pass
    
    def test_add_documents_invalid_input(self):
        """Test document addition with invalid input."""
        pass
```

## Writing Tests

### Unit Test Example
```python
import pytest
from backend.src.services.embeddings import EmbeddingService

class TestEmbeddingService:
    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance for testing."""
        return EmbeddingService()
    
    def test_generate_embeddings_single_text(self, embedding_service):
        """Test embedding generation for single text."""
        # Arrange
        text = "ESP32 microcontroller with WiFi"
        
        # Act
        embeddings = embedding_service.generate_embeddings([text])
        
        # Assert
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 384  # Model dimension
        assert all(isinstance(x, float) for x in embeddings[0])
    
    def test_generate_embeddings_batch(self, embedding_service):
        """Test batch embedding generation."""
        # Arrange
        texts = [
            "ESP32 microcontroller",
            "Temperature sensor",
            "Voltage regulator"
        ]
        
        # Act
        embeddings = embedding_service.generate_embeddings(texts)
        
        # Assert
        assert len(embeddings) == len(texts)
        assert all(len(emb) == 384 for emb in embeddings)
    
    def test_generate_embeddings_empty_input(self, embedding_service):
        """Test embedding generation with empty input."""
        # Act & Assert
        with pytest.raises(ValueError, match="No texts provided"):
            embedding_service.generate_embeddings([])
```

### Integration Test Example
```python
import pytest
import tempfile
import shutil
from backend.src.services.vector_db import VectorDBService
from backend.src.services.embeddings import EmbeddingService

class TestVectorDBIntegration:
    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary directory for test database."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # Handle Windows file locking issues
            pass
    
    @pytest.fixture
    def vector_db(self, temp_db_dir):
        """Create vector database instance."""
        return VectorDBService(persist_directory=temp_db_dir)
    
    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance."""
        return EmbeddingService()
    
    def test_end_to_end_workflow(self, vector_db, embedding_service):
        """Test complete workflow from text to search."""
        # Arrange
        documents = [
            "ESP32 microcontroller with WiFi and Bluetooth",
            "Arduino Uno development board",
            "Raspberry Pi single board computer"
        ]
        metadata = [
            {"mpn": "ESP32-WROOM-32", "category": "microcontroller"},
            {"mpn": "ARDUINO-UNO-R3", "category": "development_board"},
            {"mpn": "RPI4-MODEL-B", "category": "single_board_computer"}
        ]
        
        # Act - Add documents
        vector_db.add_document_chunks(documents, metadata)
        
        # Act - Search
        results = vector_db.search_similar("WiFi microcontroller", limit=2)
        
        # Assert
        assert len(results) == 2
        assert results[0]["metadata"]["mpn"] == "ESP32-WROOM-32"
        assert results[0]["similarity_score"] > 0.5
```

### API Test Example
```python
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

class TestProjectsAPI:
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_create_project_success(self, client):
        """Test successful project creation."""
        # Arrange
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "requirements": {
                "voltage": "5V",
                "power": "low"
            }
        }
        
        # Act
        response = client.post("/api/v1/projects/", json=project_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"
        assert "id" in data
        assert data["status"] == "active"
    
    def test_create_project_invalid_data(self, client):
        """Test project creation with invalid data."""
        # Arrange
        invalid_data = {
            "name": "",  # Invalid: empty name
            "description": "Test"
        }
        
        # Act
        response = client.post("/api/v1/projects/", json=invalid_data)
        
        # Assert
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"][0]["type"]
```

## Test Fixtures

### Common Fixtures
```python
# conftest.py
import pytest
import tempfile
import shutil
from backend.src.services.vector_db import VectorDBService
from backend.src.services.embeddings import EmbeddingService

@pytest.fixture(scope="session")
def embedding_service():
    """Session-scoped embedding service."""
    return EmbeddingService()

@pytest.fixture
def temp_directory():
    """Create temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        pass  # Handle Windows file locking

@pytest.fixture
def sample_components():
    """Sample component data for testing."""
    return [
        {
            "mpn": "ESP32-WROOM-32",
            "manufacturer": "Espressif",
            "description": "WiFi & Bluetooth microcontroller",
            "category": "microcontroller"
        },
        {
            "mpn": "ARDUINO-UNO-R3",
            "manufacturer": "Arduino",
            "description": "Development board based on ATmega328P",
            "category": "development_board"
        }
    ]
```

## Performance Testing

### Response Time Tests
```python
import time
import pytest

class TestPerformance:
    @pytest.mark.performance
    def test_search_response_time(self, vector_db):
        """Test search response time requirement."""
        # Arrange
        query = "ESP32 microcontroller"
        
        # Act
        start_time = time.time()
        results = vector_db.search_similar(query, limit=10)
        end_time = time.time()
        
        # Assert
        response_time_ms = (end_time - start_time) * 1000
        assert response_time_ms < 100, f"Search took {response_time_ms:.2f}ms, expected <100ms"
    
    @pytest.mark.performance
    def test_embedding_generation_performance(self, embedding_service):
        """Test embedding generation performance."""
        # Arrange
        texts = ["Test text"] * 10
        
        # Act
        start_time = time.time()
        embeddings = embedding_service.generate_embeddings(texts)
        end_time = time.time()
        
        # Assert
        elapsed_ms = (end_time - start_time) * 1000
        assert elapsed_ms < 1000, f"Embedding generation took {elapsed_ms:.2f}ms"
```

### Load Testing
```python
import concurrent.futures
import pytest

class TestLoadPerformance:
    @pytest.mark.performance
    def test_concurrent_searches(self, vector_db):
        """Test concurrent search performance."""
        def search_task():
            return vector_db.search_similar("microcontroller", limit=5)
        
        # Execute concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(search_task) for _ in range(20)]
            results = [future.result() for future in futures]
        
        # Assert all searches completed successfully
        assert len(results) == 20
        assert all(len(result) <= 5 for result in results)
```

## Mocking and Test Doubles

### Mocking External Services
```python
import pytest
from unittest.mock import Mock, patch
from backend.src.services.planner import PlannerService

class TestPlannerService:
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"components": []}'
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client
    
    @patch('backend.src.services.planner.OpenAI')
    def test_generate_plan_with_mock(self, mock_openai_class, mock_openai_client):
        """Test plan generation with mocked OpenAI."""
        # Arrange
        mock_openai_class.return_value = mock_openai_client
        planner = PlannerService()
        requirements = {"voltage": "5V", "power": "low"}
        
        # Act
        plan = planner.generate_project_plan(requirements)
        
        # Assert
        assert plan is not None
        mock_openai_client.chat.completions.create.assert_called_once()
```

## Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    performance: marks tests as performance tests
    integration: marks tests as integration tests
    slow: marks tests as slow running
```

### Test Environment Variables
```python
# conftest.py
import os
import pytest

@pytest.fixture(autouse=True)
def test_environment():
    """Set up test environment variables."""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "ERROR"
    os.environ["CHROMA_PERSIST_DIRECTORY"] = "/tmp/test_chroma"
    yield
    # Cleanup if needed
```

## Continuous Integration

### GitHub Actions Test Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12, 3.13]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest --cov=backend/src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Data Management

### Test Data Files
```python
# tests/data/sample_datasheets.py
SAMPLE_DATASHEET_TEXT = """
ESP32-WROOM-32 Datasheet

Overview:
The ESP32-WROOM-32 is a powerful, generic WiFi-BT-BLE MCU module.

Specifications:
- CPU: Xtensa dual-core 32-bit LX6 microprocessor
- Operating voltage: 3.0V to 3.6V
- Operating current: 80mA (average)
"""

SAMPLE_COMPONENTS = [
    {
        "mpn": "ESP32-WROOM-32",
        "manufacturer": "Espressif",
        "category": "microcontroller",
        "description": "WiFi & Bluetooth microcontroller module"
    }
]
```

## Best Practices

### Test Organization
1. **One test class per service/module**
2. **Descriptive test names**
3. **Arrange-Act-Assert pattern**
4. **Independent tests** (no test dependencies)
5. **Clean up resources** in fixtures

### Test Data
1. **Use fixtures for reusable data**
2. **Keep test data minimal**
3. **Use factories for complex objects**
4. **Avoid hardcoded values**

### Performance
1. **Use session-scoped fixtures** for expensive operations
2. **Mock external dependencies**
3. **Parallel test execution** where possible
4. **Profile slow tests**

### Maintenance
1. **Regular test review and cleanup**
2. **Update tests with code changes**
3. **Monitor test coverage trends**
4. **Remove obsolete tests**