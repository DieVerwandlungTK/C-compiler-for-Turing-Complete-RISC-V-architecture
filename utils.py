def strtol(s: str) -> tuple[int, str]:
    n = 0
    cnt = 0
    for i, c in enumerate(s):
        if c.isdigit():
            n = n * 10 + int(c)
            cnt = i
        else:
            break
    s = s[cnt + 1:]
    return n, s