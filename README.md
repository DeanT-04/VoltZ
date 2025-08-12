# VoltForge

[![CI/CD Pipeline](https://github.com/voltforge/voltforge/actions/workflows/ci.yml/badge.svg)](https://github.com/voltforge/voltforge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A lightweight tool that transforms user prompts into validated, downloadable KiCad schematic projects. VoltForge bridges the gap between circuit design ideas and practical implementation by leveraging AI to generate professional-grade schematics with proper component selection and validation.

## 🚀 Features

- **AI-Powered Circuit Generation**: Transform natural language descriptions into complete circuit schematics
- **Component Intelligence**: Automatic component selection with real-world part numbers and specifications
- **Validation & Simulation**: Built-in circuit validation and SPICE simulation capabilities
- **KiCad Integration**: Direct export to KiCad project files for professional PCB design
- **Vector-Based Search**: Intelligent component matching using semantic search
- **MCP Integration**: Model Context Protocol support for enhanced AI interactions

## 🏗️ Architecture

VoltForge follows a modular architecture designed for scalability and maintainability:

```
├── backend/          # FastAPI Python backend
├── frontend/         # Static web interface
├── infra/           # Infrastructure configurations
├── docs/            # Documentation
└── scripts/         # Development and deployment scripts
```

### Core Technologies

- **Backend**: FastAPI with Python 3.11+
- **Circuit Generation**: SKiDL for schematic synthesis
- **Component Database**: ChromaDB with vector embeddings
- **Simulation**: ngspice for circuit validation
- **Task Queue**: Redis with RQ for background processing
- **Containerization**: Docker with multi-service orchestration

## 🛠️ Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/voltforge/voltforge.git
   cd voltforge
   ```

2. **Run the setup script**:
   
   **Linux/macOS**:
   ```bash
   chmod +x scripts/dev-start.sh
   ./scripts/dev-start.sh
   ```
   
   **Windows**:
   ```cmd
   scripts\dev-start.bat
   ```

3. **Start the development environment**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Start Redis**:
   ```bash
   docker run -d --name voltforge-redis -p 6379:6379 redis:7-alpine
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

## 📖 Usage

### Basic Circuit Generation

1. **Submit a prompt** describing your circuit:
   ```
   "Create a simple LED blinker circuit using a 555 timer"
   ```

2. **Review the generated schematic** with automatic component selection

3. **Validate the design** using built-in simulation tools

4. **Download the KiCad project** for PCB design

### API Usage

The REST API provides programmatic access to all features:

```python
import httpx

# Generate a circuit
response = httpx.post("http://localhost:8000/api/generate", json={
    "prompt": "Design a voltage divider for 5V to 3.3V conversion",
    "validate": True
})

circuit = response.json()
```

### MCP Integration

VoltForge supports Model Context Protocol for enhanced AI interactions:

```json
{
  "mcpServers": {
    "voltforge": {
      "command": "uvx",
      "args": ["voltforge-mcp-server@latest"],
      "env": {
        "VOLTFORGE_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Unit tests
pytest backend/tests/

# Integration tests
pytest backend/tests/integration/

# MCP tests
pytest backend/tests/mcp/

# Performance tests
locust -f backend/tests/performance/locustfile.py
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Core settings
ENVIRONMENT=development
DEBUG=true
REDIS_URL=redis://localhost:6379/0

# API configuration
API_HOST=0.0.0.0
API_PORT=8000

# External APIs (optional)
DIGIKEY_API_KEY=your_key_here
OCTOPART_API_KEY=your_key_here

# Vector database
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Circuit simulation
NGSPICE_EXECUTABLE=ngspice
```

### Component Database

VoltForge uses a vector database for intelligent component matching:

- **Embeddings**: Sentence transformers for semantic search
- **Storage**: ChromaDB for efficient vector operations
- **Caching**: Redis for component metadata caching

## 🚀 Deployment

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with orchestration
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configs

- **Development**: Full debugging, hot reload
- **Testing**: Isolated services, test databases
- **Production**: Optimized performance, security hardening

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **Testing**: Maintain >90% code coverage
- **Documentation**: Update docs for new features
- **Commits**: Use conventional commit messages

## 📊 Performance

VoltForge is designed for efficiency:

- **Response Time**: <2s for simple circuits, <10s for complex designs
- **Throughput**: 100+ concurrent requests with Redis queue
- **Memory**: <512MB base footprint
- **Storage**: Vector database scales with component library

## 🔒 Security

Security is a priority:

- **Input Validation**: Comprehensive request sanitization
- **Rate Limiting**: API throttling and abuse prevention
- **Dependencies**: Regular security scanning with Bandit
- **Containers**: Minimal attack surface with Alpine Linux

## 📚 Documentation

### Core Documentation
- **[🏗️ Architecture Guide](./docs/architecture.md)** - System design, components, and technical decisions
- **[📖 API Reference](./docs/api.md)** - Complete API documentation with examples
- **[💻 Development Guide](./docs/development.md)** - Setup, workflow, and development guidelines
- **[🚀 Deployment Guide](./docs/deployment.md)** - Production deployment instructions
- **[🧪 Testing Guide](./docs/testing.md)** - Testing strategy, guidelines, and best practices
- **[🤝 Contributing Guide](./docs/contributing.md)** - How to contribute to the project

### Additional Resources
- **[📋 Changelog](./CHANGELOG.md)** - Version history and changes
- **[👥 Contributors](./CONTRIBUTORS.md)** - Project contributors and acknowledgments
- **API Reference**: Interactive docs available at `/docs` endpoint

## 🐛 Troubleshooting

### Common Issues

**Redis Connection Failed**:
```bash
# Check Redis status
docker ps | grep redis
# Restart if needed
docker restart voltforge-redis
```

**ngspice Not Found**:
```bash
# Ubuntu/Debian
sudo apt-get install ngspice

# macOS
brew install ngspice

# Windows
# Download from http://ngspice.sourceforge.net/
```

**Vector Database Corruption**:
```bash
# Reset vector database
rm -rf data/vector_db
# Restart application to rebuild
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SKiDL**: Python-based schematic design language
- **ngspice**: Open-source circuit simulator
- **ChromaDB**: Vector database for embeddings
- **FastAPI**: Modern Python web framework
- **KiCad**: Open-source PCB design suite

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/voltforge/voltforge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/voltforge/voltforge/discussions)
- **Documentation**: [Project Wiki](https://github.com/voltforge/voltforge/wiki)

---

**VoltForge** - Transforming ideas into circuits, one prompt at a time. ⚡