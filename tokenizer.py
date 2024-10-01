from enum import Enum
import sys
from utils import *

class TokenType(Enum):
    TK_RESERVED = 0
    TK_IDENT = 1
    TK_NUM = 2
    TK_EOF = 3
    TK_RETURN = 4

class Token():
    def __init__(self, type: TokenType, token_str: str, val = None) -> None:
        self.type = type
        self.val = val
        self.token_str = token_str

class Tokenizer():
    def __init__(self) -> None:
        self.tokens: list[Token] = []

    def tokenize(self, src: str) -> None:
        i = 0
        while i < len(src):
            if src[i].isspace():
                i += 1
                continue
            
            elif src[i:i+2] in ("==", "!=", "<=", ">="):
                self.tokens.append(Token(TokenType.TK_RESERVED, src[i:i+2]))
                i += 2
                continue

            elif src[i] in "+-()*/<>=;":
                self.tokens.append(Token(TokenType.TK_RESERVED, src[i]))
                i += 1
                continue

            elif src[i].isdigit():
                val, val_len = strtol(src[i:])
                self.tokens.append(Token(TokenType.TK_NUM, src[i:i+val_len], val))
                i += val_len
                continue

            elif src[i:i+6] == "return" and not src[i+6].isalnum() and src[i+6] != "_":
                self.tokens.append(Token(TokenType.TK_RETURN, "return"))
                i += 6
                continue

            elif is_valid_as_head(src[i]):
                ident = get_ident(src[i:])
                self.tokens.append(Token(TokenType.TK_IDENT, ident))
                i += len(ident)
                continue

            else:
                print(f"Failed to tokenize: {src[i:]}", file=sys.stderr)
                sys.exit(1)
        
        self.tokens.append(Token(TokenType.TK_EOF, ""))
    
    def consume(self, op: str) -> bool:
        if self.tokens[0].type == TokenType.TK_RESERVED or self.tokens[0].type == TokenType.TK_RETURN:
            if self.tokens[0].token_str == op:
                self.tokens.pop(0)
                return True
        return False
    
    def consume_ident(self) -> Token | None:
        if self.tokens[0].type != TokenType.TK_IDENT:
            return None
        
        return self.tokens.pop(0)
    
    def expect(self, op: str) -> None:
        if self.tokens[0].type != TokenType.TK_RESERVED or self.tokens[0].token_str != op:
            print(f"Expected {op} but got {self.tokens[0].token_str}.", file=sys.stderr)
            sys.exit(1)
        self.tokens.pop(0)
    
    def expect_number(self) -> int:
        if self.tokens[0].type != TokenType.TK_NUM:
            print(f"Expected a number but got {self.tokens[0].token_str}.", file=sys.stderr)
            sys.exit(1)
        val = self.tokens[0].val
        self.tokens.pop(0)
        return val
    
    def at_eof(self) -> bool:
        return self.tokens[0].type == TokenType.TK_EOF

        
        
        
        
