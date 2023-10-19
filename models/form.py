from pydantic import BaseModel, root_validator, field_validator, ValidationInfo
from typing import List, Optional, Union
from enum import Enum
from models.value import Value


class _LineType(Enum):
    Aka = "@aka"
    End = "@@"
    InternalNote = "@inote"
    Lit = "@lit"
    Name = "@form"
    Note = "@note"
    PName = "@pname"
    Ref = "@ref"
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
    pname: str = ""  # e.g. |GA₂×(A.HA)| -> |GA₂×A+HA|
    signlists: List[str] = []
    unicode_cuneiform: str = ""
    unicode_map: str = ""
    unicode_name: str = ""
    unicode_notes: str = ""
    unicode_sequence: str = ""
    unicode_version: str = ""

    @classmethod
    def from_lines(cls, lines) -> "Form":
        _, first_line = _parse_line(lines[0])
        form = cls(variant_code=first_line)

        for i, line in enumerate(lines):
            line_type, data = _parse_line(line)

            # Once we start seeing value blocks,
            # all properties thereafter should be scoped to a value.
            # We'll handle them separately to avoid any leakage.
            if line_type in [
                _LineType.Value,
                _LineType.ValueDeprecated,
            ]:
                value_blocks = _separate_out_value_blocks(lines[i:])
                form.values = [Value.from_lines(block) for block in value_blocks]
                break
            
            # Skip these
            if line_type == _LineType.Name:
                pass
            elif line_type == _LineType.End:
                pass
            else:
              form._validate_uniqueness(line_type)
              form._assign_property(line_type, data)
        return form

    @property
    def is_compound(self):
        return "|" in (self.name or "")

    def _validate_uniqueness(self, line_type: _LineType):
      if line_type == _LineType.Aka and self.aka:
          raise ValueError(f"Duplicate values for 'aka' in form {self.variant_code}.")
      elif line_type == _LineType.PName and self.pname:
          raise ValueError(f"Duplicate values for 'pname' in form {self.variant_code}.")
      elif line_type == _LineType.UnicodeAge and self.unicode_version:
          raise ValueError(f"Duplicate values for 'uage' in form {self.variant_code}.")
      elif line_type == _LineType.UnicodeCuneiform and self.unicode_cuneiform:
          raise ValueError(f"Duplicate values for 'ucun' in form {self.variant_code}.")
      elif line_type == _LineType.UnicodeName and self.unicode_name:
          raise ValueError(f"Duplicate values for 'uname' in form {self.variant_code}.")
      elif line_type == _LineType.UnicodeNote and self.unicode_notes:
          raise ValueError(f"Duplicate values for 'unote' in form {self.variant_code}.")
      elif line_type == _LineType.UnicodeSequence and self.unicode_sequence:
          raise ValueError(f"Duplicate values for 'useq' in form {self.variant_code}.")
    
    def _assign_property(self, line_type: _LineType, data: str):
      if line_type == _LineType.Aka:
          self.aka = data
      elif line_type == _LineType.PName:
          self.pname = data
      elif line_type == _LineType.UnicodeAge:
          self.unicode_version = data
      elif line_type == _LineType.UnicodeCuneiform:
          self.unicode_cuneiform = data
      elif line_type == _LineType.UnicodeName:
          self.unicode_name = data
      elif line_type == _LineType.UnicodeNote:
          self.unicode_notes = data
      elif line_type == _LineType.UnicodeSequence:
          self.unicode_sequence = data

      elif line_type == _LineType.InternalNote:
          self.inotes.append(data)
      elif line_type == _LineType.Lit:
          self.lit.append(data)
      elif line_type == _LineType.Note:
          self.notes.append(data)
      elif line_type == _LineType.Ref:
          self.ref.append(data)
      elif line_type == _LineType.SignList:
          self.signlists.append(data)

      else:
          raise ValueError(
              f"Invalid assignment of '{line_type}' in form {self.variant_code}."
          )


def _parse_line(line: str) -> (_LineType, str):
    try:
        line_type_str, data = line.split(" ", 1)
    except ValueError:
        line_type_str, data = line, ""

    try:
        line_type = _LineType(line_type_str)
    except ValueError:
        raise ValueError(f"Unrecognized line type '{line_type_str}' in block {line}.")
    return (line_type, data)

def _separate_out_value_blocks(
    lines: List[str],
) -> List[List[str]]:
    # Next step is to split the value lines into blocks.
    value_blocks: List[List[str]] = []
    for line in lines:
        line_type, _ = _parse_line(line)
        if line_type in [_LineType.Value, _LineType.ValueDeprecated]:
            value_blocks.append([line])
        elif line_type == _LineType.End:
            pass
        else:
            value_blocks[-1].append(line)
    return value_blocks
