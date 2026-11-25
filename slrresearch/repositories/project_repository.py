
import json
from pathlib import Path

from slrresearch.schemas.project import Project


class ProjectNotFoundError(FileNotFoundError):
    """Levée lorsqu'un projet demandé n'existe pas."""


class ProjectRepository:
    """
    Gère la persistance des projets SLR au format JSON.
    """

    def __init__(self, storage_dir: Path | str | None = None):
        if storage_dir is None:
            project_root = Path(__file__).resolve().parents[2]
            storage_dir = project_root / "data" / "projects"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_path(self, project_id: str) -> Path:
        # Empêche un identifiant de sortir du dossier de stockage.
        if not project_id or Path(project_id).name != project_id:
            raise ValueError("Identifiant de projet invalide.")

        return self.storage_dir / f"{project_id}.json"

    def create(self, project: Project) -> Project:
        path = self._get_project_path(project.project_id)

        if path.exists():
            raise FileExistsError(
                f"Le projet {project.project_id} existe déjà."
            )

        self._write_project(path, project)
        return project

    def get(self, project_id: str) -> Project:
        path = self._get_project_path(project_id)

        if not path.exists():
            raise ProjectNotFoundError(
                f"Projet introuvable : {project_id}"
            )

        data = json.loads(path.read_text(encoding="utf-8"))
        return Project.model_validate(data)

    def list_all(self) -> list[Project]:
        projects = []

        for path in sorted(self.storage_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            projects.append(Project.model_validate(data))

        return projects

    def update(self, project: Project) -> Project:
        path = self._get_project_path(project.project_id)

        if not path.exists():
            raise ProjectNotFoundError(
                f"Projet introuvable : {project.project_id}"
            )

        self._write_project(path, project)
        return project

    @staticmethod
    def _write_project(path: Path, project: Project) -> None:
        data = project.model_dump(mode="json")
        temporary_path = path.with_suffix(".tmp")

        temporary_path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

        temporary_path.replace(path)
