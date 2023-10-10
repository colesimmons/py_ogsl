from pydantic import BaseModel, Field
from typing import List, Optional

class Value(BaseModel):
    value: str
    questionable: bool = False
    deprecated: bool = False
    lang_restriction: Optional[str] = None
    proof_example: Optional[str] = None
    notes: List[str] = []
    inotes: List[str] = []

class Form(BaseModel):
    variant_code: str
    name: Optional[str] = None
    values: List[Value] = []
    notes: List[str] = []
    inotes: List[str] = []
    signlists: List[str] = []
    unicode_cuneiform: Optional[str] = None
    unicode_map: Optional[str] = None
    unicode_name: Optional[str] = None
    unicode_notes: Optional[str] = None
    unicode_sequence: Optional[str] = None
    unicode_version: Optional[str] = None

class Sign(BaseModel):
    name: str
    forms: List[Form] = []
    values: List[Value] = []
    notes: List[str] = []
    inotes: List[str] = []
    signlists: List[str] = []
    unicode_cuneiform: Optional[str] = None
    unicode_map: Optional[str] = None
    unicode_name: Optional[str] = None
    unicode_notes: Optional[str] = None
    unicode_sequence: Optional[str] = None
    unicode_version: Optional[str] = None