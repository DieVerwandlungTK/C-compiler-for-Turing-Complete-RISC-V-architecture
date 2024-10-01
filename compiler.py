import sys
from tokenizer import Tokenizer
from syntax_tree import Parser, Node, NodeType

class Compiler():
    """ C compiler class

    This class compiles the given syntax tree into a RISC-V assembly code.

    Attributes:
        file_name (str): The name of the file to write the assembly code.

    """

    def __init__(self, parser: Parser) -> None:
        """ Initialize the compiler class

        Args:
            file_path (str): The name of the file to write the assembly code.
        
        Returns:
            None: This function does not return anything.

        """

        self.parser = parser
    
    def compile(self, file_path: str) -> None:
        """ Compile the given syntax tree into a RISC-V assembly code

        Args:
            node (Node): The root node of the syntax tree.
        
        Returns:
            None: This function does not return anything.

        """

        f = open(file_path, "w")   # Flush the file
        f.close()

        f = open(file_path, "a")
        f.write("main:\n")
        f.write("   lui t0, 16\n")
        f.write("   add sp, sp, t0\n")
        f.write("   add fp, fp, t0\n")
        f.write(f"   lw t0,  {(self.parser.lvar_offsets[-1]//16 + 1)*16}\n")
        f.write(f"   sub sp, sp, t0\n")
        f.write("\n")

        def _pop_operands() -> None:
            """ Pop the operands from the stack

            This function pops the operands from the stack and stores them in the t0 and t1 registers.

            Args:
                None: This function does not take any arguments.
            
            Returns:
                None: This function does not return anything.

            """

            f.write("   lw t0, 0(sp)\n")
            f.write("   lw t1, 16(sp)\n")
            f.write("   addi sp, sp, 32\n")
        
        def _push_result() -> None:
            """ Push the result to the stack

            This function pushes the t0 register's value to the stack.

            Be careful that this function overwrite the t1 register.

            Args:
                None: This function does not take any arguments.
            
            Returns:
                None: This function does not return anything.

            """

            f.write("   li t1, 16\n")
            f.write("   sub sp, sp, t1\n")
            f.write("   sw t0, 0(sp)\n")
        
        def _gen_lval(node: Node) -> None:
            if node.node_type != NodeType.ND_LVAR:
                sys.exit(1)
            f.write(f"   li t0, {node.offset}\n")
            f.write("   sub t0, fp, t0\n")
            _push_result()
            f.write("\n")

        def _gen(node: Node) -> None:
            """ Recursively compile the syntax tree

            This function recursively compiles the syntax tree.

            Args:
                node (Node): The current node to compile.
            
            Returns:
                None: This function does not return anything.

            """

            if node.node_type == NodeType.ND_NUM:
                f.write(f"   li t0, {node.val}\n")
                _push_result()
                f.write("\n")

                return None
                
            elif node.node_type == NodeType.ND_LVAR:
                _gen_lval(node)
                f.write("   lw t0, 0(sp)\n")
                f.write("   lw t0, 0(t0)\n")
                f.write("   sw t0, 0(sp)\n")
                f.write("\n")

                return None
            
            elif node.node_type == NodeType.ND_ASSIGN:
                _gen_lval(node.lhs)
                _gen(node.rhs)
                _pop_operands()
                f.write("   sw t0, 0(t1)\n")
                _push_result()
                f.write("\n")

                return None
            
            elif node.node_type == NodeType.ND_RETURN:
                _gen(node.lhs)
                f.write("   lw a0, 0(sp)\n")
                f.write("   addi sp, sp, 16\n")
                f.write("   mv sp, fp\n")
                f.write("   lw fp, 0(sp)\n")
                f.write("   addi sp, sp, 16\n")
                f.write("   ret\n")
                f.write("\n")

                return None
            
            elif node.node_type == NodeType.ND_IF:
                _gen(node.cond)
                f.write("   lw t0, 0(sp)\n")
                f.write("   addi sp, sp, 16\n")

                if node.els:
                    f.write(f"   beqz t0, {node.labels[1]}\n")
                    _gen(node.then)
                    f.write(f"   j {node.labels[0]}\n")
                    f.write("\n")
                    f.write(f"{node.labels[1]}:\n")
                    _gen(node.els)

                else:
                    f.write(f"   beqz t0, {node.labels[0]}\n")
                    _gen(node.then)

                f.write(f"{node.labels[0]}:\n")
                return None
            
            _gen(node.lhs)      # Generate the left node
            _gen(node.rhs)      # Generate the right node
            _pop_operands()     # Pop the operands from the stack
            # left node is in t1, right node is in t0

            if node.node_type == NodeType.ND_ADD:         
                f.write("   add t0, t1, t0\n")  # Add the operands

            elif node.node_type == NodeType.ND_SUB:
                f.write("   sub t0, t1, t0\n")
            
            elif node.node_type == NodeType.ND_MUL:
                f.write("   mul t0, t1, t0\n")
            
            elif node.node_type == NodeType.ND_DIV:
                f.write("   div t0, t1, t0\n")
            
            elif node.node_type == NodeType.ND_EQ:
                f.write("   xor t0, t1, t0\n")
                f.write("   seqz t0, t0\n")
            
            elif node.node_type == NodeType.ND_NEQ:
                f.write("   xor t0, t1, t0\n")
                f.write("   snez t0, t0\n")

            elif node.node_type == NodeType.ND_LT:
                f.write("   slt t0, t1, t0\n")
            
            elif node.node_type == NodeType.ND_LE:
                f.write("   slt t2, t1, t0\n")  # t2 = t1 < t0
                f.write("   xor t3, t1, t0\n")  # t3 = t0 ^ t1
                f.write("   seqz t3, t3\n")     # t3 = t3 == 0
                f.write("   or t0, t2, t3\n")   # t0 = t2 || t3
            
            else:
                sys.exit(1)

            _push_result()      # Push the result to the stack
            f.write("\n")

            return None
            
        for node in self.parser.code:
            _gen(node)
            f.write("   lw a0, 0(sp)\n")
            f.write("   addi sp, sp, 16\n")
            f.write("\n")
        
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
    compiler = Compiler(parser)
    compiler.compile(args[2])
