from pydantic import BaseModel, root_validator
from typing import List


class SignBlock(BaseModel):
    lines: List[str]

    @root_validator(pre=True)
    def custom_init(cls, values):
        lines = values["lines"]
        first_line = lines[0]
        last_line = lines[-1]

        # Validate first line
        first_line_tokens = first_line.split(' ')
        if len(first_line_tokens) != 2:
            raise SyntaxError(f"Invalid '@sign' block: {lines}")
        
        # Validate last line
        if last_line != "@end sign":
            raise SyntaxError(f"Invalid ending to '@sign' block: {lines}")

        # Deal w/ cases like a @unote wrapping to the next line (as in @sign DE₂)
        # and make sure no inner lines contain @sign
        fmtd_lines = []
        for i, line in enumerate(values["lines"]):
            first_token = line.split(' ')[0]
            if i > 0 and (first_token == "@sign" or first_token == "@sign-"):
                raise SyntaxError(f"Nested '@sign' detected in block:\n{lines}")

            if not line.startswith("@"):
                fmtd_lines[-1] = fmtd_lines[-1] + line
            elif not line:
                pass
            else:
                fmtd_lines.append(line)
        values["lines"] = fmtd_lines
        return values
