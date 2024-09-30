from enum import Enum
from tokenizer import Tokenizer

class NodeType(Enum):
    ND_ADD = 0      # +
    ND_SUB = 1      # -
    ND_MUL = 2      # *
    ND_DIV = 3      # /
    ND_NUM = 4      # Number
    ND_EQ = 5       # ==
    ND_NEQ = 6      # !=
    ND_LT = 7       # <
    ND_LE = 8       # <=
    ND_LVAR = 9     # Local variable
    ND_ASSIGN = 10  # =

class Node():
    def __init__(self, type, lhs = None, rhs = None, val = None, offset = None) -> None:
        self.node_type = type
        self.lhs = lhs
        self.rhs = rhs
        self.val = val
        self.offset = offset

class Parser():
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer: Tokenizer = tokenizer
        self.code: list[Node] = []
    
    def _stmt(self) -> Node:
        node = self._expr()
        self.tokenizer.expect(";")
        return node
    
    def _expr(self) -> Node:
        return self._assign()
    
    def _assign(self) -> Node:
        node = self._equality()

        if self.tokenizer.consume("="):
            node = Node(NodeType.ND_ASSIGN, node, self._assign())
        
        return node
    
    def _equality(self) -> Node:
        node = self._relational()

        while True:
            if self.tokenizer.consume("=="):
                node = Node(NodeType.ND_EQ, node, self._relational())

            elif self.tokenizer.consume("!="):
                node = Node(NodeType.ND_NEQ, node, self._relational())
                
            else:
                break
        
        return node
    
    def _relational(self) -> Node:
        node = self._add()

        while True:
            if self.tokenizer.consume("<"):
                node = Node(NodeType.ND_LT, node, self._add())

            elif self.tokenizer.consume("<="):
                node = Node(NodeType.ND_LE, node, self._add())

            elif self.tokenizer.consume(">"):
                node = Node(NodeType.ND_LT, self._add(), node)

            elif self.tokenizer.consume(">="):
                node = Node(NodeType.ND_LE, self._add(), node)

            else:
                break
        
        return node
    
    def _add(self) -> Node:
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
        node = self._unary()

        while True:
            if self.tokenizer.consume("*"):
                node = Node(NodeType.ND_MUL, node, self._unary())

            elif self.tokenizer.consume("/"):
                node = Node(NodeType.ND_DIV, node, self._unary())

            else:
                break
        
        return node
    
    def _unary(self) -> Node:
        if self.tokenizer.consume("+"):
            return self._primary()
        
        elif self.tokenizer.consume("-"):
            return Node(NodeType.ND_SUB, Node(NodeType.ND_NUM, val=0), self._primary())
        
        else:
            return self._primary()
    
    def _primary(self) -> Node:
        tok = self.tokenizer.consume_ident()
        if tok:
            offset = (ord(tok.token_str) - ord("a") + 1)*4
            return Node(NodeType.ND_LVAR, offset=offset)
        
        elif self.tokenizer.consume("("):
            node = self._expr()
            self.tokenizer.expect(")")
            return node
        
        else:
            return Node(NodeType.ND_NUM, val=self.tokenizer.expect_number())
    
    def parse(self) -> None:
        while not self.tokenizer.at_eof():
            self.code.append(self._stmt())
        