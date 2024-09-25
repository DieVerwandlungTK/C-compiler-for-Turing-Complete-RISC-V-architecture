import sys
from tokenizer import Tokenizer, TokenType

def strtol(s):
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

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        print("The given number of arguments is invalid.", file=sys.stderr)
        sys.exit(1)

    with open(args[2], "w") as f:
        f.write("main:\n")

        tokenizer = Tokenizer()
        tokenizer.tokenize(open(args[1], "r").read())

        while not tokenizer.at_eof():
            if tokenizer.consume("+"):
                f.write(" addi ")
                f.write(f"a0, a0, {tokenizer.expect_number()}\n")
                continue

            if tokenizer.consume("-"):
                f.write(" li ")
                f.write(f"t0, {tokenizer.expect_number()}\n")
                f.write(" sub ")
                f.write(f"a0, a0, t0\n")
                continue

            if tokenizer.tokens[0].token_type == TokenType.TK_NUM:
                f.write(" li ")
                f.write(f"a0, {tokenizer.expect_number()}\n")
                continue

            print(f"Unexpected token: {tokenizer.tokens[0].token_str}", file=sys.stderr)
            sys.exit(1)
        
                
        f.write(" ret\n")
