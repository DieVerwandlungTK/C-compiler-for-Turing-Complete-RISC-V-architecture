import sys
from tokenizer import Tokenizer, TokenType
from syntax_tree import Parser, Node, NodeType

class Compiler():
    def __init__(self, file_path: str) -> None:
        self.file_name = file_path
    
    def compile(self, node: Node) -> None:
        f = open(self.file_name, "w")
        f.close()

        f = open(self.file_name, "a")
        f.write("main:\n")

        def _prelude() -> None:
            f.write("   li t2, 4\n")
            f.write("   sub sp, sp, t2\n")
            f.write("   lw t0, 0(sp)\n")
            f.write("   sub sp, sp, t2\n")
            f.write("   lw t1, 0(sp)\n")
        
        def _epilogue() -> None:
            f.write("   sw t0, 0(sp)\n")
            f.write("   addi sp, sp, 4\n")

        def _recursive_compile(node: Node) -> None:
            if node.node_type == NodeType.ND_ADD:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   add t0, t0, t1\n")
                _epilogue()

            elif node.node_type == NodeType.ND_SUB:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   sub t0, t0, t1\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_MUL:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   mul t0, t0, t1\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_DIV:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   div t0, t0, t1\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_NUM:
                f.write(f"   li t0, {node.val}\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_EQ:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   xor t0, t0, t1\n")
                f.write("   seqz t0, t0\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_NEQ:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   xor t0, t0, t1\n")
                f.write("   snez t0, t0\n")
                _epilogue()

            elif node.node_type == NodeType.ND_LT:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   slt t0, t0, t1\n")
                _epilogue()
            
            elif node.node_type == NodeType.ND_LE:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _prelude()
                f.write("   slt t2, t0, t1\n")
                f.write("   xor t3, t0, t1\n")
                f.write("   seqz t3, t3\n")
                f.write("   or t0, t2, t3\n")
                _epilogue()
            
            else:
                sys.exit(1)
            f.write("\n")
            
        _recursive_compile(node)
        f.write("   ret\n")
        f.close()

                




if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        print("The given number of arguments is invalid.", file=sys.stderr)
        sys.exit(1)

    
    tokenizer = Tokenizer()
    tokenizer.tokenize(open(args[1], "r").read())
    parser = Parser(tokenizer)
    parser.parse()
    compiler = Compiler(args[2])
    compiler.compile(parser.root)
