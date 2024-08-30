from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

import rtyaml
from pydantic import BaseModel, Field

from config import config

ROOT_DIR = config.get("ROOT_DIR", Path())


OPENCONTROL_SCHEMA_VERSION = "1.0.0"
COMPONENT_SCHEMA_VERSION = "3.1.0"


class Reference(BaseModel):
    name: str
    path: str  # TODO (url?)
    type: str  # TODO (enum)


class Statement(BaseModel):
    text: str
    key: Optional[str]


class Parameter(BaseModel):
    key: str
    text: str


class ImplementationStatusEnum(str, Enum):
    partial = "partial"
    complete = "complete"
    planned = "planned"
    none = "none"


class CoveredBy(BaseModel):
    verification_key: str
    system_key: Optional[str]
    component_key: Optional[str]


class Control(BaseModel):
    control_key: str
    standard_key: str
    covered_by: Optional[List[CoveredBy]]
    narrative: Optional[List[Statement]]
    references: Optional[List[Reference]]
    implementation_statuses: Optional[Set[ImplementationStatusEnum]]
    control_origins: Optional[List[str]]
    parameters: Optional[List[Parameter]]


class ComponentFile(BaseModel):
    family: str
    documentation_complete: bool
    satisfies: Optional[List[Control]]


class Component(BaseModel):
    name: str
    schema_version: str = COMPONENT_SCHEMA_VERSION
    satisfies: List[str]


class Metadata(BaseModel):
    description: str
    maintainers: Optional[List[str]] = Field(default=[])


class OpenControl(BaseModel):
    schema_version: str = OPENCONTROL_SCHEMA_VERSION
    name: str
    metadata: Optional[Metadata]
    components: List[str] = Field(default=[])
    certifications: List[str] = Field(default=[])
    standards: List[str] = Field(default=[])

    def __init__(self, name: str, description: str, maintainers: list):
        metadata = Metadata(
            description=description,
            maintainers=maintainers,
        )
        super().__init__(
            name=name,
            metadata=metadata,
        )

    def write(self, project_path: str):
        opencontrol_path = (
            ROOT_DIR.joinpath(project_path).joinpath("opencontrol").with_suffix(".yaml")  # type: ignore
        )
        with opencontrol_path.open("w+") as oc:
            oc.write(rtyaml.dump(self.model_dump()))
