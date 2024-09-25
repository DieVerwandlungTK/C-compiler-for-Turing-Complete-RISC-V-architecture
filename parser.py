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
        self.tokenizer: Tokenizer = tokenizer
        self.root: Node | None = None
    
    def _expr(self) -> Node:
        node = self._mul()

        while True:
            if self.tokenizer.consume("+"):
                node = Node(NodeType.ND_ADD, node, self._mul())
            elif self.tokenizer.consume("-"):
                node = Node(NodeType.ND_SUB, node, self._mul())
            else:
                break

        return node

    def _mul(self) -> Node:
        node = self._primary()

        while True:
            if self.tokenizer.consume("*"):
                node = Node(NodeType.ND_MUL, node, self._primary())
            elif self.tokenizer.consume("/"):
                node = Node(NodeType.ND_DIV, node, self._primary())
            else:
                break
        
        return node
    
    def _primary(self) -> Node:
        if self.tokenizer.consume("("):
            node = self._expr()
            self.tokenizer.expect(")")
            return node
        else:
            return Node(NodeType.ND_NUM, val=self.tokenizer.expect_number())
    
    def parse(self) -> None:
        self.root = self._expr()
        