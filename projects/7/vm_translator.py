#!/usr/bin/env python3
import sys
from vm_parser import Parser
from vm_code_writer import CodeWriter
from pathlib import Path

def main() -> None:
    # 引数のチェック（スクリプト名自身も含まれるため len は 1 以上）
    if len(sys.argv) < 2:
        print("使用方法: python3 vm_translator.py ProgName.vm")
        sys.exit(1)

    vm_file_path = sys.argv[1]
    if "." not in vm_file_path:
        raise RuntimeError(f"入力ファイル名が不正です: {vm_file_path}")
        
    asm_file_path = Path(vm_file_path.split(".")[0] + ".asm")
    code_writer = CodeWriter(asm_file_path)
    try:
        parser = Parser(vm_file_path)
        while parser.has_more_lines̶():
            parser.advance̶()
            command_type = parser.command_type()
            if command_type == "C_PUSH" or command_type == "C_POP":
                code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2())
            elif command_type == "C_ARITHMETIC":
                code_writer.write_arithmetic(parser.arg1())
            else:
                raise RuntimeError(f"サポート外のコマンドです: {command_type}")
    finally:
        code_writer.close()


if __name__ == "__main__":
    main()