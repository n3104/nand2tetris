#!/usr/bin/env python3

from pathlib import Path

class Parser:

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.file_path}")

        self._lines = file_path.read_text(encoding).splitlines()
        self._line_number = 0
        self._current_line = None

    def has_more_lines̶(self) -> bool:
        return self._line_number < len(self._lines)

    def advance̶(self) -> None:
        """次の行に進める（空白とコメントはスキップする）"""
        while True:
            # EOF (ファイル末尾) に達した場合
            if self.has_more_lines̶() == False:
                return

            line = self._lines[self._line_number]
            self._line_number += 1
            # コメント部分を除去
            code_part = line.split("//")[0]
            # 空白と改行コードを取り除いて空行かどうか判定
            cleaned_line = code_part.strip()
            
            # 空行とコメントならループを継続し、次の行へ進む
            if not cleaned_line:
                continue

            # 命令行が見つかったら現在行に設定する
            self._current_line = cleaned_line
            return

    def command_type(self) -> str:
        """現在のコマンドのタイプを返す"""
        line = self._current_line
        command = line.split()[0]
        if command == "push":
            return "C_PUSH"
        elif command == "pop":
            return "C_POP"
        elif command in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return "C_ARITHMETIC"
        elif command == "label":
            return "C_LABEL"
        elif command == "if-goto":
            return "C_IF"
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

    def arg1(self) -> str:
        """現在のコマンドの第1引数を返す"""
        command_type = self.command_type()
        line = self._current_line
        if command_type in ["C_PUSH", "C_POP", "C_LABEL", "C_IF"]:
            return line.split()[1]
        elif command_type == "C_ARITHMETIC":
            return line
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command_type}")

    def arg2(self) -> str:
        """現在のコマンドの第2引数を返す"""
        command_type = self.command_type()
        line = self._current_line
        if command_type in ["C_PUSH", "C_POP"]:
            return line.split()[2]
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command_type}")
