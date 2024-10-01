def strtol(s: str) -> tuple[int, int]:
    n = 0
    cnt = 0
    for i, c in enumerate(s):
        if c.isdigit():
            n = n * 10 + int(c)
            cnt = i
        else:
            break

    return n, cnt + 1

def is_valid_as_head(s: str) -> bool:
    if s[0].isalpha() or s[0] == "_":
        return True
    return False

def get_ident(s: str) -> str:
    ident = ""
    for c in s:
        if c.isalnum() or c == "_":
            ident += c
        else:
            break
    return ident

def find_label(label: str, lines: list[list[str]]) -> int:
    for i, toks in enumerate(lines):
        if toks[0] == f"{label}:":
            return i
    return -1