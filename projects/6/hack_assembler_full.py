#!/usr/bin/env python3
import sys
from hack_parser import Parser
from hack_code import Code
from hack_symbol_table import SymbolTable
from pathlib import Path

def main() -> None:
    # 引数のチェック（スクリプト名自身も含まれるため len は 1 以上）
    if len(sys.argv) < 2:
        print("使用方法: python3 hack_assembler_full.py Prog.asm")
        sys.exit(1)

    asm_file_path = sys.argv[1]
    if "." not in asm_file_path:
        raise RuntimeError(f"入力ファイル名が不正です: {asm_file_path}")
        
    hack_file_path = Path(asm_file_path.split(".")[0] + ".hack")

    symbol_table = SymbolTable()

    # 第1パス
    parser = Parser(asm_file_path)
    line_number = 0
    while parser.has_more_lines̶():
        # print(f"line_number: {line_number}")
        parser.advance̶()
        instruction_type = parser.instruction_type()
        if instruction_type == "C_INSTRUCTION" or instruction_type == "A_INSTRUCTION":
            line_number += 1
        elif instruction_type == "L_INSTRUCTION":
            symbol = parser.symbol()
            if symbol_table.contains(symbol):
                raise RuntimeError(f"同じ名前のラベルシンボルが存在します: {symbol}")
            else:
                symbol_table.add_entry(symbol, line_number)

    # 第2パス
    with hack_file_path.open("w", encoding="utf-8") as f_out:
        parser = Parser(asm_file_path)
        is_first = True
        val_address = 16
        while parser.has_more_lines̶():
            # print(f"val_address={val_address}")
            parser.advance̶()
            instruction_type = parser.instruction_type()
            if instruction_type == "C_INSTRUCTION":
                bin = "111" + Code.comp(parser.comp()) + Code.dest(parser.dest()) + Code.jump(parser.jump())
            elif instruction_type == "A_INSTRUCTION":
                symbol = parser.symbol()
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if symbol_table.contains(symbol):
                        address = symbol_table.get_address(symbol)
                    else:
                        # 変数シンボルの場合、初回はシンボルテーブルに追加する
                        symbol_table.add_entry(symbol, val_address)
                        address = val_address
                        val_address +=1
                bin = "0" + f"{address:015b}"
            else:
                # ラベル命令は書き込まない
                continue

            # 最終行は改行文字を入れない
            if not is_first:
                f_out.write("\n")
            is_first = False
            f_out.write(bin)

    # シンボルテーブルのデバック出力
    # for key in sorted(symbol_table._entries):
    #     print(f"{key}: {symbol_table._entries[key]}")


if __name__ == "__main__":
    main()