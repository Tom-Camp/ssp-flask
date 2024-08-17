from dataclasses import asdict
from pathlib import Path
from typing import List

import rtyaml
from flask import flash
from pydantic import BaseModel

from app.toolkit.base.config import Config
from app.utils.helpers import get_machine_name, load_yaml
from app.utils.library import Library

project_directories = [
    "certifications",
    "keys",
    "standards",
    "rendered/appendices",
    "rendered/components",
    "rendered/frontmatter",
    "rendered/tailoring",
    "templates/appendices",
    "templates/components",
    "templates/frontmatter",
    "templates/tailoring",
]


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
    machine_name: str = ""
    description: str
    maintainers: List[str] | None
    oc_file: str | None
    project_dir: str = ""

    def load(self) -> dict:
        project: dict = {}
        project_path = Path(self.project_dir)
        project["project"] = self.model_dump()
        project["opencontrol"] = load_yaml(
            project_path.joinpath("opencontrol").with_suffix(".yaml").as_posix()
        )
        self._check_oc(project.get("opencontrol", {}))
        project["config"] = asdict(
            Config(
                config=project_path.joinpath("configuration")
                .with_suffix(".yaml")
                .as_posix(),
                keys=project_path.joinpath("keys").as_posix(),
            )
        )

        return project

    def create(self):
        self.machine_name = get_machine_name(name=self.name)
        self.project_dir = Path("project_data").joinpath(self.machine_name).as_posix()
        self._create_dir(dir_path=self.project_dir, parents=True)

        self._create_structure()
        self._create_open_control()

    def _create_structure(self):
        project_path = Path(self.project_dir)
        Library(project_path=project_path.as_posix()).copy(
            filename="configuration.yaml", dest=None
        )
        for directory in project_directories:
            self._create_dir(
                Path(project_path).joinpath(directory).as_posix(), parents=True
            )

        self.oc_file = (
            project_path.joinpath("opencontrol").with_suffix(".yaml").as_posix()
        )
        self._write_project()
        flash(f"Project {self.name} created successfully.", "success")

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

    @staticmethod
    def _check_oc(opencontrol: dict):
        if not opencontrol.get("standards", None):
            flash(
                "The opencontrol file does not contain standards. At least one is "
                "required.",
                "error",
            )
        if not opencontrol.get("certifications", None):
            flash(
                "The opencontrol file does not contain certifications. At least one "
                "is required.",
                "error",
            )
