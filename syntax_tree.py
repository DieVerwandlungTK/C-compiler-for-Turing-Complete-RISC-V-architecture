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
    ND_RETURN = 11  # return
    ND_IF = 12      # if
    ND_FOR = 13     # for

class Node():
    def __init__(self, type, lhs = None, rhs = None, val = None, offset = None, cond = None, 
                 then = None, els = None, labels = None, init = None, inc = None) -> None:
        self.node_type = type
        self.lhs = lhs
        self.rhs = rhs
        self.val = val
        self.offset = offset
        self.cond = cond
        self.then = then
        self.els = els
        self.init = init
        self.inc = inc
        self.labels = labels

class Parser():
    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer: Tokenizer = tokenizer
        self.code: list[Node] = []
        self.l_vars: list[str] = ["0"]  # Initialize with null variable (for some convenience)
        self.lvar_offsets: list[int] = [0]
        self.labels: list[str] = []
    
    def _stmt(self) -> Node:
        if self.tokenizer.consume("return"):
            node = Node(NodeType.ND_RETURN, self._expr())
        
        elif self.tokenizer.consume("if"):
            self.tokenizer.expect("(")
            node = Node(NodeType.ND_IF, cond=self._expr(), labels=[f".Lend{len(self.labels):03}"])
            self.labels.append(node.labels[0])
            self.tokenizer.expect(")")
            node.then = self._stmt()

            if self.tokenizer.consume("else"):
                node.els = self._stmt()
                node.labels.append(f".Lelse{(len(self.labels) - 1):03}")
                self.labels.append(node.labels[1])

            return node
        
        elif self.tokenizer.consume("for"):
            self.tokenizer.expect("(")

            node = Node(NodeType.ND_FOR)

            node.labels = [f".Lbegin{len(self.labels):03}", f".Lend{len(self.labels):03}"]
            self.labels.append(node.labels[0])
            self.labels.append(node.labels[1])

            if not self.tokenizer.consume(";"):
                node.init = self._expr()
                self.tokenizer.expect(";")

            if not self.tokenizer.consume(";"):
                node.cond = self._expr()
                self.tokenizer.expect(";")
            
            if not self.tokenizer.consume(")"):
                node.inc = self._expr()
                self.tokenizer.expect(")")
            
            node.then = self._stmt()
            return node
        
        elif self.tokenizer.consume("while"):
            self.tokenizer.expect("(")

            node = Node(NodeType.ND_FOR)

            node.labels = [f".Lbegin{len(self.labels):03}", f".Lend{len(self.labels):03}"]
            self.labels.append(node.labels[0])
            self.labels.append(node.labels[1])

            node.cond = self._expr()
            self.tokenizer.expect(")")
            node.then = self._stmt()
            return node
            
        else:
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
            if tok.token_str not in self.l_vars:
                tail_offset = self.lvar_offsets[-1]
                self.l_vars.append(tok.token_str)
                self.lvar_offsets.append(tail_offset + 4)

            offset = self.lvar_offsets[self.l_vars.index(tok.token_str)]
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
        