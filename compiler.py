import sys
from tokenizer import Tokenizer, TokenType
from syntax_tree import Parser, Node, NodeType

class Compiler():
    """ C compiler class

    This class compiles the given syntax tree into a RISC-V assembly code.

    Attributes:
        file_name (str): The name of the file to write the assembly code.

    """

    def __init__(self, file_path: str) -> None:
        """ Initialize the compiler class

        Args:
            file_path (str): The name of the file to write the assembly code.
        
        Returns:
            None: This function does not return anything.

        """

        self.file_name = file_path
    
    def compile(self, node: Node) -> None:
        """ Compile the given syntax tree into a RISC-V assembly code

        Args:
            node (Node): The root node of the syntax tree.
        
        Returns:
            None: This function does not return anything.

        """

        f = open(self.file_name, "w")   # Flush the file
        f.close()

        f = open(self.file_name, "a")
        f.write("main:\n")

        def _pop_operands() -> None:
            """ Pop the operands from the stack

            This function pops the operands from the stack and stores them in the t0 and t1 registers.

            Args:
                None: This function does not take any arguments.
            
            Returns:
                None: This function does not return anything.

            """

            f.write("   li t2, 4\n")
            f.write("   sub sp, sp, t2\n")
            f.write("   lw t0, 0(sp)\n")
            f.write("   sub sp, sp, t2\n")
            f.write("   lw t1, 0(sp)\n")
        
        def _push_result() -> None:
            """ Push the result to the stack

            This function pushes the result to the stack.

            Args:
                None: This function does not take any arguments.
            
            Returns:
                None: This function does not return anything.

            """

            f.write("   sw t0, 0(sp)\n")
            f.write("   addi sp, sp, 4\n")

        def _recursive_compile(node: Node) -> None:
            """ Recursively compile the syntax tree

            This function recursively compiles the syntax tree.

            Args:
                node (Node): The current node to compile.
            
            Returns:
                None: This function does not return anything.

            """

            if node.node_type == NodeType.ND_ADD:
                _recursive_compile(node.rhs)    # Evaluate the right-hand side
                _recursive_compile(node.lhs)    # Evaluate the right-hand side
                _pop_operands()                 # Pop the operands from the stack
                f.write("   add t0, t0, t1\n")  # Add the operands
                _push_result()                  # Push the result to the stack

            elif node.node_type == NodeType.ND_SUB:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   sub t0, t0, t1\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_MUL:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   mul t0, t0, t1\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_DIV:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   div t0, t0, t1\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_NUM:
                f.write(f"   li t0, {node.val}\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_EQ:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   xor t0, t0, t1\n")
                f.write("   seqz t0, t0\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_NEQ:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   xor t0, t0, t1\n")
                f.write("   snez t0, t0\n")
                _push_result()

            elif node.node_type == NodeType.ND_LT:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   slt t0, t0, t1\n")
                _push_result()
            
            elif node.node_type == NodeType.ND_LE:
                _recursive_compile(node.rhs)
                _recursive_compile(node.lhs)
                _pop_operands()
                f.write("   slt t2, t0, t1\n")  # t2 = t0 < t1
                f.write("   xor t3, t0, t1\n")  # t3 = t0 ^ t1
                f.write("   seqz t3, t3\n")     # t3 = t3 == 0
                f.write("   or t0, t2, t3\n")   # t0 = t2 || t3
                _push_result()
            
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
