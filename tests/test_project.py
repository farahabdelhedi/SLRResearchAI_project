
from slrresearch.schemas.project import Project


def test_create_project():
    project = Project(
        topic="AI in Medical Imaging",
        objective="Study the use of deep learning for disease detection",
        context="Focus on publications from 2020 to 2026"
    )

    assert project.project_id is not None
    assert project.topic == "AI in Medical Imaging"
    assert project.objective == "Study the use of deep learning for disease detection"
    assert project.context == "Focus on publications from 2020 to 2026"
    assert project.status == "created"


def test_project_json_serialization():
    project = Project(
        topic="AI in Healthcare",
        objective="Study AI applications in healthcare"
    )

    data = project.model_dump(mode="json")

    assert isinstance(data, dict)
    assert isinstance(data["created_at"], str)
    assert data["topic"] == "AI in Healthcare"


def test_each_project_has_unique_id():
    project1 = Project(
        topic="Topic 1",
        objective="Objective 1"
    )

    project2 = Project(
        topic="Topic 2",
        objective="Objective 2"
    )

    assert project1.project_id != project2.project_id
