# SLRResearchAI

**An AI-powered Multi-Agent System for Automating Systematic Literature Reviews (SLR).**

SLRResearchAI aims to simplify and automate the main stages of a Systematic Literature Review through a modular architecture based on specialized AI agents.

The system is designed to support researchers throughout the literature review process, from defining research questions to searching scientific databases, screening papers, extracting information, and producing a structured scientific review.

---

## Project Overview

Systematic Literature Reviews require significant time and effort, especially when researchers need to formulate research questions, search multiple scientific databases, screen papers, and extract relevant information.

SLRResearchAI aims to address these challenges through specialized agents that collaborate under the supervision of a future central orchestrator.

The project follows a modular and extensible architecture, allowing each agent to be developed, tested, and improved independently.

## Architecture

The system is being developed through specialized agents with clearly defined responsibilities.

| Agent | Responsibility | Status |
|---|---|---|
| Research Question Agent | Generate, validate, and refine research questions | Implemented |
| Criteria Generation Agent | Generate inclusion and exclusion criteria | Implemented |
| Query Construction Agent | Extract research concepts and build Boolean queries | Implemented |
| Search Execution Agent | Search scientific databases using a controlled ReAct architecture | Implemented |
| Deduplication | Identify and manage duplicate paper records | Implemented |
| Screening Agent | Screen papers based on titles, abstracts, and research criteria | Implemented |
| Download Agent | Retrieve legally accessible full-text papers | Planned |
| Full-text Eligibility Agent | Evaluate papers using their full text | Planned |
| Information Extraction Agent | Extract relevant information from eligible papers | Planned |
| Writing Agent | Assist in generating the SLR document | Planned |
| Quality Agent | Evaluate the quality and consistency of the review | Planned |
| Orchestrator | Coordinate agents and manage the shared workflow state | Planned |

### Current Workflow

The currently implemented workflow covers the preparation of a systematic literature search and the initial screening of scientific papers.

### 1. Research Question Generation

- Generate three research questions using an LLM.
- Validate their structure.
- Attempt automatic repair when validation fails.
- Allow the researcher to edit, approve, or reject the questions.

### 2. Criteria Generation

- Generate inclusion and exclusion criteria from the research objective and approved questions.
- Structure the criteria for use during the screening process.

### 3. Query Construction

- Extract technologies, domain concepts, and research tasks from approved questions.
- Generate Boolean search queries based on the extracted concepts.

### 4. Scientific Search

- Execute searches using a controlled ReAct architecture.
- Select among authorized scientific search tools.
- Collect and merge paper records.
- Track actions, observations, errors, and execution status.

### 5. Deduplication

- Identify duplicate scientific paper records.
- Prepare a deduplicated collection of papers for screening.

### 6. Title and Abstract Screening

- Evaluate papers according to the generated screening criteria.
- Assess the available title and abstract information.
- Produce screening decisions and criterion assessments.
- Identify papers requiring human review.

The next planned stage is the retrieval of legally accessible full-text PDFs, followed by full-text eligibility assessment.

## Technologies

- **Python** – Main programming language.
- **LangChain** – LLM integration.
- **Pydantic** – Data validation and structured contracts.
- **FastAPI** – Backend API.
- **Swagger / OpenAPI** – API documentation and testing.
- **Ollama** – Local LLM execution.
- **Groq** – Alternative LLM provider.
- **httpx** – HTTP requests to external APIs.
- **Pytest** – Automated testing.

### Scientific Search Sources

The Search Execution Agent currently integrates:

- [OpenAlex](https://openalex.org/)
- [Crossref](https://www.crossref.org/)
- [Semantic Scholar](https://www.semanticscholar.org/)

## Project Structure

```text
SLRResearchAI_Project/
│
├── slrresearch/
│   ├── agents/
│   │   ├── research_question_agent.py
│   │   ├── technology_extraction_agent.py
│   │   ├── search_execution_agent.py
│   │   ├── criteria_generation_agent.py
│   │   ├── screening_agent.py
│   │   └── llm_screening_agent.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   └── session_store.py
│   │
│   ├── core/
│   │   └── react/
│   │       ├── contracts.py
│   │       ├── policies.py
│   │       ├── runtime.py
│   │       └── engine.py
│   │
│   ├── prompts/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── validators/
│   └── workflows/
│
├── tests/
├── frontend/
├── pytest.ini
├── requirements.txt
└── README.md
```

*The project structure may evolve as development progresses.*

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/farahabdelhedi/SLRResearchAI_project.git
cd SLRResearchAI_project
```

### 2. Create a virtual environment

```bash
py -3.10 -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the LLM provider

The project supports local LLM execution through Ollama and can also be configured to use Groq.

For local execution:

- Install and start Ollama.
- Download the model configured in the project.
- Check the LLM configuration in `slrresearch/config.py`.

If using Groq, configure the required API credentials in your local environment.

## Running the Application

Start the FastAPI application from the project root:

```bash
uvicorn slrresearch.api.main:app --reload
```

Open the Swagger documentation:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Swagger allows you to interact with and test the available API endpoints.

## Running Tests

Run the automated test suite from the project root:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_example.py -v
```

## Development Philosophy

SLRResearchAI follows several architectural principles:

- **Modularity:** Each agent has a specialized responsibility.
- **Independent testing:** Agents can be tested separately.
- **Structured communication:** Pydantic models define clear input and output contracts.
- **Controlled execution:** The ReAct engine uses an authorized tool registry.
- **Human-in-the-loop:** Researchers retain control over research question approval and can review screening decisions.
- **Extensibility:** The architecture is designed to support additional agents and future orchestration.

A shared workflow State and a central Orchestrator are planned to coordinate the agents.

Agents will not communicate directly with one another. Coordination will eventually be handled centrally by the Orchestrator.

## Roadmap

- [x] Research Question Agent
- [x] Research Question validation and human approval workflow
- [x] Criteria Generation Agent
- [x] Technology and domain concept extraction
- [x] Boolean Query Construction
- [x] ReAct-based Search Execution Agent
- [x] Integration with OpenAlex, Crossref, and Semantic Scholar
- [x] Deduplication
- [x] Screening Agent
- [x] Screening criteria assessment
- [ ] Download Agent with legal Open Access retrieval
- [ ] Full-text Eligibility Agent
- [ ] Paper Information Extraction Agent
- [ ] Writing Agent
- [ ] Quality Agent
- [ ] Central Orchestrator and shared State
- [ ] Full multi-agent integration
- [ ] Web user interface

## Project Goal

The long-term goal is to develop an intelligent, modular, and extensible multi-agent system capable of assisting researchers in conducting complete and reproducible Systematic Literature Reviews.

---

**Project Status:** Under active development 🚀