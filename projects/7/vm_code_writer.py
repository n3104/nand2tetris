#!/usr/bin/env python3

from pathlib import Path

class CodeWriter:

    def __init__(self, file_path: Path, encoding: str = "utf-8"):
        self._f_out = file_path.open("w", encoding="utf-8")
        f_out = self._f_out
        self._label_num = 0
        f_out.write(f"// set stack base address\n")
        f_out.write(f"@256\n")
        f_out.write(f"D=A\n")
        f_out.write(f"@SP\n")
        f_out.write(f"M=D\n")

    def write_arithmetic(self, command: str) -> None:
        f_out = self._f_out
        if command in ["add", "sub", "and", "or"]:
            self._write_binary_op(command)
        elif command == "neg":
            f_out.write(f"// neg\n")
            # 1つ手前の値にマイナスをかける。SPの変更は不要
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=-M\n")
        elif command == "eq":
            f_out.write(f"// eq\n")
            # まず2つ手前の値をデータレジスタに乗せる
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"A=A-1\n")
            f_out.write(f"D=M\n")
            # 1つ手前の値と演算できるようにアドレスを進める
            f_out.write(f"A=A+1\n")
            f_out.write(f"D=D-M\n") # ここだけ違う
            # 演算結果を2つ手前のアドレスに保存する
            f_out.write(f"A=A-1\n")
            f_out.write(f"M=D\n")
            # 最後にSPを1つ減らす
            f_out.write(f"@SP\n")
            f_out.write(f"M=M-1\n")
            # 1つ手前の値で判定する。SPの変更は不要
            self._label_num += 1
            label_num = self._label_num
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"D=M\n")
            f_out.write(f"@JEQ_{label_num}\n")
            f_out.write(f"D;JEQ\n")
            # false
            f_out.write(f"@0\n") # false
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            f_out.write(f"@JEQ_{label_num}_END\n")
            f_out.write(f"0;JMP\n")
            # true
            f_out.write(f"(JEQ_{label_num})\n")
            f_out.write(f"@0\n") # true
            f_out.write(f"A=A-1\n") # @-1 は掛けないのでマイナス1する
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            # end
            f_out.write(f"(JEQ_{label_num}_END)\n")
        elif command == "gt":
            f_out.write(f"// gt\n")
            # まず2つ手前の値をデータレジスタに乗せる
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"A=A-1\n")
            f_out.write(f"D=M\n")
            # 1つ手前の値と演算できるようにアドレスを進める
            f_out.write(f"A=A+1\n")
            f_out.write(f"D=D-M\n") # ここだけ違う
            # 演算結果を2つ手前のアドレスに保存する
            f_out.write(f"A=A-1\n")
            f_out.write(f"M=D\n")
            # 最後にSPを1つ減らす
            f_out.write(f"@SP\n")
            f_out.write(f"M=M-1\n")
            # 1つ手前の値で判定する。SPの変更は不要
            self._label_num += 1
            label_num = self._label_num
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"D=M\n")
            f_out.write(f"@JGT_{label_num}\n")
            f_out.write(f"D;JGT\n")
            # false
            f_out.write(f"@0\n") # false
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            f_out.write(f"@JGT_{label_num}_END\n")
            f_out.write(f"0;JMP\n")
            # true
            f_out.write(f"(JGT_{label_num})\n")
            f_out.write(f"@0\n") # true
            f_out.write(f"A=A-1\n") # @-1 は掛けないのでマイナス1する
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            # end
            f_out.write(f"(JGT_{label_num}_END)\n")
        elif command == "lt":
            f_out.write(f"// lt\n")
            # まず2つ手前の値をデータレジスタに乗せる
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"A=A-1\n")
            f_out.write(f"D=M\n")
            # 1つ手前の値と演算できるようにアドレスを進める
            f_out.write(f"A=A+1\n")
            f_out.write(f"D=D-M\n") # ここだけ違う
            # 演算結果を2つ手前のアドレスに保存する
            f_out.write(f"A=A-1\n")
            f_out.write(f"M=D\n")
            # 最後にSPを1つ減らす
            f_out.write(f"@SP\n")
            f_out.write(f"M=M-1\n")
            # 1つ手前の値で判定する。SPの変更は不要
            self._label_num += 1
            label_num = self._label_num
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"D=M\n")
            f_out.write(f"@JLT_{label_num}\n")
            f_out.write(f"D;JLT\n")
            # false
            f_out.write(f"@0\n") # false
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            f_out.write(f"@JLT_{label_num}_END\n")
            f_out.write(f"0;JMP\n")
            # true
            f_out.write(f"(JLT_{label_num})\n")
            f_out.write(f"@0\n") # true
            f_out.write(f"A=A-1\n") # @-1 は掛けないのでマイナス1する
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=D\n")
            # end
            f_out.write(f"(JLT_{label_num}_END)\n")
        elif command == "not":
            f_out.write(f"// not\n")
            # 1つ手前の値をNotする。SPの変更は不要
            f_out.write(f"@SP\n")
            f_out.write(f"A=M-1\n")
            f_out.write(f"M=!M\n")
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

    def _write_binary_op(self, command: str) -> None:
        f_out = self._f_out
        if command == "add":
            op = "D=D+M"
        elif command == "sub":
            op = "D=D-M"
        elif command == "and":
            op = "D=D&M"
        elif command == "or":
            op = "D=D|M"
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

        f_out.write(f"// {command}\n")
        # まず2つ手前の値をデータレジスタに乗せる
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"A=A-1\n")
        f_out.write(f"D=M\n")
        # 1つ手前の値と演算できるようにアドレスを進める
        f_out.write(f"A=A+1\n")
        f_out.write(f"{op}\n") # ここだけ違う
        # 演算結果を2つ手前のアドレスに保存する
        f_out.write(f"A=A-1\n")
        f_out.write(f"M=D\n")
        # 最後にSPを1つ減らす
        f_out.write(f"@SP\n")
        f_out.write(f"M=M-1\n")

    def write_push_pop(self, command: str, segment:str, index: int) -> None:
        f_out = self._f_out
        if command == "C_PUSH":
            f_out.write(f"// push {segment} {index}\n")
            if segment == "constant":
                f_out.write(f"@{index}\n")
                f_out.write(f"D=A\n")
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"M=D\n")
                f_out.write(f"@SP\n")
                f_out.write(f"M=M+1\n")
                return
        elif command == "C_POP":
            return
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

    def close(self) -> None:
        # 最後に無限ループを入れておく
        f_out = self._f_out
        f_out.write(f"// END loop\n")
        f_out.write(f"(END)\n")
        f_out.write(f"@END\n")
        f_out.write(f"0;JMP") # 最終行は改行コードを入れない
        return self._f_out.close()