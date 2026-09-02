#!/usr/bin/env python3

from pathlib import Path

class Parser:

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        self.file_path = Path(file_path)
        self.encoding = encoding

        if not self.file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.file_path}")
        
        self._file_obj = open(self.file_path, "r", encoding=self.encoding)
        self._current_line = None
        self._peeked_line = None

    def has_more_lines̶(self) -> bool:
        """次の行が存在するか確認する（ポインタは進めない）"""
        return self._peek() is not None

    def _peek(self) -> str:
        """次の行の内容をプレビューする（ポインタは進めない）"""
        if self._peeked_line is None:
            # まだ先読みバッファが空なら、次の行を読み込んでバッファに保持
            self._peeked_line = self._seek_next()
            
        # EOF（ファイル末尾）に達していたら None を返す
        if self._peeked_line == "":
            return None
            
        return self._peeked_line

    def _seek_next(self) -> None:
        """次の行の命令行を取得する（空白とコメントはスキップする）"""
        while True:
            line = self._file_obj.readline()
            
            # EOF (ファイル末尾) に達した場合
            if line == "":
                return ""

            # コメント部分を除去
            code_part = line.split("//")[0]
            # 空白と改行コードを取り除いて空行かどうか判定
            cleaned_line = code_part.strip()
            
            # 空行とコメントならループを継続し、次の行へ進む
            if not cleaned_line:
                continue

            # 命令行が見つかったら返す
            return cleaned_line

    def advance̶(self) -> None:
        """実際に1行読み込んでポインタを進める"""
        if self._peeked_line is not None:
            # 先読みバッファに値があれば、それを消費してバッファをクリア
            self._current_line = self._peeked_line
            self._peeked_line = None
            return
        
        # has_more_lines̶ が true の場合のみ呼び出すべき命令なので、バッファになければ現在行を None にする
        self._current_line = None

    def instruction_type(self) -> str:
        """現在の命令のタイプを返す"""
        instruction = self._current_line
        if instruction.startswith("@"):
            return "A_INSTRUCTION"
        elif instruction.startswith("("):
            return "L_INSTRUCTION"
        else:
            return "C_INSTRUCTION"

    def symbol(self) -> str:
        """現在の命令のシンボルを返す"""
        instruction_type = self.instruction_type()
        instruction = self._current_line
        if instruction_type == "A_INSTRUCTION":
            return instruction.strip("@")
        elif instruction_type == "L_INSTRUCTION":
            return instruction.strip("()")
        else:
            raise RuntimeError(f"C命令のためsymbolを抽出できません: {instruction_type}")

    def dest(self) -> str:
        """現在の C 命令の dest 部分を返す。dest が省略されている場合は None を返す。"""
        instruction_type = self.instruction_type()
        if instruction_type != "C_INSTRUCTION":
            raise RuntimeError(f"C命令ではありません: {instruction_type}")

        instruction = self._current_line
        if "=" in instruction:
            return instruction.split("=")[0].strip()
        else:
            return None

    def comp(self) -> str:
        """現在の C 命令の comp 部分を返す。"""
        instruction_type = self.instruction_type()
        if instruction_type != "C_INSTRUCTION":
            raise RuntimeError(f"C命令ではありません: {instruction_type}")

        instruction = self._current_line
        # destが存在する場合dest部分を除去する
        if "=" in instruction:
            instruction = instruction.split("=")[1].strip()
        # jumpが存在する場合jump部分を除去する
        if ";" in instruction:
            instruction = instruction.split(";")[0].strip()

        return instruction

    def jump(self) -> str:
        """現在の C 命令の jump 部分を返す。"""
        instruction_type = self.instruction_type()
        if instruction_type != "C_INSTRUCTION":
            raise RuntimeError(f"C命令ではありません: {instruction_type}")

        instruction = self._current_line
        if ";" in instruction:
            return instruction.split(";")[1].strip()
        else:
            return None
