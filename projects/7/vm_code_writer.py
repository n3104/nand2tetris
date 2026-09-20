#!/usr/bin/env python3

from pathlib import Path

class CodeWriter:

    def __init__(self, file_path: Path, encoding: str = "utf-8"):
        self._f_out = file_path.open("w", encoding="utf-8")
        f_out = self._f_out
        f_out.write(f"// set stack base address\n")
        f_out.write(f"@256\n")
        f_out.write(f"D=A\n")
        f_out.write(f"@SP\n")
        f_out.write(f"M=D\n")

    def write_arithmetic(self, command: str) -> None:
        f_out = self._f_out
        if command == "add":
            f_out.write(f"// add\n")
            f_out.write(f"@SP\n")
            f_out.write(f"M=M-1\n")
            f_out.write(f"A=M\n")
            f_out.write(f"D=M\n")
            f_out.write(f"@SP\n")
            f_out.write(f"M=M-1\n")
            f_out.write(f"A=M\n")
            f_out.write(f"M=D+M\n")
            f_out.write(f"@SP\n")
            f_out.write(f"M=M+1\n")
        else:
            raise RuntimeError(f"サポート外のコマンドです: {command}")

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