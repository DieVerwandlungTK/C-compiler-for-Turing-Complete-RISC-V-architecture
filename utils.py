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