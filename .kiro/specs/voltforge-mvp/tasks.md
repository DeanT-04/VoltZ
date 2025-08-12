# Implementation Plan

- [x] 1. Set up project structure and core configuration





  - Create directory structure following PRD specifications (/backend, /frontend, /infra, /docs, /scripts)
  - Set up pyproject.toml with pinned dependencies (FastAPI, SKiDL, Chroma, ngspice-python)
  - Create docker-compose.yml for local development with Redis
  - Configure CI/CD pipeline with GitHub Actions for linting, testing, and MCP validation
  - _Requirements: 3.1, 3.4, 5.1, 5.4_

- [x] 2. Implement core data models and validation





  - Create Pydantic models for ParsedPrompt, Component, SchematicResult, and Project
  - Implement validation functions for electrical specifications and pin mappings
  - Write unit tests for data model validation and serialization
  - _Requirements: 4.1, 4.4, 6.1_
-

- [x] 3. Build FastAPI application foundation





  - Create FastAPI app with structured routing and middleware
  - Implement API endpoint stubs for all 5 core endpoints
  - Add request/response validation using Pydantic schemas
  - Configure CORS, rate limiting, and security headers
  - Write API contract tests to validate JSON schemas
  - _Requirements: 1.2, 5.5, 6.1, 6.4_

- [x] 4. Implement Planner service for prompt parsing










  - Create PlannerService class with regex-based role extraction (microcontroller, sensor, power)
  - Implement constraint parsing for voltage, size, and battery requirements
  - Add deterministic classification logic without LLM dependencies
  - Write unit tests for 12 example prompts with 90% extraction accuracy target
  - _Requirements: 1.1, 3.2, 4.4_

- [x] 5. Set up vector database and embedding system







  - Configure Chroma or FAISS for local vector storage
  - Implement embedding generation using sentence-transformers/all-MiniLM-L6-v2
  - Create datasheet ingestion pipeline with pdfminer.six for text extraction
  - Implement text chunking (1k-2k chars) with provenance tracking
  - Write integration tests for vector search with ≤150ms latency requirement
  - _Requirements: 3.3, 7.1, 7.4, 7.5_
-

- [ ] 6. Build Researcher service for component discovery



  - Implement ResearcherService with local vector database querying
  - Add fallback logic for external API integration (Digikey/Octopart)
  - Create component caching system with TTL configuration
  - Implement "no candidate found" handling instead of hallucination
  - Write integration tests for component search with mock external APIs
  - _Requirements: 7.1, 7.2, 7.3, 3.4_
- [ ] 7. Create SKiDL coder service for schematic generation


- [ ] 7. Create SKiDL coder service for schematic generation

  - Implement SKiDLCoderService with template-based component mapping
  - Create component templates for common parts (ESP32, sensors, power management)
  - Add SKiDL netlist generation with explicit VCC/GND net handling
  - Implement KiCad S-expression converter for .kicad_sch output
  - Write unit tests for template rendering and netlist validation
  - _Requirements: 1.3, 4.1, 4.5_

- [ ] 8. Implement sanity checker with ngspice integration
  - Create SanityChecker service for static electrical validation
  - Integrate ngspice for basic DC analysis and pin continuity checks
  - Implement pin count validation and power net verification
  - Add warning generation for missing decoupling, incompatible voltages
  - Write integration tests with sample circuits for validation accuracy
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 9. Build export service for KiCad project generation
  - Implement ExportService to create .zip packages with .kicad_sch files
  - Generate BOM (Bill of Materials) in CSV format with component details
  - Create .kicad_pcb stub files for PCB layout compatibility
  - Add file validation to ensure KiCad compatibility
  - Write unit tests for zip generation and file structure validation
  - _Requirements: 1.5, 4.5_

- [ ] 10. Create job queue system for background processing
  - Implement task queue using RQ with Redis or asyncio for MVP
  - Add job status tracking and progress reporting
  - Create background workers for schematic generation pipeline
  - Implement job cleanup and error recovery mechanisms
  - Write integration tests for job processing and status updates
  - _Requirements: 1.4, 2.3_

- [ ] 11. Build static frontend with vanilla JavaScript
  - Create index.html with semantic markup and accessibility features
  - Implement ui.js with DOM manipulation for prompt input and component selection
  - Build api.js REST client with error handling and loading states
  - Create styles.css with inline critical CSS for performance
  - Ensure bundle size ≤50KB gzipped and ≤1s cold load time
  - _Requirements: 2.1, 2.2, 2.4, 6.1_

- [ ] 12. Implement SVG preview generation and rendering
  - Add SVG schematic generation from SKiDL netlists
  - Implement server-side SVG sanitization to strip malicious content
  - Create inline SVG rendering in frontend with responsive design
  - Add component labeling and net visualization in SVG output
  - Write tests for SVG generation and sanitization security
  - _Requirements: 1.4, 6.2_

- [ ] 13. Create edit loop functionality for iterative design
  - Implement component selection updates with automatic regeneration
  - Add real-time SVG preview updates when selections change
  - Create warning acceptance/rejection workflow for validation issues
  - Maintain performance requirements (≤2-5s) during edit iterations
  - Write integration tests for edit loop state management
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 14. Set up comprehensive test infrastructure
  - Create Mock Component Provider classes for deterministic test data
  - Implement Playwright test harnesses for 5 MCPs (Most Critical Paths)
  - Set up mock servers for external API simulation (mcp-local, mcp-external, mcp-failure)
  - Configure test database with sample datasheets and components
  - Write performance tests for API latency and bundle size validation
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 15. Implement MCP-1: Happy path end-to-end flow
  - Write Playwright test for complete user journey: prompt → shortlist → select → generate → export
  - Validate status transitions and SVG content generation
  - Test KiCad zip export and file structure validation
  - Ensure test completes within performance requirements
  - _Requirements: 5.3_

- [ ] 16. Implement MCP-2: Component fallback scenario
  - Write Playwright test for local search failure → external API → success flow
  - Mock external API responses for consistent test results
  - Validate shortlist generation with ≥1 candidate requirement
  - Test UI handling of fallback scenarios
  - _Requirements: 5.3, 7.2_

- [ ] 17. Implement MCP-3: Validation warning handling
  - Write Playwright test for missing power net → warning generation → user decision
  - Test warning message display and user interaction options
  - Validate that warnings don't block export when accepted
  - Test sanity checker integration with ngspice
  - _Requirements: 5.3, 4.2, 4.3_

- [ ] 18. Implement MCP-4: Edit loop validation
  - Write Playwright test for component selection changes → regeneration → updated preview
  - Validate SVG updates contain new component symbols and connections
  - Test performance during multiple edit iterations
  - Ensure state consistency throughout edit loop
  - _Requirements: 5.3, 8.1, 8.2_

- [ ] 19. Implement MCP-5: Export and KiCad compatibility
  - Write Playwright test for export generation and file validation
  - Create KiCad S-expression schema validator for automated testing
  - Test that exported files open in KiCad without manual edits
  - Validate BOM generation and component data accuracy
  - _Requirements: 5.3, 1.5_

- [ ] 20. Add security hardening and input validation
  - Implement comprehensive input sanitization for all user inputs
  - Add rate limiting middleware for API endpoints
  - Create SVG sanitization pipeline with security testing
  - Implement file upload validation and size limits
  - Write security tests for injection attacks and malicious inputs
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 21. Optimize performance and bundle size
  - Profile and optimize API response times to meet ≤150ms requirement
  - Minimize frontend bundle size to ≤50KB gzipped target
  - Implement caching strategies for vector database queries
  - Optimize SVG generation for ≤2s preview rendering
  - Write performance regression tests for CI pipeline
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [ ] 22. Create development and deployment scripts
  - Write scripts/dev-start.sh for one-command local development setup
  - Create Docker configuration for production deployment
  - Implement database migration and seeding scripts
  - Add monitoring and logging configuration with structured JSON logs
  - Create deployment validation scripts for production readiness
  - _Requirements: 3.1, 3.4_

- [ ] 23. Integrate all components and perform system testing
  - Wire together all services in the main FastAPI application
  - Test complete system integration with real component data
  - Validate all API endpoints work together in production-like environment
  - Run full MCP test suite and ensure all tests pass
  - Perform load testing and validate performance requirements
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.3, 5.2_