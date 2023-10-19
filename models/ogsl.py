from pydantic import BaseModel
from typing import List
from models.sign import Sign


class OGSL(BaseModel):
    lines: List[str] = []
    blocks: List[List[str]] = []
    signs: List[Sign] = []

    @classmethod
    def load(cls, filename: str = "./ogsl.asl") -> "OGSL":
        ogsl = cls()
        ogsl.lines = _read_lines(filename)
        ogsl.blocks = _get_blocks(ogsl.lines)
        sign_blocks = _limit_to_sign_blocks(ogsl.blocks)
        ogsl.signs = _parse_sign_blocks(sign_blocks)
        return ogsl


def _read_lines(filename: str) -> List[str]:
    with open(filename, "r") as f:
        lines = f.readlines()
        lines = [l.replace("\n", "").replace("\t", " ").strip() for l in lines]
        return lines


def _get_blocks(lines: List[str]) -> List[List[str]]:
    """
    Find all blocks of text separated by a blank line.
    Returns a list of blocks, where each block is a list of its lines.
    """
    groups = []
    current_group = []

    for line in lines:
        stripped_line = line.strip().replace("\t", " ")

        if stripped_line:
            current_group.append(stripped_line)
        else:
            if current_group:
                groups.append(current_group)
                current_group = []

    if current_group:
        groups.append(current_group)

    return groups


def _validate_sign_block(lines: List[str]) -> List[str]:
    first_line = lines[0]
    last_line = lines[-1]

    # Validate first line
    first_line_tokens = first_line.split(" ")
    if len(first_line_tokens) != 2:
        raise SyntaxError(f"Invalid '@sign' block: {lines}")

    # Validate last line
    if last_line != "@end sign":
        raise SyntaxError(f"Invalid ending to '@sign' block: {lines}")

    # Deal w/ cases like a @unote wrapping to the next line (as in @sign DE₂)
    # and make sure no inner lines contain @sign
    fmtd_lines = []
    for i, line in enumerate(lines):
        first_token = line.split(" ")[0]
        if i > 0 and (first_token == "@sign" or first_token == "@sign-"):
            raise SyntaxError(f"Nested '@sign' detected in block:\n{lines}")

        if not line.startswith("@"):
            fmtd_lines[-1] = fmtd_lines[-1] + line
        elif not line:
            pass
        else:
            fmtd_lines.append(line)
    return fmtd_lines


def _limit_to_sign_blocks(blocks: List[List[str]]) -> List[List[str]]:
    """
    Given a list of blocks, return a list of only those blocks that are sign blocks.
    """
    sign_blocks = []
    other_block_types = set()
    for block in blocks:
        first_line_tokens = block[0].split(" ")
        if first_line_tokens[0] == "@sign" or first_line_tokens[0] == "@sign-":
            sign_blocks.append(block)
        else:
            other_block_types.add(first_line_tokens[0])
    print(f"Detected {len(sign_blocks)} sign blocks out of {len(blocks)} total.")
    print("Other block types: ", list(sorted(other_block_types)))
    return [_validate_sign_block(block) for block in sign_blocks]


def _parse_sign_blocks(blocks: List[List[str]]) -> List[Sign]:
    signs = [Sign.from_lines(block) for block in blocks]
    return [sign for sign in signs if sign is not None]
