from pydantic import BaseModel, root_validator, field_validator, ValidationInfo
from typing import List, Optional, Union
from enum import Enum
from models.value import Value


class _LineType(Enum):
    Aka = "@aka"
    InternalNote = "@inote"
    Lit = "@lit"
    Name = "@form"
    Note = "@note"
    PName = "@pname"
    Ref = "@ref"
    End = "@@"
    SignList = "@list"
    Sys = "@sys"
    UnicodeAge = "@uage"
    UnicodeCuneiform = "@ucun"
    UnicodeName = "@uname"
    UnicodeNote = "@unote"
    UnicodeSequence = "@useq"
    Value = "@v"
    ValueDeprecated = "@v-"


class Form(BaseModel):
    variant_code: str
    name: str = ""
    aka: str = ""
    values: List[Value] = []
    lit: List[str] = []
    ref: List[str] = []
    notes: List[str] = []
    inotes: List[str] = []
    sys: List[str] = []
    pname: str = ""
    signlists: List[str] = []
    unicode_cuneiform: str = ""
    unicode_map: str = ""
    unicode_name: str = ""
    unicode_notes: str = ""
    unicode_sequence: str = ""
    unicode_version: str = ""

    @classmethod
    def from_lines(cls, lines) -> "Form":
      form: Optional["Form"] = None

      for line in lines:
        line_type, data = _parse_line(line)
        if line_type == _LineType.Name:
          form = cls(variant_code=data)
        elif line_type == _LineType.Aka:
          form.aka = data
        elif line_type == _LineType.End:
          pass
        elif line_type == _LineType.InternalNote:
          form.inotes.append(data)
        elif line_type == _LineType.Lit:
          form.lit.append(data)
        elif line_type == _LineType.Note:
          form.notes.append(data)
        elif line_type == _LineType.PName:
          form.pname = data
        elif line_type == _LineType.Ref:
          form.ref.append(data)
        elif line_type == _LineType.SignList:
          form.signlists.append(data)
        elif line_type == _LineType.Sys:
          form.sys.append(data)
        elif line_type == _LineType.UnicodeAge:
          form.unicode_version = data
        elif line_type == _LineType.UnicodeCuneiform:
          form.unicode_cuneiform = data
        elif line_type == _LineType.UnicodeName:
          form.unicode_name = data
        elif line_type == _LineType.UnicodeNote:
          form.unicode_notes = data
        elif line_type == _LineType.UnicodeSequence:
          form.unicode_sequence = data
        elif line_type == _LineType.Value:
          pass
        elif line_type == _LineType.ValueDeprecated:
          pass
        else:
          raise ValueError(f"Unrecognized line type '{line_type}' in form block {lines}.")
      return form

    @property
    def is_compound(self):
        return "|" in (self.name or "")


def _parse_line(line: str) -> (_LineType, str):
    try:
      line_type_str, data = line.split(" ", 1)
    except ValueError:
      line_type_str, data = line, ""

    try:
        line_type = _LineType(line_type_str)
    except ValueError:
        raise ValueError(
            f"Unrecognized line type '{line_type_str}' in block {line}."
        )
    return (line_type, data)