import sys
from tokenizer import Tokenizer, TokenType
from syntax_tree import Parser, Node, NodeType

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

class Compiler():
    def __init__(self, file_path: str) -> None:
        self.file_name = file_path
    
    def compile(self, node: Node) -> None:
        f = open(self.file_name, "w")
        f.close()

        f = open(self.file_name, "a")
        f.write("main:\n")
        def _recursive_compile(node: Node) -> None:
            if node.node_type == NodeType.ND_ADD:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                f.write("   lw t0, 0(sp)\n")
                f.write("   li t2, 4\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   lw t1, 0(sp)\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   add t0, t0, t1\n")
                f.write("   sw t0, 0(sp)\n")
                f.write("   addi sp, sp, 4\n")

            elif node.node_type == NodeType.ND_SUB:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                f.write("   lw t0, 0(sp)\n")
                f.write("   li t2, 4\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   lw t1, 0(sp)\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   sub t0, t0, t1\n")
                f.write("   sw t0, 0(sp)\n")
                f.write("   addi sp, sp, 4\n")
            
            elif node.node_type == NodeType.ND_MUL:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                f.write("   lw t0, 0(sp)\n")
                f.write("   li t2, 4\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   lw t1, 0(sp)\n")
                f.write("   sub sp, sp, t2\n")
                # hoge
            
            elif node.node_type == NodeType.ND_DIV:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                f.write("   lw t0, 0(sp)\n")
                f.write("   li t2, 4\n")
                f.write("   sub sp, sp, t2\n")
                f.write("   lw t1, 0(sp)\n")
                f.write("   sub sp, sp, t2\n")
                # fuga
            
            elif node.node_type == NodeType.ND_NUM:
                f.write(f"   li t0, {node.val}\n")
                f.write("   sw t0, 0(sp)\n")
                f.write("   li t0, 4\n")
                f.write("   addi sp, sp, 4\n")
            
            else:
                sys.exit(1)
        
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
