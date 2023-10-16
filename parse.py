"""
Description of the file format here:
http://oracc.museum.upenn.edu/ogsl/theogslfileformat/index.html
"""
import json
from typing import List, Union
from models import SignBlock, Sign, Form, Value


def read_ogsl() -> List[str]:
  with open('ogsl.asl', 'r') as f:
    lines = f.readlines()
    lines = [l.replace('\n', '').replace('\t', ' ').strip() for l in lines]
    return lines


def get_blocks(filename) -> List[str]:
    """
    Find all blocks of text separated by a blank line.
    Returns a list of blocks, where each block is a list of its lines.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    groups = []
    current_group = []
    
    for line in lines:
        stripped_line = line.strip().replace('\t', ' ')

        if stripped_line:
            current_group.append(stripped_line)
        else:
            if current_group:
                groups.append(current_group)
                current_group = []
                
    if current_group:
        groups.append(current_group)
        
    return groups

def limit_to_sign_blocks(blocks) -> List[SignBlock]:
    """
    Given a list of blocks, return a list of only those blocks that are sign blocks.
    """
    sign_blocks = []
    other_block_types = set()
    for block in blocks:
        first_line_tokens = block[0].split(' ')
        if first_line_tokens[0] == "@sign" or first_line_tokens[0] == "@sign-":
            block = SignBlock(lines=block)
            sign_blocks.append(block)
        else:
            other_block_types.add(first_line_tokens[0])
    print(f"Detected {len(sign_blocks)} sign blocks out of {len(blocks)} total.")
    print("Other block types: ", list(sorted(other_block_types)))
    return sign_blocks


def parse_sign_blocks(blocks: List[SignBlock]) -> List[Sign]:
  signs = [Sign.from_lines(block.lines) for block in blocks]
  return [sign for sign in signs if sign is not None]

  
def main():
  blocks = get_blocks('ogsl.asl')
  sign_blocks = limit_to_sign_blocks(blocks)
  # Other block types: ['@compoundonly', '@inote', '@listdef', '@lref', '@signlist', '@sysdef']
  parsed = parse_sign_blocks(sign_blocks)

  # Validate: are names unique
  # validate: are signs unique?
  no_cune = 0
  cune = 0
  for sign in parsed:
    #print(sign.name)
    if sign.unicode_cuneiform:
      cune += 1
    else:
      no_cune += 1
  print(no_cune)
  print(cune)


if __name__ == "__main__":
  main()

def dump_to_json(signs):
  out = {}
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