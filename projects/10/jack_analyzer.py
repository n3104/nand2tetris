#!/usr/bin/env python3
import html
import sys
import time
from jack_tokenizer import JackTokenizer
from pathlib import Path

def main() -> None:
    # 引数のチェック（スクリプト名自身も含まれるため len は 1 以上）
    if len(sys.argv) < 2:
        print("使用方法: python3 jack_analyzer.py source")
        sys.exit(1)

    jack_file_path = Path(sys.argv[1])
    if not jack_file_path.exists():
        print("パスが存在しません")
        raise RuntimeError(f"パスが存在しません: {jack_file_path}")
    elif jack_file_path.is_file():
        if jack_file_path.suffix != ".jack":
            raise RuntimeError(f"Jackファイルではありません: {jack_file_path}")
        jack_files = [jack_file_path]
    elif jack_file_path.is_dir():
        jack_files = list(jack_file_path.glob("*.jack"))

    out_dir_path = Path(str(int(time.time())))
    out_dir_path.mkdir(parents=True, exist_ok=True)
    for jack_file_path in jack_files:
        token_file_path = Path(out_dir_path, jack_file_path.stem + "T.xml")
        with token_file_path.open("w", encoding="utf-8") as f_out:
            tokenizer = JackTokenizer(jack_file_path)
            f_out.write(f"<tokens>\n")
            while tokenizer.has_more_tokens():
                tokenizer.advance̶()
                token_type = tokenizer.token_type()
                if token_type == "KEYWORD":
                    f_out.write(f"<keyword> {tokenizer.key_word().lower()} </keyword>\n")
                elif token_type == "SYMBOL":
                    f_out.write(f"<symbol> {html.escape(tokenizer.symbol())} </symbol>\n")
                elif token_type == "IDENTIFIER":
                    f_out.write(f"<identifier> {tokenizer.identifier()} </identifier>\n")
                elif token_type == "INT_CONST":
                    f_out.write(f"<integerConstant> {tokenizer.int_val()} </integerConstant>\n")
                elif token_type == "STRING_CONST":
                    f_out.write(f"<stringConstant> {html.escape(tokenizer.string_val())} </stringConstant>\n")
                else:
                    raise RuntimeError(f"サポート外のtoken_typeです: {token_type}")

            f_out.write(f"</tokens>\n")


if __name__ == "__main__":
    main()