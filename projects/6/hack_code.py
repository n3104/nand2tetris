#!/usr/bin/env python3

from pathlib import Path
from typing import Dict

class Code:

    DESTS: Dict[str, str] = {
        "M": "001",
        "D": "010",
        "DM": "011",
        "A": "100",
        "AM": "110",
        "ADM": "111",
    }    

    @classmethod
    def dest(cls, dest:str) -> str:
        """dest ニーモニックのバイナリコードを返す。"""
        if dest is None:
            return "000"

        bin = cls.DESTS.get(dest)
        if bin is None:
            raise RuntimeError(f"不正なdestです: {dest}")

        return bin

    COMPS: Dict[str, str] = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001101",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
    }    

    @classmethod
    def comp(cls, comp:str) -> str:
        """comp ニーモニックのバイナリコードを返す。"""
        bin = cls.COMPS.get(comp)
        if bin is None:
            raise RuntimeError(f"不正なcompです: {comp}")

        return bin

    JUMPS: Dict[str, str] = {
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }    

    @classmethod
    def jump(cls, jump:str) -> str:
        """jump ニーモニックのバイナリコードを返す。"""
        if jump is None:
            return "000"

        bin = cls.JUMPS.get(jump)
        if bin is None:
            raise RuntimeError(f"不正なjumpです: {jump}")

        return bin
