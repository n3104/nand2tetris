#!/usr/bin/env python3
import sys
from hack_parser import Parser
from hack_code import Code
from pathlib import Path

def main() -> None:
    # 引数のチェック（スクリプト名自身も含まれるため len は 1 以上）
    if len(sys.argv) < 2:
        print("使用方法: python3 HackAssembler_Basic.py Prog.asm")
        sys.exit(1)

    asm_file_path = sys.argv[1]
    if "." not in asm_file_path:
        raise RuntimeError(f"入力ファイル名が不正です: {asm_file_path}")
        
    hack_file_path = Path(asm_file_path.split(".")[0] + ".hack")

    with hack_file_path.open("w", encoding="utf-8") as f_out:
        parser = Parser(asm_file_path)
        while parser.has_more_lines̶():
            bin = _assemble_next(parser)
            f_out.write(bin + "\n")

def _assemble_next(parser: Parser) -> str:
    parser.advance̶()
    instruction_type = parser.instruction_type()
    if instruction_type == "C_INSTRUCTION":
        return "111" + Code.dest(parser.dest()) + Code.comp(parser.comp()) + Code.jump(parser.jump())
    elif instruction_type == "A_INSTRUCTION":
        return "0" + f"{int(parser.symbol()):015b}"

    raise RuntimeError(f"対応していない命令タイプです: {instruction_type}")

if __name__ == "__main__":
    main()