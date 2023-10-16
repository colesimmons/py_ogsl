from pydantic import BaseModel, root_validator, field_validator, ValidationInfo
from typing import List, Optional, Union
from enum import Enum


class _LineType(Enum):
    InternalNote = "@inote"
    Lit = "@lit"
    Note = "@note"
    Ref = "@ref"
    Sys = "@sys"
    Value = "@v"
    ValueDeprecated = "@v-"


class Value(BaseModel):
    value: str
    is_questionable: bool = False
    is_deprecated: bool = False
    #lang_restriction: str = ""
    #proof_example: str = ""
    sys: List[str] = [] # ?
    ref: str = "" # ?
    lit: List[str] = [] # ?
    notes: List[str] = []
    inotes: List[str] = []

    @field_validator("*")
    @classmethod
    def validate_fields_unique(cls, value, info: ValidationInfo):
        should_be_unique = info.field_name in [
            "sys",
            "ref"
            "lit",
        ]
        if (
            should_be_unique
            and info.field_name in info.data
            and info.data[info.field_name]
        ):
            raise ValueError(
                f"Duplicate values for '{info.field_name}' in sign {info.data['name']}."
            )
        return value

    @classmethod
    def from_lines(cls, lines) -> "Value":
      value: Optional["Value"] = None

      for line in lines:
        line_type, data = _parse_line(line)

        if line_type == _LineType.Value or line_type == _LineType.ValueDeprecated:
          is_questionable = data.endswith("?")
          is_deprecated = line_type == _LineType.ValueDeprecated
          data = data[:-1] if is_questionable else data
          value = cls(value=data, is_deprecated=is_deprecated, is_questionable=is_questionable)
        elif line_type == _LineType.InternalNote:
          value.inotes.append(data)
        elif line_type == _LineType.Lit:
          value.lit.append(data)
        elif line_type == _LineType.Note:
          value.notes.append(data)
        elif line_type == _LineType.Ref:
          if value.ref:
            raise ValueError(f"Duplicate ref value in value block {lines}.")
          value.ref = data
        elif line_type == _LineType.Sys:
          value.sys.append(data)
        else:
          raise ValueError(f"Unrecognized line type '{line_type}' in value block {lines}.")

      return value


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