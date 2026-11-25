
import pytest

from slrresearch.schemas.project import Project
from slrresearch.repositories.project_repository import (
    ProjectRepository,
    ProjectNotFoundError,
)


def test_create_and_get_project(tmp_path):
    repository = ProjectRepository(tmp_path)

    project = Project(
        topic="AI in Healthcare",
        objective="Study AI applications in healthcare"
    )

    repository.create(project)

    retrieved = repository.get(project.project_id)

    assert retrieved.project_id == project.project_id
    assert retrieved.topic == project.topic
    assert retrieved.objective == project.objective


def test_list_all_projects(tmp_path):
    repository = ProjectRepository(tmp_path)

    project1 = Project(topic="Topic 1", objective="Objective 1")
    project2 = Project(topic="Topic 2", objective="Objective 2")

    repository.create(project1)
    repository.create(project2)

    projects = repository.list_all()

    assert len(projects) == 2


def test_update_project(tmp_path):
    repository = ProjectRepository(tmp_path)

    project = Project(
        topic="AI",
        objective="Study AI"
    )
    repository.create(project)

    project.topic = "Artificial Intelligence"
    repository.update(project)

    retrieved = repository.get(project.project_id)

    assert retrieved.topic == "Artificial Intelligence"


def test_get_nonexistent_project(tmp_path):
    repository = ProjectRepository(tmp_path)

    with pytest.raises(ProjectNotFoundError):
        repository.get("unknown-project")


def test_create_duplicate_project(tmp_path):
    repository = ProjectRepository(tmp_path)

    project = Project(
        topic="AI",
        objective="Study AI"
    )

    repository.create(project)

    with pytest.raises(FileExistsError):
        repository.create(project)
