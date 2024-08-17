from datetime import datetime
from pathlib import Path
from typing import List

import rtyaml
from flask import flash
from pydantic import BaseModel

from app.utils.helpers import get_machine_name


class Metadata(BaseModel):
    description: str
    maintainers: List[str]


class SspDate(BaseModel):
    iso_date: str = "iso-date3"
    text: datetime | None


class SspCertifications(BaseModel):
    name: str
    abbr: str


class SystemSecurityPlan(BaseModel):
    title: str
    date: SspDate
    certifications: SspCertifications


class OpenControl(BaseModel):
    schema_version: str = "1.0.0"
    name: str
    metadata: Metadata | None
    components: List[str] = []
    certifications: List[str] = []
    standards: List[str] = []


class Project(BaseModel):
    name: str
    machine_name: str = ""
    description: str
    maintainers: List[str] | None
    oc_file: str | None
    config_file: str | None
    certifications: str | None
    standards: str | None
    keys: str | None
    project_dir: str | None

    def create(self):
        self.machine_name = get_machine_name(name=self.name)
        self.project_dir = Path("project_data").joinpath(self.machine_name).as_posix()
        self._create_dir(dir_path=self.project_dir, parents=True)
        self._create_structure()
        self._create_open_control()

    def _create_structure(self):
        project_path = Path(self.project_dir)
        self.oc_file = (
            project_path.joinpath("opencontrol").with_suffix(".yaml").as_posix()
        )
        self.keys = project_path.joinpath("keys").as_posix()
        self._create_dir(dir_path=self.keys, parents=False)
        self.certifications = (
            project_path.joinpath("keys").joinpath("certifications").as_posix()
        )
        self._create_dir(dir_path=self.certifications, parents=False)
        self.standards = project_path.joinpath("keys").joinpath("standards").as_posix()
        self._create_dir(dir_path=self.standards, parents=False)
        self._create_templates()
        self._create_rendered()
        self._write_project()

    def _create_templates(self):
        templates = Path(self.project_dir).joinpath("templates")
        for template_dir in ["appendices", "components", "frontmatter", "tailoring"]:
            self._create_dir(templates.joinpath(template_dir).as_posix(), parents=True)

    def _create_rendered(self):
        rendered = Path(self.project_dir).joinpath("rendered")
        for rendered_dir in [
            "appendices",
            "components",
            "frontmatter",
            "tailoring",
            "docs",
        ]:
            self._create_dir(rendered.joinpath(rendered_dir).as_posix(), parents=True)

    @staticmethod
    def _create_dir(dir_path: str, parents: bool):
        try:
            Path(dir_path).mkdir(parents=parents)
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
        with Path(self.oc_file).open("w+") as oc:
            oc.write(rtyaml.dump(opencontrol.model_dump()))

    def _write_project(self):
        with Path(self.project_dir).joinpath("project").with_suffix(".yaml").open(
            "w+"
        ) as pr:
            pr.write(rtyaml.dump(self.model_dump()))
