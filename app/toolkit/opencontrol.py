from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

import rtyaml
from pydantic import BaseModel, Field, PrivateAttr

from config import config

ROOT_DIR = config.get("ROOT_DIR", Path())

OPENCONTROL_SCHEMA_VERSION = "1.0.0"
COMPONENT_SCHEMA_VERSION = "3.1.0"


class OpenControlElement(BaseModel):
    @staticmethod
    def new_relative_path(self):
        assert False

    def storage_path(self, root_dir=None):
        if hasattr(self, "_file"):
            p = Path(self._file)
        else:
            p = self.new_relative_path()
        if root_dir:
            return root_dir / p
        else:
            return p


class Reference(OpenControlElement):
    name: str
    path: str  # TODO (url?)
    type: str  # TODO (enum)


class Statement(OpenControlElement):
    text: str
    key: Optional[str]


class Parameter(OpenControlElement):
    key: str
    text: str


class ImplementationStatusEnum(str, Enum):
    partial = "partial"
    complete = "complete"
    planned = "planned"
    none = "none"


class CoveredBy(OpenControlElement):
    verification_key: str
    system_key: Optional[str]
    component_key: Optional[str]


class Control(OpenControlElement):
    control_key: str
    standard_key: str
    covered_by: Optional[List[CoveredBy]]
    narrative: Optional[List[Statement]]
    references: Optional[List[Reference]]
    implementation_statuses: Optional[Set[ImplementationStatusEnum]]
    control_origins: Optional[List[str]]
    parameters: Optional[List[Parameter]]


class ComponentFile(OpenControlElement):
    family: str
    documentation_complete: bool
    satisfies: Optional[List[Control]]


class Component(OpenControlElement):
    name: str
    schema_version: str = COMPONENT_SCHEMA_VERSION
    satisfies: List[str]

    def update(self, action: str, component: str):
        component_path = f"./{component}"
        if action == "add" and component_path not in self.satisfies:
            self.satisfies.append(component_path)
        elif action == "remove" and component_path in self.satisfies:
            self.satisfies.remove(component_path)

    def write(self, component: str):
        component_path = (
            ROOT_DIR.joinpath("templates")  # type: ignore
            .joinpath("opencontrol")  # type: ignore
            .joinpath(component)  # type: ignore
            .joinpath("component")
            .with_suffix(".yaml")  # type: ignore
        )
        with component_path.open("w+") as oc:
            oc.write(rtyaml.dump(self.model_dump()))


class Metadata(BaseModel):
    description: str
    maintainers: Optional[List[str]] = Field(default=[])


class OpenControl(BaseModel):
    schema_version: str = OPENCONTROL_SCHEMA_VERSION
    name: str
    metadata: Metadata
    components: List[str] = Field(default=[])
    certifications: List[str] = Field(default=[])
    standards: List[str] = Field(default=[])

    _root_dir: str = PrivateAttr()

    def add(self, project_path: str, key: str, attribute: str):
        field = getattr(self, key)
        if attribute not in field:
            field.append(attribute)
        setattr(self, key, field)
        self.write(project_path=project_path)

    def remove(self, project_path: str, key: str, attribute: str):
        field = getattr(self, key)
        if attribute in field:
            field.remove(attribute)
        setattr(self, key, field)
        self.write(project_path=project_path)

    def write(self, project_path: str):
        opencontrol_path = (
            ROOT_DIR.joinpath(project_path)  # type: ignore
            .joinpath("opencontrol")
            .with_suffix(".yaml")  # type: ignore
        )
        with opencontrol_path.open("w") as oc:
            oc.write(rtyaml.dump(self.model_dump()))
