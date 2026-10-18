#!/usr/bin/env python3

from pathlib import Path

class JackTokenizer:

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.file_path}")


        # コメントを除去する
        lines = file_path.read_text(encoding).splitlines()
        lines = self._filter_api_and_muliti_line_comments(lines)
        lines = self._filter_line_comment_and_blank_lines(lines)

        self._lines = lines
        self._lines_index = 0
        if self._has_more_lines̶():
            self._current_line = lines[0] # 先頭行を入れておく
        else:
            self._current_line = None
        self._current_line_index = 0
        self._current_token = None
        self._current_token_type = None

    def _filter_api_and_muliti_line_comments(self, lines: list) -> list:
        filtered_lines = []
        if len(lines) <= 0:
            return filtered_lines

        finding_end = False
        lines_index = 0
        line = lines[0]
        while True:
            if finding_end != True:
                # コメントの開始文字列を探す
                index = line.find("/*")
                if index >= 0:
                    # コメントの開始前の文字列を追加し、てコメントの開始後の文字列で再度処理をする
                    filtered_lines.append(line[:index])
                    line = line[index+2:]
                    finding_end = True
                    continue
                else:
                    # コメントに関係しない文字列を追加する
                    filtered_lines.append(line)
            else:
                # コメントの終了文字列を探す
                index = line.find("*/")
                if index >= 0:
                    # コメントの終了後の文字列で再度処理をする
                    line = line[index+2:]
                    finding_end = False
                    continue

            # 処理対象の行を進める。最終行に達した場合は処理を終了する
            lines_index += 1
            if lines_index >= len(lines):
                break
            line = lines[lines_index]

        return filtered_lines

    def _filter_line_comment_and_blank_lines(self, lines: list) -> list:
        filtered_lines = []
        for line in lines:
            # 行コメント部分を除去
            code_part = line.split("//")[0]
            # 空白と改行コードを取り除いて空行かどうか判定
            cleaned_line = code_part.strip()
            
            # 空行とコメントならループを継続し、次の行へ進む
            if not cleaned_line:
                continue
            else:
                filtered_lines.append(cleaned_line)

        return filtered_lines

    def has_more_tokens(self) -> bool:
        # 最終行に到達後に複数回呼び出されること考慮して最初に判定を入れておく
        if self._has_more_lines̶() == False:
            return False

        # 現在行が最終文字の場合は次の行に進める。その上で次の行が存在する確認する
        if self._current_line_index >= len(self._current_line):
            self._lines_index += 1
            if self._has_more_lines̶() == False:
                # 最終行に到達した場合はトークンをNoneにしておく
                self._current_token = None
                self._current_token_type = None
                return False
            else:
                # 現在行を次の行に進める
                self._current_line = self._lines[self._lines_index]
                self._current_line_index = 0

        return True

    def _has_more_lines̶(self) -> bool:
        return self._lines_index < len(self._lines)

    SYMBOLS: frozenset[str] = frozenset({"{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"})
    KEY_WORDS: frozenset[str] = frozenset({"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"})

    def advance̶(self) -> None:
        # EOF (ファイル末尾) に達した場合
        if self.has_more_tokens() == False:
            return

        line = self._current_line
        line_index = self._current_line_index
        start = line_index
        end = line_index+1
        while True:
            token = line[start:end]
            if token == " ":
                # 半角スペースの場合
                # 半角スペースはトークンではなくトークン間のデリミタなので半角スペース以外の文字が見つかるまでstartとendを進める。returnしない
                while True:
                    start += 1
                    end += 1
                    token = line[start:end]
                    if token == " ":
                        continue
                    else:
                        break
                # lineはstrip済みなので半角スペースがある場合は必ず次のtokenが存在するのでendが文字列の突き抜ける考慮は不要
                continue
            elif token in JackTokenizer.SYMBOLS:
                # SYMBOLの場合
                # SYMBOLはすべて1文字なので一致すればSYMBOLとみなせる
                self._current_token = token
                self._current_token_type = "SYMBOL"
                self._current_line_index = end
                return
            elif token == '"':
                # STRING_CONSTの場合
                # 前後が""で囲まれているので、次の”が見つかればトークンの終了とみなせる
                sub_start = start + 1
                sub_end = end + 1
                while True:
                    token = line[sub_start:sub_end]
                    if token == '"':
                        self._current_token = line[start+1:sub_start]
                        self._current_token_type = "STRING_CONST"
                        self._current_line_index = sub_end
                        return
                    else:
                        sub_start += 1
                        sub_end += 1
            elif token.isdecimal():
                # INT_CONSTの場合
                # 数字以外の文字に切り替わる、もしくは行末まで進めばトークンの終了とみなせる
                sub_start = start + 1
                sub_end = end + 1
                while True:
                    # INT_CONSTが行の最後のトークンの場合
                    if sub_end > len(line):
                        self._current_token = line[start:sub_start]
                        self._current_token_type = "INT_CONST"
                        self._current_line_index = sub_end
                        return

                    token = line[sub_start:sub_end]
                    if token.isdecimal():
                        sub_start += 1
                        sub_end += 1
                    else:
                        # 数字以外なので別のトークンに切り替わったことを意味する
                        self._current_token = line[start:sub_start]
                        self._current_token_type = "INT_CONST"
                        self._current_line_index = sub_start
                        return
            else:
                # KEYWORDもしくはIDENTIFIERの場合
                # SYMBOLもしくは半角スペースに切り替わる、もしくは行末まで進めばトークンの終了とみなせる。"は対象外でいいはず
                sub_start = start + 1
                sub_end = end + 1
                while True:
                    # このがトークンが行の最後のトークンの場合
                    if sub_end > len(line):
                        self._current_token = line[start:sub_start]
                        if self._current_token in JackTokenizer.KEY_WORDS:
                            self._current_token_type = "KEYWORD"
                        else:
                            self._current_token_type = "IDENTIFIER"
                        self._current_line_index = sub_end
                        return

                    token = line[sub_start:sub_end]
                    if token == " " or token in JackTokenizer.SYMBOLS:
                        # SYMBOLもしくは半角スペース別のトークンに切り替わったことを意味する
                        self._current_token = line[start:sub_start]
                        if self._current_token in JackTokenizer.KEY_WORDS:
                            self._current_token_type = "KEYWORD"
                        else:
                            self._current_token_type = "IDENTIFIER"
                        self._current_line_index = sub_start
                        return
                    else:
                        sub_start += 1
                        sub_end += 1
            
    def token_type(self) -> str:
        return self._current_token_type

    def key_word(self) -> str:
         if self._current_token_type != "KEYWORD":
             raise RuntimeError(f"KEYWORDではありません: {self._current_token_type}")
 
         return self._current_token.upper()
 
    def symbol(self) -> str:
        if self._current_token_type != "SYMBOL":
            raise RuntimeError(f"SYMBOLではありません: {self._current_token_type}")

        return self._current_token

    def identifier(self) -> str:
        if self._current_token_type != "IDENTIFIER":
            raise RuntimeError(f"IDENTIFIERではありません: {self._current_token_type}")

        return self._current_token

    def int_val(self) -> int:
        if self._current_token_type != "INT_CONST":
            raise RuntimeError(f"INT_CONSTではありません: {self._current_token_type}")

        return int(self._current_token)

    def string_val(self) -> str:
        if self._current_token_type != "STRING_CONST":
            raise RuntimeError(f"STRING_CONSTではありません: {self._current_token_type}")

        return self._current_token
