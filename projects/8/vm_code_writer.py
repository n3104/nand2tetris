#!/usr/bin/env python3

from pathlib import Path

class CodeWriter:

    def __init__(self, file_path: Path, encoding: str = "utf-8", with_bootstrap: bool = False):
        self._f_out = file_path.open("w", encoding="utf-8")
        f_out = self._f_out
        self._comparison_label_num = 0
        self._f_name = file_path.stem
        self._function_name = "" # functionを利用していないケースもあるので空文字列に初期化しておく
        self._ret_label_index = 0
        if with_bootstrap:
            f_out.write(f"// bootstrap\n")
            f_out.write(f"@256\n")
            f_out.write(f"D=A\n")
            f_out.write(f"@SP\n")
            f_out.write(f"M=D\n")
            # call Sys.init
            self.write_call("Sys.init", 0)

    def set_file_name(self, file_name: str) -> None:
        self._f_name = Path(file_name).stem
        self._function_name = "" # ファイルが変わったので空文字列に初期化しておく

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
        self._comparison_label_num += 1
        label_num = self._comparison_label_num
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
            elif segment in ["local", "argument", "this", "that", "temp", "pointer", "static"]:
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
                elif segment == "pointer":
                    segment_name = "3" # pointerの開始位置はRAM[3]固定
                elif segment == "static":
                    segment_name = f"{self._f_name}.{index}" # staticの場合はファイル名.iという変数シンボルを利用する

                # スタックの値を設定するセグメントのアドレスをデータレジスタに設定する
                if segment == "static": # staticの場合は変数シンボルのアドレスをそのまま使う
                    f_out.write(f"@{segment_name}\n")
                else:
                    f_out.write(f"@{index}\n")
                    f_out.write(f"D=A\n")
                    f_out.write(f"@{segment_name}\n") # まずここが違う
                    if segment in ["temp", "pointer"]: # RAMのアドレスを直接使用するセグメント
                        f_out.write(f"A=D+A\n")
                    else: # RAMのアドレスが示すメモリ上のアドレスを使用するセグメント
                        f_out.write(f"A=D+M\n")
                f_out.write(f"D=M\n")

                # スタックの先頭の値を設定し、SPを増やす
                f_out.write(f"@SP\n")
                f_out.write(f"A=M\n")
                f_out.write(f"M=D\n")
                f_out.write(f"@SP\n")
                f_out.write(f"M=M+1\n")
            else:
                raise RuntimeError(f"サポート外のセグメントです: {segment}")
        elif command == "C_POP":
            f_out.write(f"// pop {segment} {index}\n")
            if segment in ["local", "argument", "this", "that", "temp", "pointer", "static"]:
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
                elif segment == "pointer":
                    segment_name = "3" # pointerの開始位置はRAM[3]固定
                elif segment == "static":
                    segment_name = f"{self._f_name}.{index}" # staticの場合はファイル名.iという変数シンボルを利用する

                # スタックに値を追加するセグメントのアドレスをデータレジスタに設定する
                if segment == "static": # staticの場合は変数シンボルのアドレスをそのまま使う
                    f_out.write(f"@{segment_name}\n")
                    f_out.write(f"D=A\n")
                else:
                    f_out.write(f"@{index}\n")
                    f_out.write(f"D=A\n")
                    f_out.write(f"@{segment_name}\n") # まずここが違う
                    if segment in ["temp", "pointer"]: # RAMのアドレスを直接使用するセグメント
                        f_out.write(f"D=D+A\n")
                    else: # RAMのアドレスが示すメモリ上のアドレスを使用するセグメント
                        f_out.write(f"D=D+M\n")
                # データレジスタが1つだと足りないのでセグメントのアドレスを一旦R13の位置に退避しておく
                f_out.write(f"@R13\n")
                f_out.write(f"M=D\n")

                # スタックの先頭の値をデータレジスタに入れる
                f_out.write(f"@SP\n")
                f_out.write(f"A=M-1\n")
                f_out.write(f"D=M\n")
                # 退避しておいたセグメントのアドレスに対してスタックの先頭の値を設定する
                f_out.write(f"@R13\n")
                f_out.write(f"A=M\n") # 退避しておいたセグメントのアドレスをAレジスタに読み込む
                f_out.write(f"M=D\n")
                # 最後にSPを1つ減らす
                f_out.write(f"@SP\n")
                f_out.write(f"M=M-1\n")
            else:
                raise RuntimeError(f"サポート外のセグメントです: {segment}")
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

    def write_label(self, label: str) -> None:
        f_out = self._f_out
        f_out.write(f"// write label {label}\n")
        f_out.write(f"({self._function_name}${label})\n")

    def write_goto(self, label: str) -> None:
        f_out = self._f_out
        f_out.write(f"// write goto {label}\n")
        f_out.write(f"@{self._function_name}${label}\n")
        f_out.write(f"0;JMP\n")

    def write_if(self, label: str) -> None:
        f_out = self._f_out
        f_out.write(f"// write if {label}\n")
        # スタックの先頭の値をデータレジスタに入れる
        f_out.write(f"@SP\n")
        f_out.write(f"A=M-1\n")
        f_out.write(f"D=M\n")
        # SPを1つ減らす
        f_out.write(f"@SP\n")
        f_out.write(f"M=M-1\n")
        # false(0)でなければラベルにジャンプする
        f_out.write(f"@{self._function_name}${label}\n")
        f_out.write(f"D;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        f_out = self._f_out
        f_out.write(f"// write function {function_name} {n_vars}\n")
        self._function_name = function_name
        self._ret_label_index = 0 # returnアドレスのシンボルのindexは関数毎に0から始まるように初期化する
        f_out.write(f"({function_name})\n")
        # ローカル変数の初期化
        for i in range(n_vars):
            f_out.write(f"@{i}\n")
            f_out.write(f"D=A\n")
            f_out.write(f"@LCL\n")
            f_out.write(f"A=D+M\n")
            f_out.write(f"M=0\n")
            # SPをインクリメントする
            f_out.write(f"@SP\n")
            f_out.write(f"M=M+1\n")

    def write_call(self, function_name: str, n_args: int) -> None:
        f_out = self._f_out

        def store_frame(segment:str, is_return_address_label: bool = False):
            f_out.write(f"// store frame {segment}\n")
            # 対象セグメントのアドレスをDレジスタに入れる
            f_out.write(f"@{segment}\n")
            if is_return_address_label:
                f_out.write(f"D=A\n") # ラベルなので直接アドレスを入れる
            else:
                f_out.write(f"D=M\n")
            # スタックに追加する
            f_out.write(f"@SP\n")
            f_out.write(f"A=M\n")
            f_out.write(f"M=D\n")
            f_out.write(f"@SP\n")
            f_out.write(f"M=M+1\n")

        f_out.write(f"// call function {function_name} {n_args}\n")
        # push returnAddress
        return_address_label = f"{self._function_name}$ret.{self._ret_label_index}"
        self._ret_label_index += 1
        store_frame(return_address_label, is_return_address_label=True)
        # push LCL
        store_frame("LCL")
        # push ARG
        store_frame("ARG")
        # push THIS
        store_frame("THIS")
        # push THAT
        store_frame("THAT")
        # ARG = SP-5-nArgs
        f_out.write(f"@5\n")
        f_out.write(f"D=A\n")
        f_out.write(f"@{n_args}\n")
        f_out.write(f"D=D+A\n")
        f_out.write(f"@SP\n")
        f_out.write(f"D=M-D\n")
        f_out.write(f"@ARG\n")
        f_out.write(f"M=D\n")
        # LCL = SP
        f_out.write(f"@SP\n")
        f_out.write(f"D=M\n")
        f_out.write(f"@LCL\n")
        f_out.write(f"M=D\n")
        # goto f
        f_out.write(f"@{function_name}\n")
        f_out.write(f"0;JMP\n")
        # (returnAddress)
        f_out.write(f"({return_address_label})\n")

    def write_return(self) -> None:
        f_out = self._f_out
        f_out.write(f"// write return\n")

        def restore_frame(segment:str, index: int):
            f_out.write(f"// restore frame {segment} {index}\n")
            f_out.write(f"@{index}\n")
            f_out.write(f"D=A\n")
            f_out.write(f"@R14\n") # frame
            f_out.write(f"A=M-D\n")
            f_out.write(f"D=M\n")
            f_out.write(f"@{segment}\n")
            f_out.write(f"M=D\n")

        # frame = LCL
        f_out.write(f"@LCL\n")
        f_out.write(f"D=M\n")
        f_out.write(f"@R14\n") # frame。R13をwrite_push_popで使用するのでR14とする
        f_out.write(f"M=D\n")
        # retAddr = *(frame - 5)
        restore_frame("R15", 5) # R15をretAddrとする
        # *ARG = pop()
        self.write_push_pop("C_POP", "argument", 0)
        # SP = ARG + 1
        f_out.write(f"@ARG\n")
        f_out.write(f"D=M+1\n")
        f_out.write(f"@SP\n")
        f_out.write(f"M=D\n")
        # THAT = *(frame - 1)
        restore_frame("THAT", 1)
        # THIS = *(frame - 2)
        restore_frame("THIS", 2)
        # ARG = *(frame - 3)
        restore_frame("ARG", 3)
        # LCL = *(frame - 4)
        restore_frame("LCL", 4)
        # goto retAddr
        f_out.write(f"@R15\n") # retAddr
        f_out.write(f"A=M\n")
        f_out.write(f"0;JMP\n")

    def close(self) -> None:
        return self._f_out.close()