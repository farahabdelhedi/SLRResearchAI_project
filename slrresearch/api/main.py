
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from slrresearch.config import Settings, build_model
from slrresearch.agents.research_question_agent import ResearchQuestionAgent
from slrresearch.workflows.research_question_workflow import (
    ResearchQuestionWorkflow,
)
from slrresearch.agents.technology_extraction_agent import (
    TechnologyExtractionAgent,
)
from slrresearch.workflows.query_construction_workflow import (
    QueryConstructionWorkflow,
)
from slrresearch.agents.search_execution_agent import SearchExecutionAgent
from slrresearch.schemas.query_construction import QueryConstructionResult

from slrresearch.api.session_store import create_session, get_session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SLRResearchAI API",
    description="API de génération et validation des questions de recherche.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Initialisation du modèle et de l'agent
settings = Settings()
model = build_model(settings)

research_question_agent = ResearchQuestionAgent(
    model=model,
    provider=settings.provider,
)

# Initialisation du workflow de construction des requêtes
technology_extraction_agent = TechnologyExtractionAgent(
    model=model
)

query_construction_workflow = QueryConstructionWorkflow(
    technology_agent=technology_extraction_agent
)

# Initialisation du workflow humain
research_question_workflow = ResearchQuestionWorkflow(
    agent=research_question_agent
)
# Initialisation du Search Execution Agent
search_execution_agent = SearchExecutionAgent(model=model)

class ResearchQuestionRequest(BaseModel):
    topic: str
    objective: str
    context: str = ""

class SessionRequest(BaseModel):
    session_id: str

class EditQuestionsRequest(BaseModel):
    session_id: str
    questions_text: str
class SearchExecutionRequest(BaseModel):
    objective: str
    query_result: QueryConstructionResult
    max_steps: int = 5
    target_papers: int = 10


@app.get("/")
def home():
    return {
        "message": "Bienvenue dans l'API SLRResearchAI",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResearchQuestionAgent",
    }


@app.post("/api/research-questions/generate")
def generate_research_questions(request: ResearchQuestionRequest):
    try:
        # 1. Génération et validation automatique
        result = research_question_agent.run(
            topic=request.topic,
            objective=request.objective,
            context=request.context,
        )

        response = result.model_dump()

        # 2. Créer une session uniquement si les questions
        # ont passé la validation automatique
        if result.status in {"accepted", "repaired"}:
            review = research_question_workflow.start_review(result)
            session_id = create_session(review)

            response["session_id"] = session_id
            response["human_review_status"] = review.status
        else:
            response["session_id"] = None
            response["human_review_status"] = None

        return response

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération : {str(error)}",
        )

@app.post("/api/research-questions/approve")
def approve_research_questions(request: SessionRequest):
    try:
        # Retrouver la session
        review = get_session(request.session_id)

        # Accepter les questions sans les modifier
        research_question_workflow.approve(review)

        # Récupérer les questions approuvées
        approved_questions = (
            research_question_workflow.get_approved_questions(review)
        )

        return {
            "session_id": request.session_id,
            "status": review.status,
            "message": "Les questions ont été approuvées par l'utilisateur.",
            "questions": [
                question.model_dump()
                for question in approved_questions
            ],
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.put("/api/research-questions/edit")
def edit_research_questions(request: EditQuestionsRequest):
    try:
        review = get_session(request.session_id)

        research_question_workflow.edit_questions(
            review,
            request.questions_text,
        )

        return {
            "session_id": request.session_id,
            "status": review.status,
            "message": "Les questions ont été modifiées et validées.",
            "questions": [
                question.model_dump()
                for question in review.questions
            ],
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

class RejectQuestionsRequest(BaseModel):
    session_id: str
    reason: str = ""


@app.post("/api/research-questions/reject")
def reject_research_questions(request: RejectQuestionsRequest):
    try:
        review = get_session(request.session_id)

        research_question_workflow.reject(
            review,
            request.reason,
        )

        return {
            "session_id": request.session_id,
            "status": review.status,
            "message": "Les questions ont été rejetées par l'utilisateur.",
            "rejection_reason": review.rejection_reason,
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
@app.post("/api/query-construction/generate")
def generate_queries(request: SessionRequest):
    try:
        # 1. Récupérer la session du chercheur
        review = get_session(request.session_id)

        # 2. Vérifier que les questions ont été approuvées
        approved_questions = (
            research_question_workflow.get_approved_questions(review)
        )

        # 3. Extraire les concepts et construire les requêtes
        result = query_construction_workflow.run(
            approved_questions
        )

        # 4. Retourner le résultat
        return {
            "session_id": request.session_id,
            "status": "success",
            "technologies": result.technologies,
            "domain_concepts": result.domain_concepts,
            "research_tasks": result.research_tasks,
            "queries": result.queries,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la construction des requêtes : {str(error)}",
        )
@app.post("/api/search/execute")
def execute_search(request: SearchExecutionRequest):
    try:
        result = search_execution_agent.run(
            objective=request.objective,
            query_result=request.query_result,
            max_steps=request.max_steps,
            target_papers=request.target_papers,
        )

        return result.model_dump()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pendant l'exécution de la recherche : {str(error)}",
        )
