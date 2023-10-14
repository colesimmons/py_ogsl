from pydantic import BaseModel, root_validator, field_validator, ValidationInfo
from typing import List, Optional, Union
from enum import Enum
from models.value import Value


class Form(BaseModel):
    variant_code: str
    name: str = ""
    values: List[Value] = []
    notes: List[str] = []
    inotes: List[str] = []
    signlists: List[str] = []
    unicode_cuneiform: str = ""
    unicode_map: str = ""
    unicode_name: str = ""
    unicode_notes: str = ""
    unicode_sequence: str = ""
    unicode_version: str = ""

    @classmethod
    def from_lines(cls, lines) -> "Form":
        return cls(variant_code="lorem_ipsum")

    @property
    def is_compound(self):
        return "|" in (self.name or "")
