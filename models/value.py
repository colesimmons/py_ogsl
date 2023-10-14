from pydantic import BaseModel, root_validator, field_validator, ValidationInfo
from typing import List, Optional, Union
from enum import Enum


class Value(BaseModel):
    value: str
    questionable: bool = False
    deprecated: bool = False
    lang_restriction: str = ""
    proof_example: str = ""
    notes: List[str] = []
    inotes: List[str] = []

    @classmethod
    def from_lines(cls, lines) -> "Value":
        return cls(value="lorem_ipsum")
