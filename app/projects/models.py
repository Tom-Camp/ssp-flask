from pathlib import Path
from typing import List

from flask import flash
from pydantic import BaseModel


class Metadata(BaseModel):
    description: str
    maintainers: List[str]


class OpenControl(BaseModel):
    schema_version: str = "1.0.0"
    name: str
    metadata: Metadata | None
    components: List[str] | None
    certifications: List[str] = []
    standards: List[str] = []


class Project(BaseModel):
    name: str
    oc_file: Path | None
    config_file: Path | None
    keys_dir: Path | None
    project_dir: Path | None

    def create(self):
        self.project_dir = Path("project_data").joinpath(self.name)
        try:
            self.project_dir.mkdir(exist_ok=False)
            self._create_structure()
        except FileExistsError:
            flash(f"Project {self.name} already exists.", "error")
        finally:
            pass

    def _create_structure(self):
        self.project_dir.joinpath("keys").mkdir()
        self.project_dir.joinpath("certifications").mkdir()
        self.project_dir.joinpath("standards").mkdir()
        self._create_templates()
        self._create_rendered()

    def _create_templates(self):
        templates = self.project_dir.joinpath("templates")
        for template_dir in ["appendices", "components", "frontmatter", "tailoring"]:
            templates.joinpath(template_dir).mkdir(parents=True)

    def _create_rendered(self):
        rendered = self.project_dir.joinpath("rendered")
        for rendered_dir in [
            "appendices",
            "components",
            "frontmatter",
            "tailoring",
            "docs",
            "docs",
        ]:
            rendered.joinpath(rendered_dir).mkdir(parents=True)
