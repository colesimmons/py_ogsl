from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List, Optional
from enum import Enum
from models.form import Form
from models.value import Value


class _LineType(Enum):
    Aka = "@aka"
    End = "@end"
    Fake = "@fake"
    Form = "@form"
    InternalNote = "@inote"
    Lit = "@lit"
    Name = "@sign"
    NameDeprecated = "@sign-"
    Note = "@note"
    PName = "@pname"
    Ref = "@ref"
    Separator = "@@"
    SignList = "@list"
    Sys = "@sys"
    UnicodeAge = "@uage"
    UnicodeCuneiform = "@ucun"
    UnicodeMap = "@umap"
    UnicodeName = "@uname"
    UnicodeNote = "@unote"
    UnicodeSequence = "@useq"
    Value = "@v"
    ValueDeprecated = "@v-"


class Sign(BaseModel):
    name: str
    is_deprecated: bool
    pname: str = ""  # e.g. if name = UR₂×(A.NA), pname = |UR₂×A+NA|
    aka: str = ""
    forms: List[Form] = []
    values: List[Value] = []
    notes: List[str] = []
    inotes: List[str] = []
    sign_list: List[str] = []
    literature: List[str] = []
    references: List[str] = []
    unicode_cuneiform: str = ""
    unicode_map: str = ""
    unicode_name: str = ""
    unicode_notes: str = ""
    unicode_sequence: str = ""
    unicode_version: str = ""

    @property
    def is_compound(self):
        return "|" in (self.name or "")

    @field_validator("*")
    @classmethod
    def validate_fields_unique(cls, value, info: ValidationInfo):
        should_be_unique = info.field_name.startswith("unicode") or info.field_name in [
            "aka",
            "name"
            "pname",
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
    def from_lines(
        cls, lines: List[str]
    ) -> Optional["Sign"]:
        if not lines:
            return None

        # FIRST LINE
        first_line = lines[0]
        line_type, first_line_val = _parse_line(first_line)
        if line_type not in [_LineType.Name, _LineType.NameDeprecated]:
          raise ValueError(f"Expected @sign or @sign- on line {first_line}.")
        sign = Sign(name=first_line_val, is_deprecated=line_type == _LineType.NameDeprecated)

        # LAST LINE
        final_line = lines[-1]
        if final_line != "@end sign":
          raise ValueError(f"Expected @end on line {final_line}.")

        # Loop through remaining lines.
        for i, line in enumerate(lines[1:-1]):
            line_type, data = _parse_line(line)
            if line_type == _LineType.Fake:
                return None

            # Once we start seeing value or form blocks,
            # all properties thereafter should be scoped to a form or a value.
            # We'll handle them separately to avoid any leakage.
            if line_type in [
                _LineType.Form,
                _LineType.Value,
                _LineType.ValueDeprecated,
            ]:
              value_blocks, form_blocks = _separate_out_value_and_form_blocks(lines[i+1:-1])
              sign.values = [Value.from_lines(block) for block in value_blocks]
              sign.forms = [Form.from_lines(block) for block in form_blocks]
              break

            sign._assign_property(line_type, data)

        return sign

    def _assign_property(self, line_type: _LineType, val: str):
      if line_type == _LineType.Aka:
          self.aka = val
      elif line_type == _LineType.InternalNote:
          self.inotes.append(val)
      elif line_type == _LineType.Lit:
          self.literature.append(val)
      elif line_type == _LineType.PName:
          self.pname = val
      elif line_type == _LineType.Ref:
          self.references.append(val)
      elif line_type == _LineType.Note:
          self.notes.append(val)
      elif line_type == _LineType.SignList:
          self.sign_list.append(val)
      elif line_type == _LineType.UnicodeAge:
          self.unicode_version = val
      elif line_type == _LineType.UnicodeCuneiform:
          self.unicode_cuneiform = val
      elif line_type == _LineType.UnicodeMap:
          self.unicode_map = val
      elif line_type == _LineType.UnicodeName:
          self.unicode_name = val
      elif line_type == _LineType.UnicodeNote:
          self.unicode_notes = val
      elif line_type == _LineType.UnicodeSequence:
          self.unicode_sequence = val
      else:
          raise ValueError(
              f"Unrecognized line type '{line_type}' in block {lines}."
          )


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


def _separate_out_value_and_form_blocks(lines: List[str]) -> (List[List[str]], List[List[str]]):
  # First step is to split between all sign value-related lines and all form-related lines.
  all_value_lines: List[str] = lines
  all_form_lines: List[str] = []

  for i, line in enumerate(lines):
    line_type, _ = _parse_line(line)
    if line_type == _LineType.Form:
      all_value_lines = lines[:i]
      all_form_lines = lines[i:]
      break
  
  # Next step is to split the value lines into blocks.
  value_blocks: List[List[str]] = []
  for line in all_value_lines:
    line_type, _ = _parse_line(line)
    if line_type in [_LineType.Value, _LineType.ValueDeprecated]:
        value_blocks.append([line])
    else:
        value_blocks[-1].append(line)

  # Now do the same for the form lines.
  form_blocks: List[List[str]] = []
  for line in all_form_lines:
    line_type, _ = _parse_line(line)
    if line_type == _LineType.Form:
        form_blocks.append([line])
    else:
        form_blocks[-1].append(line)
  
  return (value_blocks, form_blocks)