from pathlib import Path
from typing import List

import rtyaml
from flask import flash
from pydantic import BaseModel


class Metadata(BaseModel):
    description: str
    maintainers: List[str]


class OpenControl(BaseModel):
    schema_version: str = "1.0.0"
    name: str
    metadata: Metadata | None
    components: List[str] = []
    certifications: List[str] = []
    standards: List[str] = []


class Project(BaseModel):
    name: str
    description: str
    maintainers: List[str] | None
    oc_file: Path | None
    config_file: Path | None
    certifications: Path | None
    standards: Path | None
    keys: Path | None
    project_dir: Path | None

    def create(self):
        self.project_dir = Path("project_data").joinpath(self.name)
        self._create_dir(dir_path=self.project_dir, parents=True)
        self._create_structure()
        self._create_open_control()

    def _create_structure(self):
        self.oc_file = self.project_dir.joinpath("opencontrol").with_suffix(".yaml")
        self.keys = self.project_dir.joinpath("keys")
        self._create_dir(dir_path=self.keys, parents=False)
        self.certifications = self.project_dir.joinpath("certifications")
        self._create_dir(dir_path=self.certifications, parents=False)
        self.standards = self.project_dir.joinpath("standards")
        self._create_dir(dir_path=self.standards, parents=False)
        self._create_templates()
        self._create_rendered()

    def _create_templates(self):
        templates = self.project_dir.joinpath("templates")
        for template_dir in ["appendices", "components", "frontmatter", "tailoring"]:
            self._create_dir(templates.joinpath(template_dir), parents=True)

    def _create_rendered(self):
        rendered = self.project_dir.joinpath("rendered")
        for rendered_dir in [
            "appendices",
            "components",
            "frontmatter",
            "tailoring",
            "docs",
        ]:
            self._create_dir(rendered.joinpath(rendered_dir), parents=True)

    @staticmethod
    def _create_dir(dir_path: Path, parents: bool):
        try:
            dir_path.mkdir(parents=parents)
        except FileExistsError:
            flash(f"Directory {dir_path} already exists", "error")
        except FileNotFoundError:
            flash(f"Parent directory for {dir_path} doesn't exist", "error")
        finally:
            pass

    def _create_open_control(self):
        meta = Metadata(
            description=self.description,
            maintainers=self.maintainers,
        )
        opencontrol = OpenControl(
            name=self.name,
            metadata=meta,
            components=[],
            certifications=[],
            standards=[],
        )
        with self.oc_file.open("w+") as oc:
            oc.write(rtyaml.dump(opencontrol.dict()))
