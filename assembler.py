import sys
from utils import strtol, find_label

class Assembler():
    REGISTER_MAP = {"zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "000100", "t0": "00101",
                    "t1": "00110", "t2": "00111", "fp": "01000", "s0": "01000", "s1": "01001", "a0": "01010",
                    "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110", "a5": "01111", "a6": "10000",
                    "a7": "10001", "s2": "10010", "s3": "10011", "s4": "10100", "s5": "10101", "s6": "10110",
                    "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100",
                    "t4": "11101", "t5": "11110", "t6": "11111"}
    
    def __init__(self) -> None:
        pass

    @staticmethod
    def _imm_to_bin(imm: str, width) -> str:
        imm = int(imm)
        if imm < 0:
            imm = (1 << width) + imm
        return f"{imm:0{width}b}"
    
    @staticmethod
    def _r_instruction(rd: str, rs1: str, rs2: str, funct3: str, funct7: str) -> str:
        return f"{funct7}{Assembler.REGISTER_MAP[rs2]}{Assembler.REGISTER_MAP[rs1]}{funct3}{Assembler.REGISTER_MAP[rd]}0110011"
    
    @staticmethod
    def _i_instruction(opcode: str, rd: str, rs1: str, imm: str, funct3: str) -> str:
        imm = Assembler._imm_to_bin(imm, 12)
        return f"{imm}{Assembler.REGISTER_MAP[rs1]}{funct3}{Assembler.REGISTER_MAP[rd]}{opcode}"
    
    @staticmethod
    def _arithmetic_instruction(rd: str, rs1: str, imm: str, funct3: str) -> str:
        return Assembler._i_instruction("0010011", rd, rs1, imm, funct3)
    
    @staticmethod
    def _load_instruction(rd: str, rs1: str, imm: str, funct3: str) -> str:
        return Assembler._i_instruction("0000011", rd, rs1, imm, funct3)
    
    @staticmethod
    def _jalr_instruction(rd: str, rs1: str, imm: str) -> str:
        return Assembler._i_instruction("1100111", rd, rs1, imm, "000")
    
    @staticmethod
    def _s_instruction(rs2: str, rs1: str, imm: str, funct3: str) -> str:
        imm = Assembler._imm_to_bin(imm, 12)
        return f"{imm[:7]}{Assembler.REGISTER_MAP[rs2]}{Assembler.REGISTER_MAP[rs1]}{funct3}{imm[7:]}0100011"
    
    @staticmethod
    def _b_instruction(rs1: str, rs2: str, imm: str, funct3: str) -> str:
        imm = Assembler._imm_to_bin(imm, 12)
        return f"{imm[0]}{imm[2:8]}{Assembler.REGISTER_MAP[rs2]}{Assembler.REGISTER_MAP[rs1]}{funct3}{imm[8:]}{imm[1]}1100011"
    
    @staticmethod
    def _u_instruction(opcode: str, rd: str, imm: str) -> str:
        imm = Assembler._imm_to_bin(imm, 20)
        return f"{imm}{Assembler.REGISTER_MAP[rd]}{opcode}"
    
    @staticmethod
    def _lui_instruction(rd: str, imm: str) -> str:
        return Assembler._u_instruction("0110111", rd, imm)
    
    @staticmethod
    def _auipc_instruction(rd: str, imm: str) -> str:
        return Assembler._u_instruction("0010111", rd, imm)
    
    @staticmethod
    def _j_instruction(rd: str, imm: str) -> str:
        imm = Assembler._imm_to_bin(imm, 20)
        return f"{imm[0]}{imm[10:]}{imm[9]}{imm[1:9]}{Assembler.REGISTER_MAP[rd]}1101111"
    
    @staticmethod
    def _jal_instruction(rd: str, imm: str) -> str:
        return Assembler._j_instruction(rd, imm)

    @staticmethod
    def _calc_offset(label: str, lines: list[str], i: int) -> str:
        if label.isdigit():
            offset = label
        
        else:
            idx = find_label(label, lines)
            offset = str((idx - i)*4)
        
        return offset

    def assemble(self, file_path: str) -> None:
        with open("out.bin", "bw") as out:
            pass
        
        f = open(file_path, "r")
        lines = f.readlines()
        lines = [line.split() for line in lines]
        lines = [line for line in lines if len(line) > 0]
        for i in range(len(lines)):
            for j in range(len(lines[i])):
                lines[i][j] = lines[i][j].replace(",", "")

        for i, toks in enumerate(lines):
            bin = ""
            if len(toks) == 0:
                continue
            if toks[0] == "main:":
                continue
            
            elif toks[0] == "addi":
                bin = Assembler._arithmetic_instruction(toks[1], toks[2], toks[3], "000")
            
            elif toks[0] == "ori":
                bin = Assembler._arithmetic_instruction(toks[1], toks[2], toks[3], "110")
            
            elif toks[0] == "add":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "000", "0000000")
            
            elif toks[0] == "sub":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "000", "0100000")
            
            elif toks[0] == "slt":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "010", "0000000")
            
            elif toks[0] == "sltu":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "011", "0000000")
            
            elif toks[0] == "xor":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "100", "0000000")
            
            elif toks[0] == "or":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "110", "0000000")
            
            elif toks[0] == "lui":
                bin = Assembler._lui_instruction(toks[1], toks[2])
            
            elif toks[0] == "lw":
                imm, val_len = strtol(toks[2])
                rest = toks[2][val_len:]
                rs1 = rest.replace("(", "").replace(")", "")
                bin = Assembler._load_instruction(toks[1], rs1, imm, "010")
            
            elif toks[0] == "sw":
                imm, val_len = strtol(toks[2])
                rest = toks[2][val_len:]
                rs1 = rest.replace("(", "").replace(")", "")
                bin = Assembler._s_instruction(toks[1], rs1, imm, "010")
            
            # M-extension
            elif toks[0] == "mul":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "000", "0000001")
            
            elif toks[0] == "div":
                bin = Assembler._r_instruction(toks[1], toks[2], toks[3], "100", "0000001")
            
            # pseudo instructions
            elif toks[0] == "li":
                bin = Assembler._arithmetic_instruction(toks[1], "zero", toks[2], "000")
            
            elif toks[0] == "mv":
                bin = Assembler._arithmetic_instruction(toks[1], toks[2], "0", "000")

            elif toks[0] == "seqz":
                bin = Assembler._arithmetic_instruction(toks[1], "zero", "1", "011")
            
            elif toks[0] == "snez":
                bin = Assembler._r_instruction(toks[1], "zero", toks[2], "010", "0000000")
            
            elif toks[0] == "beqz":
                offset = Assembler._calc_offset(toks[2], lines, i)
                bin = Assembler._b_instruction("zero", toks[1], offset, "000")
            
            elif toks[0] == "j":
                offset = Assembler._calc_offset(toks[1], lines, i)
                bin = Assembler._j_instruction("zero", offset)

            elif toks[0] == "ret":
                continue

            else:
                if toks[0][-1] == ":":
                    continue

                else:
                    print(f"Unknown instruction: {toks[0]}", file=sys.stderr)
                    sys.exit(1)

            if len(bin) > 0:
                out = open("out.bin", "ba")
                out.write(int(bin, 2).to_bytes(len(bin) // 8, byteorder="big"))
                out.close()
                



if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("The given number of arguments is invalid.", file=sys.stderr)
        sys.exit(1)

    linker = Assembler()
    linker.assemble(args[1])