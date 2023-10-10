from typing import Union
from models import Sign, Form, Value


def read_ogsl() -> [str]:
  with open('ogsl.asl', 'r') as f:
    lines = f.readlines()
    lines = [l.replace('\n', '').replace('\t', ' ').strip() for l in lines]
    return lines


def find_sign_blocks(lines):
    inside_sign_block = False

    sign_blocks = [] # list of (start, end)
    sign_start_line = 0
    
    for i, line in enumerate(lines):
        token = line.split(' ', 1)[0]
        
        if token == '@sign' or token == "@sign-":
            if inside_sign_block:
                raise SyntaxError(f"Nested '@sign' detected. Starting at line {sign_start_line+1}, another '@sign' found at line {i+1}.")
            inside_sign_block = True
            sign_start_line = i
        elif token == '@end':
            data = line.split(' ', 1)[1] if ' ' in line else None
            if data == 'sign':
                if not inside_sign_block:
                    raise SyntaxError(f"Orphan '@end sign' detected at line {i+1}.")
                inside_sign_block = False
                sign_blocks.append((sign_start_line, i))

    if inside_sign_block:
        raise SyntaxError(f"Unclosed '@sign' block starting at line {sign_start_line+1}.")
    return sign_blocks


def parse_sign_block(lines: [str], block_start: int, block_end: int):
  block_lines = lines[block_start:block_end]

  sign_name = block_lines[0].split(' ', 1)[1]
  sign = Sign(name=sign_name)

  value_scope: Union[Sign, Form] = sign
  note_scope: Union[Sign, Form, Value] = sign

  for i, line in enumerate(block_lines[1:]):
      line_num = block_start + i + 2

      token, data = line.split(' ', 1) if ' ' in line else (line, None)
      
      # Values can belong to either a sign or a form.
      if token == '@v' or token == "@v-":
        value = Value(value=data, deprecated=(token == "@v-"))
        value_scope.values.append(value)
        note_scope = value

      # Form
      elif token == '@form':
        if isinstance(value_scope, Form):
          sign.forms.append(value_scope)
        form = Form(variant_code=data)
        value_scope = form
        note_scope = form

      # ----------------------
      # ------- NOTES --------
      # ----------------------
      elif token == '@note':
        note_scope.notes.append(data)
      elif token == "@inote":
        note_scope.inotes.append(data)

      # ----------------------
      # ----- UNICODE --------
      # ----------------------
      # @uage = unicode age/version
      elif token == "@uage":
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_version is not None:
            raise ValueError(f"Duplicate '@uage' on line {line_num}.")
          value_scope.unicode_version = data
        else:
          raise ValueError(f"Unexpected '@uage' on line {line_num}.")
      # @ucun = unicode cuneiform
      elif token == "@ucun":
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_cuneiform is not None:
            raise ValueError(f"Duplicate '@ucun' on line {line_num}.")
          value_scope.unicode_cuneiform = data
        else:
          raise ValueError(f"Unexpected '@ucun' on line {line_num}.")
      # @umap = unicode map
      elif token == '@umap':
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_map is not None:
            raise ValueError(f"Duplicate '@umap' on line {line_num}.")
          value_scope.unicode_map = data
        else:
          raise ValueError(f"Unexpected '@umap' on line {line_num}.")
      # @uname = unicode name
      elif token == "@uname":
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_name is not None:
            raise ValueError(f"Duplicate '@uname' on line {line_num}.")
          value_scope.unicode_name = data
        else:
          raise ValueError(f"Unexpected '@uname' on line {line_num}.")
      # @unote = unicode note
      elif token == '@unote':
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_notes is not None:
            raise ValueError(f"Duplicate '@unote' on line {line_num}.")
          value_scope.unicode_notes = data
        else:
          raise ValueError(f"Unexpected '@unote' on line {line_num}.")
      # @useq = unicode sequence
      elif token == "@useq":
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          if value_scope.unicode_sequence is not None:
            raise ValueError(f"Duplicate '@useq' on line {line_num}.")
          value_scope.unicode_sequence = data
        else:
          raise ValueError(f"Unexpected '@useq' on line {line_num}.")

      # ----------------------
      # ------- OTHER --------
      # ----------------------
      elif token == "@list":
        if isinstance(value_scope, Sign) or isinstance(value_scope, Form):
          value_scope.signlists.append(data)
        else:
          raise ValueError(f"Unexpected '@list' on line {line_num}.")
      elif token == "@aka":
        continue
      elif token == "@@":
        continue
      elif token == "@lit":
        continue
      elif token == '@sys':
        continue
      elif token == '@ref':
        continue
      elif token == '@pname':
        continue
      elif token == '@fake':
        continue
      elif token in ['ideally', 'now', 'or']:
        continue
      else:
        raise ValueError(f"Unrecognized token '{token}' on line {line}.")

  if isinstance(value_scope, Form):
    sign.forms.append(value_scope)
  return sign

def main():
  lines = read_ogsl()
  sign_blocks = find_sign_blocks(lines)
  signs = []
  for block_start, block_end in sign_blocks:
    sign = parse_sign_block(lines, block_start, block_end)
    signs.append(sign)

  out = {}
  import json
  for sign in signs:
    for value in sign.values:
      val = value.value
      if val[-1] == "?":
        val = val[:-1]
      out[val] = sign.unicode_cuneiform if sign.unicode_cuneiform is not None else sign.name
    for form in sign.forms:
      for value in form.values:
        val = value.value
        if val[-1] == "?":
          val = val[:-1]
        out[val] = form.unicode_cuneiform if form.unicode_cuneiform is not None else form.variant_code
  with open("signs-2.json", "w") as f:
    json.dump(out, f, ensure_ascii=False)
if __name__ == "__main__":
  main()