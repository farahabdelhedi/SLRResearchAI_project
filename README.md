# SLRResearchAI

**An AI-powered Multi-Agent System for Automating Systematic Literature Reviews (SLR).**

SLRResearchAI aims to simplify and automate the main stages of a Systematic Literature Review through a modular architecture based on specialized AI agents.

The system is designed to support researchers throughout the literature review process, from defining research questions to extracting information and producing a structured scientific review.

---

## Project Overview

Systematic Literature Reviews require significant time and effort, especially when researchers need to formulate research questions, search multiple scientific databases, screen papers, and extract relevant information.

SLRResearchAI aims to address these challenges through specialized agents that collaborate under the supervision of a future central orchestrator.

The project follows a modular and extensible architecture, allowing each agent to be developed, tested, and improved independently.

## Architecture

The planned system consists of the following specialized agents:

| Agent | Responsibility | Status |
|---|---|---|
| Research Question Agent | Generate, validate, and refine research questions | Implemented |
| Search Agent | Search scientific databases and collect relevant papers | Implemented |
| Download Agent | Retrieve scientific papers and PDFs | Planned |
| Screening Agent | Screen papers according to inclusion and exclusion criteria | Planned |
| Extraction Agent | Extract relevant information from selected papers | Planned |
| Writing Agent | Assist in generating the SLR document | Planned |
| Quality Agent | Evaluate the quality and consistency of the review | Planned |
| Orchestrator | Coordinate agents and manage the shared workflow state | Planned |

### Current Workflow

The currently implemented workflow covers three main stages:

1. **Research Question Generation**
   - Generate three research questions using an LLM.
   - Validate their structure.
   - Attempt automatic repair when validation fails.
   - Allow the researcher to edit, approve, or reject the questions.

2. **Query Construction**
   - Extract technologies, domain concepts, and research tasks from approved questions.
   - Generate Boolean search queries.

3. **Scientific Search**
   - Execute searches using a controlled ReAct architecture.
   - Select among authorized scientific search tools.
   - Collect and merge paper records.
   - Track actions, observations, errors, and execution status.

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

The Search Agent currently integrates:

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
│   │   └── search_execution_agent.py
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
├── .env
├── pytest.ini
└── README.md
```

*The structure may evolve as development progresses.*

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/farahabdelhedi/SLRResearchAI_project.git
cd SLRResearchAI-Project
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
- **Human-in-the-loop:** Researchers retain control over research question approval.
- **Extensibility:** The architecture is designed to support additional agents and future orchestration.

A shared workflow State and a central Orchestrator are planned to coordinate the agents. Agents will not communicate directly with one another; coordination will be handled centrally.

## Roadmap

- [x] Research Question Agent
- [x] Research Question validation and human approval workflow
- [x] Technology and domain concept extraction
- [x] Boolean Query Construction
- [x] ReAct-based Search Agent
- [x] Integration with OpenAlex, Crossref, and Semantic Scholar
- [ ] Download Agent
- [ ] Screening Agent
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