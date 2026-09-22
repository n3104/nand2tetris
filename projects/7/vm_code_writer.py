#!/usr/bin/env python3

from pathlib import Path

class CodeWriter:

    def __init__(self, file_path: Path, encoding: str = "utf-8"):
        self._f_out = file_path.open("w", encoding="utf-8")
        f_out = self._f_out
        self._label_num = 0

    def write_arithmetic(self, command: str) -> None:
        if command in ["add", "sub", "and", "or"]:
            self._write_binary_op(command)
        elif command in ["neg", "not"]:
            self._write_unary_op(command)
        elif command in ["eq", "lt", "gt"]:
            self._write_comparison_op(command)
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

    def _write_unary_op(self, command: str) -> None:
        f_out = self._f_out
        if command == "neg":
            op = "M=-M"
        elif command == "not":
            op = "M=!M"
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

        f_out.write(f"// {command}\n")
        # 1つ手前の値を演算する。SPの変更は不要
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"{op}\n") # ここだけ違う

    def _write_comparison_op(self, command: str) -> None:
        f_out = self._f_out
        if command == "eq":
            op = "JEQ"
        elif command == "gt":
            op = "JGT"
        elif command == "lt":
            op = "JLT"
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

        f_out.write(f"// {command}\n")
        # 比較できるようにまず減算する
        self._write_binary_op("sub")
        # 1つ手前の値で判定する。SPの変更は不要
        self._label_num += 1
        label_num = self._label_num
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"D=M\n")
        f_out.write(f"@{op}_{label_num}\n")
        f_out.write(f"D;{op}\n")
        # false
        f_out.write(f"@0\n") # false
        f_out.write(f"D=A\n")
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"M=D\n")
        f_out.write(f"@{op}_{label_num}_END\n")
        f_out.write(f"0;JMP\n")
        # true
        f_out.write(f"({op}_{label_num})\n")
        f_out.write(f"@0\n") # true
        f_out.write(f"A=A-1\n") # @-1 は直接書けないのでマイナス1する
        f_out.write(f"D=A\n")
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"M=D\n")
        # end
        f_out.write(f"({op}_{label_num}_END)\n")

    def write_push_pop(self, command: str, segment:str, index: int) -> None:
        f_out = self._f_out
        if command == "C_PUSH":
            f_out.write(f"// push {segment} {index}\n")
            if segment == "constant":
                f_out.write(f"@{index}\n")
                f_out.write(f"D=A\n")
                # スタックに追加する
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"M=D\n")
                f_out.write(f"@SP\n")
                f_out.write(f"M=M+1\n")
                return
            elif segment in ["local", "argument", "this", "that", "temp"]:
                if segment == "local":
                    segment_name = "LCL"
                elif segment == "argument":
                    segment_name = "ARG"
                elif segment == "this":
                    segment_name = "THIS"
                elif segment == "that":
                    segment_name = "THAT"
                elif segment == "temp":
                    segment_name = "5" # tempの開始位置はRAM[5]固定

                f_out.write(f"@{index}\n")
                f_out.write(f"D=A\n")
                f_out.write(f"@{segment_name}\n") # ここだけ違う
                if segment == "temp":
                    f_out.write(f"A=D+A\n") # tempの場合はRAM[5]-RAM[12]固定
                else:
                    f_out.write(f"A=D+M\n")
                f_out.write(f"D=M\n")
                # スタックに追加する
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"M=D\n")
                f_out.write(f"@SP\n")
                f_out.write(f"M=M+1\n")
            else:
                raise RuntimeError(f"サポート外のセグメントです: {segment}")
        elif command == "C_POP":
            f_out.write(f"// pop {segment} {index}\n")
            if segment in ["local", "argument", "this", "that", "temp"]:
                if segment == "local":
                    segment_name = "LCL"
                elif segment == "argument":
                    segment_name = "ARG"
                elif segment == "this":
                    segment_name = "THIS"
                elif segment == "that":
                    segment_name = "THAT"
                elif segment == "temp":
                    segment_name = "5" # tempの開始位置はRAM[5]固定

                f_out.write(f"@{index}\n")
                f_out.write(f"D=A\n")
                f_out.write(f"@{segment_name}\n") # ここだけ違う
                if segment == "temp":
                    f_out.write(f"D=D+A\n") # tempの場合はRAM[5]-RAM[12]固定
                else:
                    f_out.write(f"D=D+M\n")
                # セグメントのアドレスを一旦SPの位置においておく
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"M=D\n")
                # スタックの1つ前の値をデータレジスタに入れる
                f_out.write(f"@SP\n")
                f_out.write(f"A=M-1\n")
                f_out.write(f"D=M\n")
                # 退避しておいたセグメントのアドレスに対してスタックの1つ前の値を設定する
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"A=M\n") # 退避しておいたセグメントのアドレスをAレジスタに読み込む
                f_out.write(f"M=D\n")
                # 最後にSPを1つ減らす
                f_out.write(f"@SP\n")
                f_out.write(f"M=M-1\n")
            else:
                raise RuntimeError(f"サポート外のセグメントです: {segment}")
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