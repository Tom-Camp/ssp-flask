"""
Copyright 2019-2024 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/compliancetools#copyright.
"""

from typing import List

from pydantic import BaseModel

from app.toolkit.makefamilies.family import Family


class Ssp(BaseModel):
    name: str
    standards: List[str]
    families: List[Family]
