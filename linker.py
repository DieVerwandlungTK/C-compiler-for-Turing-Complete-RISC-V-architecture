import sys
from utils import strtol

REGISTER_MAP = {"zero": "00000", "ra": "00001", "sp": "00010", "t0": "00101", 
                "t1": "00110", "t2": "00111", "a0": "01010", "t3": "11100"}

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("The given number of arguments is invalid.", file=sys.stderr)
        sys.exit(1)

    with open("out.bin", "bw") as out:
        pass

    with open(args[1], "r") as f:
        for line in f:
            bin = ""
            toks = line.split()
            toks = [tok.replace(",", "") for tok in toks]
            print(toks, file=sys.stderr)
            if len(toks) == 0:
                continue

            if toks[0] == "main:":
                continue

            if toks[0] == "li":
                bin += f"{int(toks[2]):012b}"
                bin += REGISTER_MAP["zero"]
                bin += "000"
                bin += REGISTER_MAP[toks[1]]
                bin += "00100"
                bin += "11"
            
            if toks[0] == "addi":
                bin += f"{int(toks[3]):012b}"
                bin += f"{REGISTER_MAP[toks[2]]}"
                bin += "000"
                bin += REGISTER_MAP[toks[1]]
                bin += "00100"
                bin += "11"
            
            if toks[0] == "sub":
                bin += "01000"
                bin += "00"
                bin += f"{REGISTER_MAP[toks[3]]}"
                bin += f"{REGISTER_MAP[toks[2]]}"
                bin += "000"
                bin += REGISTER_MAP[toks[1]]
                bin += "01100"
                bin += "11"
            
            if toks[0] == "lw":
                n, rest = strtol(toks[2])
                bin += f"{n:012b}"
                bin += f"{REGISTER_MAP[rest.replace('(', '').replace(')', '')]}"
                bin += "010"
                bin += REGISTER_MAP[toks[1]]
                bin += "00000"
                bin += "11"
            
            if toks[0] == "sw":
                n, rest = strtol(toks[2])
                offset = f"{n:012b}"
                bin += offset[:7]
                bin += f"{REGISTER_MAP[toks[1]]}"
                bin += f"{REGISTER_MAP[rest.replace('(', '').replace(')', '')]}"
                bin += "010"
                bin += offset[7:]
                bin += "01000"
                bin += "11"

            if line == "ret":
                continue
            
            if len(bin) > 0:
                with open("out.bin", "ba") as out:
                    out.write(int(bin, 2).to_bytes(len(bin) // 8, byteorder="big"))