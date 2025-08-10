# Requirements Document

## Introduction

VoltForge is a lightweight, open-source tool that transforms user prompts into validated, downloadable KiCad schematic projects. The system prioritizes speed, deterministic generation, and correctness over AI-powered generation. It uses a pipeline approach: prompt analysis → component research → user selection → schematic generation → validation → export. The MVP focuses on delivering a working prototype that feels instant to users while maintaining ultra-lightweight architecture and full open-source compatibility.

## Requirements

### Requirement 1

**User Story:** As an electronics engineer, I want to input a natural language description of a circuit and receive a working KiCad schematic, so that I can quickly prototype electronic designs without manual component research and schematic drawing.

#### Acceptance Criteria

1. WHEN a user submits a prompt THEN the system SHALL parse the prompt and extract component roles (microcontroller, sensor, power) and constraints (voltage, size) within 2 seconds
2. WHEN the system processes a prompt THEN it SHALL return a shortlist of 1-3 component candidates per role with datasheet references
3. WHEN a user selects components from the shortlist THEN the system SHALL generate a valid KiCad schematic file (.kicad_sch) that opens without manual edits
4. WHEN the schematic is generated THEN the system SHALL provide an SVG preview within 2 seconds for cache hits or 5 seconds worst-case
5. WHEN the user requests export THEN the system SHALL provide a downloadable zip containing KiCad project files and BOM

### Requirement 2

**User Story:** As a developer, I want the application to load instantly and feel responsive, so that I can iterate quickly on circuit designs without waiting for heavy interfaces.

#### Acceptance Criteria

1. WHEN a user loads the application THEN the cold page load (HTML+CSS+JS) SHALL complete within 1 second on a modern laptop
2. WHEN the UI bundle is served THEN it SHALL be ≤ 50 KB gzipped (target ≤ 20 KB)
3. WHEN the user interacts with the interface THEN API responses for simple lookups SHALL have 95th percentile latency ≤ 150ms
4. WHEN the frontend renders THEN it SHALL use vanilla JS with optional htmx and inline SVG for previews
5. WHEN the system processes requests THEN typical schematic generation end-to-end SHALL complete within 2 seconds for cache hits

### Requirement 3

**User Story:** As an open-source advocate, I want all components of the system to be fully open-source, so that I can inspect, modify, and contribute to the codebase without proprietary dependencies.

#### Acceptance Criteria

1. WHEN the system is deployed THEN all code, build processes, and models SHALL be OSS-compatible
2. WHEN the system generates schematics THEN it SHALL use deterministic generation (SKiDL/templates) without heavy LLMs
3. WHEN the system performs component research THEN it SHALL use small embedding models only for RAG (sentence-transformers/all-MiniLM-L6-v2)
4. WHEN external APIs are used THEN the system SHALL respect API Terms of Service and use cached copies of datasheets
5. WHEN the system stores data THEN it SHALL use local vector databases (Chroma or FAISS) without cloud dependencies

### Requirement 4

**User Story:** As a circuit designer, I want the generated schematics to be electrically correct and validated, so that I can trust the output for actual circuit implementation.

#### Acceptance Criteria

1. WHEN a schematic is generated THEN the system SHALL perform static checks for pin count validation and explicit VCC/GND nets
2. WHEN the system validates circuits THEN it SHALL use ngspice for basic sanity checks including pin continuity and basic DC results
3. WHEN validation finds issues THEN the system SHALL return warnings and errors to the user before export
4. WHEN components are selected THEN the system SHALL use datasheet-parsed facts and templates to avoid hallucination
5. WHEN the system generates netlists THEN they SHALL pass pin count checks and have explicit power connections

### Requirement 5

**User Story:** As a developer maintaining the system, I want comprehensive test coverage and automated validation, so that I can confidently deploy changes without breaking core functionality.

#### Acceptance Criteria

1. WHEN code is committed THEN unit test coverage SHALL be ≥ 85% for core backend modules
2. WHEN pull requests are created THEN Playwright MCP smoke tests SHALL pass on every PR
3. WHEN the system runs tests THEN it SHALL include 5 Most Critical Paths (MCPs) covering happy path, fallback, warnings, edit loop, and export validation
4. WHEN tests execute THEN they SHALL use deterministic mock responses to eliminate flakiness
5. WHEN the CI pipeline runs THEN it SHALL enforce linting, coverage gates, and API contract validation

### Requirement 6

**User Story:** As a system administrator, I want the application to be secure and handle user inputs safely, so that the system can be deployed without security vulnerabilities.

#### Acceptance Criteria

1. WHEN the system handles user inputs THEN it SHALL sanitize and escape all inputs to prevent injection attacks
2. WHEN SVG content is generated THEN it SHALL be sanitized server-side to strip scripts and malicious content
3. WHEN the system stores secrets THEN it SHALL use environment variables and never hard-code credentials in the repository
4. WHEN external APIs are called THEN the system SHALL implement rate limiting to prevent abuse
5. WHEN the system processes files THEN it SHALL validate file types and sizes to prevent malicious uploads

### Requirement 7

**User Story:** As a user researching components, I want the system to find relevant parts from datasheets and external APIs, so that I can discover appropriate components for my circuit requirements.

#### Acceptance Criteria

1. WHEN the system searches for components THEN it SHALL query local vector database for relevant datasheet chunks first
2. WHEN local search yields no results THEN the system SHALL query external component APIs (Digikey/Octopart) if configured
3. WHEN no candidates are found THEN the system SHALL return "no candidate found" message rather than hallucinating components
4. WHEN datasheets are processed THEN the system SHALL parse text via pdfminer.six or Apache Tika and chunk into 1k-2k character segments
5. WHEN new datasheets are ingested THEN the system SHALL compute embeddings and store vectors with provenance and page references

### Requirement 8

**User Story:** As a user iterating on designs, I want to modify component selections and see updated schematics, so that I can refine my circuit design through an interactive process.

#### Acceptance Criteria

1. WHEN a user changes component selections THEN the system SHALL re-run the coder and sanity checker automatically
2. WHEN the schematic is updated THEN the system SHALL provide a new SVG preview reflecting the changes
3. WHEN validation warnings are present THEN the user SHALL be able to accept warnings or make corrections
4. WHEN the user makes multiple edits THEN each iteration SHALL maintain the same performance requirements (≤ 2-5 seconds)
5. WHEN the edit loop completes THEN the updated schematic SHALL maintain electrical correctness and validation