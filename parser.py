from enum import Enum
from tokenizer import Tokenizer

class NodeType(Enum):
    ND_ADD = 0
    ND_SUB = 1
    ND_MUL = 2
    ND_DIV = 3
    ND_NUM = 4

class Node():
    def __init__(self, type: NodeType, lhs: "Node" | None = None, rhs: "Node" | None = None, val: int | None = None) -> None:
        self.node_type = type
        self.lhs = lhs
        self.rhs = rhs
        self.val = val

class Parser():
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer