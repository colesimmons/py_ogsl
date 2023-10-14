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
    NameIsDeprecated = "@sign-"
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
    def parse_line(cls, line: str) -> (_LineType, str):
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


    @classmethod
    def from_lines(
        cls, lines: List[str]
    ) -> Optional["Sign"]:
        if not lines:
            return None

        # Parse first line to get name
        first_line = lines[0]
        line_type, first_line_val = cls.parse_line(first_line)
        if line_type == _LineType.Name or line_type == _LineType.NameIsDeprecated:
          sign = Sign(name=first_line_val, is_deprecated=line_type == _LineType.NameIsDeprecated)
        else:
          raise ValueError(f"Expected @sign or @sign- on line {first_line}.")

        # Validate that final line is @end
        final_line = lines[-1]
        if final_line != "@end sign":
          raise ValueError(f"Expected @end on line {final_line}.")

        # Parse remaining lines
        form_blocks: List[List[str]] = []
        cur_form_block: List[str] = []

        value_blocks: List[List[str]] = []
        cur_value_block: List[str] = []

        for line in lines[1:-1]:
            line_type, data = cls.parse_line(line)

            # Once we start seeing form blocks,
            # the lines no longer define properties of the sign.
            if line_type == _LineType.Form:
                if cur_form_block:
                    form_blocks.append(cur_form_block)
                cur_form_block = [line]
                continue

            if cur_form_block:
                cur_form_block.append(line)
                continue

            # Same with values.
            if line_type == _LineType.Value or line_type == _LineType.ValueDeprecated:
                if cur_value_block:
                    value_blocks.append(cur_value_block)
                cur_value_block = [line]
                continue

            if cur_value_block:
                cur_value_block.append(line)
                continue

            # Okay, now the lines are defining properties of the sign.
            if line_type == _LineType.Fake:
                return None
            else:
              sign.assign_val(line_type, data)

        if cur_value_block:
            value_blocks.append(cur_value_block)
        if cur_form_block:
            form_blocks.append(cur_form_block)

        sign.forms = [Form.from_lines(lines) for lines in form_blocks]
        sign.values = [Value.from_lines(lines) for lines in value_blocks]
        return sign

    def assign_val(self, line_type: _LineType, val: str):
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
  
