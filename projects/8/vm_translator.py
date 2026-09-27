#!/usr/bin/env python3
import sys
from vm_parser import Parser
from vm_code_writer import CodeWriter
from pathlib import Path

def main() -> None:
    # 引数のチェック（スクリプト名自身も含まれるため len は 1 以上）
    if len(sys.argv) < 2:
        print("使用方法: python3 vm_translator.py ProgName.vm or Prog folder")
        sys.exit(1)

    vm_file_path = Path(sys.argv[1])
    if not vm_file_path.exists():
        print("パスが存在しません")
        raise RuntimeError(f"パスが存在しません: {vm_file_path}")
    elif vm_file_path.is_file():
        if vm_file_path.suffix != ".vm":
            raise RuntimeError(f"VMファイルではありません: {vm_file_path}")
        asm_file_path = Path(vm_file_path.parent, vm_file_path.stem + ".asm")
        vm_files = [vm_file_path]
    elif vm_file_path.is_dir():
        asm_file_path = Path(vm_file_path, vm_file_path.name + ".asm")
        vm_files = list(vm_file_path.glob("*.vm"))

    code_writer = CodeWriter(asm_file_path)
    try:
        for vm_file_path in vm_files:
            parser = Parser(vm_file_path)
            code_writer.set_file_name(vm_file_path.name)
            while parser.has_more_lines̶():
                parser.advance̶()
                command_type = parser.command_type()
                if command_type in ["C_PUSH", "C_POP"]:
                    code_writer.write_push_pop(command_type, parser.arg1(), parser.arg2())
                elif command_type == "C_ARITHMETIC":
                    code_writer.write_arithmetic(parser.arg1())
                elif command_type == "C_LABEL":
                    code_writer.write_label(parser.arg1())
                elif command_type == "C_GOTO":
                    code_writer.write_goto(parser.arg1())
                elif command_type == "C_IF":
                    code_writer.write_if(parser.arg1())
                elif command_type == "C_FUNCTION":
                    code_writer.write_function(parser.arg1(), int(parser.arg2()))
                elif command_type == "C_RETURN":
                    code_writer.write_return()
                else:
                    raise RuntimeError(f"サポート外のコマンドです: {command_type}")
    finally:
        code_writer.close()


if __name__ == "__main__":
    main()