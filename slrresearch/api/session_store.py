
from uuid import uuid4

from slrresearch.workflows.research_question_workflow import HumanReview


# Stockage temporaire des sessions de validation humaine
sessions: dict[str, HumanReview] = {}


def create_session(review: HumanReview) -> str:
    session_id = str(uuid4())
    sessions[session_id] = review
    return session_id


def get_session(session_id: str) -> HumanReview:
    review = sessions.get(session_id)

    if review is None:
        raise ValueError("Session introuvable.")

    return review
