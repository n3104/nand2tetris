#!/usr/bin/env python3

import html
from jack_tokenizer import JackTokenizer
from typing import TextIO
from pathlib import Path

class CompilationEngine:

    def __init__(self, input_file_path: Path, output_file_path: Path):
        self._tokenizer = JackTokenizer(input_file_path)
        self._f_out = output_file_path.open("w", encoding="utf-8")
        self._current_token = None
        self._current_token_type = None
        self._indent = ""

    def compile_class(self) -> None:
        self._print_with_indent("<class>")
        self._advance_tokenizer()
        self._increment_indent()
        # 'class' className '{' classVarDec * subroutineDec * '}'
        self._process("class")
        self._process() # className
        self._process("{")
        while True:
            token = self._current_token
            if token in ["field", "static"]:
                self._compile_class_var_dec()
            elif token in ["constructor", "function", "method"]:
                self._compile_subroutine()
            else:
                break

        self._process("}")
        self._decrement_indent()
        self._print_with_indent("</class>")
        self._f_out.close()

    def _compile_class_var_dec(self) -> None:
        self._print_with_indent("<classVarDec>")
        self._increment_indent()
        # ( 'static' | 'field' ) type varName (',' varName) * ';'
        self._process() # ('static' | 'field')
        self._process() # type
        self._process() # varName
        while True:
            #  (',' varName) * ';'
            token = self._current_token
            if token == ",":
                self._process() # ,
                self._process() # varName
            elif token == ";":
                self._process() # ;
                break
            else:
                raise RuntimeError(f"syntax error 想定外のtokenです: token = {token}")

        self._decrement_indent()
        self._print_with_indent("</classVarDec>")

    def _compile_subroutine(self) -> None:
        self._print_with_indent("<subroutineDec>")
        self._increment_indent()
        # ( 'constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self._process() # ('constructor' | 'function' | 'method')
        self._process() # ('void' | type)
        self._process() # subroutineName
        self._process("(")
        self._compile_parameter_list()
        self._process(")")
        self._compile_subroutine_body()
        self._decrement_indent()
        self._print_with_indent("</subroutineDec>")

    def _compile_parameter_list(self) -> None:
        self._print_with_indent("<parameterList>")
        self._increment_indent()
        while True:
            # ( (type varName) (',' type varName) * ) ?
            token = self._current_token
            if token == ")":
                break

            if token == ",":
                self._process(",")
            self._process() # type
            self._process() # varName

        self._decrement_indent()
        self._print_with_indent("</parameterList>")

    def _compile_subroutine_body(self) -> None:
        self._print_with_indent("<subroutineBody>")
        self._increment_indent()
        self._process("{")
        while True:
            # '{' varDec* statements '}'
            token = self._current_token
            if token == "var":
                self._compile_var_dec()
            else:
                self._compile_statements()
                break

        self._process("}")
        self._decrement_indent()
        self._print_with_indent("</subroutineBody>")

    def _compile_var_dec(self) -> None:
        self._print_with_indent("<varDec>")
        self._increment_indent()
        self._process("var")
        self._process() # type
        self._process() # varName
        while True:
            #  (',' varName) * ';'
            token = self._current_token
            if token == ",":
                self._process() # ,
                self._process() # varName
            elif token == ";":
                self._process() # ;
                break
            else:
                raise RuntimeError(f"syntax error 想定外のtokenです: token = {token}")

        self._decrement_indent()
        self._print_with_indent("</varDec>")

    def _compile_statements(self) -> None:
        self._print_with_indent("<statements>")
        self._increment_indent()
        while True:
            # statement *
            token = self._current_token
            if token == "let":
                self._compile_let()
            elif token == "if":
                self._compile_if()
            elif token == "while":
                self._compile_while()
            elif token == "do":
                self._compile_do()
            elif token == "return":
                self._compile_return()
            else:
                break

        self._decrement_indent()
        self._print_with_indent("</statements>")

    def _compile_let(self) -> None:
        self._print_with_indent("<letStatement>")
        self._increment_indent()
        # 'let' varName ('[' expression ']' ) ? '=' expression ';'
        self._process("let")
        self._process() # varName
        token = self._current_token
        if token == "[":
            self._process("[")
            self._compile_expression()
            self._process("]")
        self._process("=")
        self._compile_expression()
        self._process(";")
        self._decrement_indent()
        self._print_with_indent("</letStatement>")

    def _compile_if(self) -> None:
        self._print_with_indent("<ifStatement>")
        self._increment_indent()
        # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' ) ?
        self._process("if")
        self._process("(")
        self._compile_expression()
        self._process(")")
        self._process("{")
        self._compile_statements()
        self._process("}")
        token = self._current_token
        if token == "else":
            self._process("else")
            self._process("{")
            self._compile_statements()
            self._process("}")
        self._decrement_indent()
        self._print_with_indent("</ifStatement>")

    def _compile_while(self) -> None:
        self._print_with_indent("<whileStatement>")
        self._increment_indent()
        # 'while' '(' expression ')' '{' statements '}'
        self._process("while")
        self._process("(")
        self._compile_expression()
        self._process(")")
        self._process("{")
        self._compile_statements()
        self._process("}")
        self._decrement_indent()
        self._print_with_indent("</whileStatement>")

    def _compile_do(self) -> None:
        self._print_with_indent("<doStatement>")
        self._increment_indent()
        # 'do' subroutineCall ';'
        self._process("do")
        # subroutineCall: subroutineName '(' expressionList ')' | ( className | varName) '.' subroutineName'(' expressionList ')'
        token = self._current_token
        self._process() # subroutineName | className | varName
        token = self._current_token
        if token == "(":
            # subroutineName '(' expressionList ')'
            self._process("(")
            self._compile_expression_list()
            self._process(")")
        elif token == ".":
            # ( className | varName) '.' subroutineName'(' expressionList ')'
            self._process(".")
            self._process() # subroutineName
            self._process("(")
            self._compile_expression_list()
            self._process(")")
        else:
            raise RuntimeError(f"syntax error 想定外のtokenです: token = {token}")

        self._process(";")
        self._decrement_indent()
        self._print_with_indent("</doStatement>")

    def _compile_return(self) -> None:
        self._print_with_indent("<returnStatement>")
        self._increment_indent()
        # 'return' expression ? ';'
        self._process("return")
        token = self._current_token
        if token != ";":
            self._compile_expression()
        self._process(";")
        self._decrement_indent()
        self._print_with_indent("</returnStatement>")

    def _compile_expression(self) -> None:
        self._print_with_indent("<expression>")
        self._increment_indent()
        # term (op term) *
        self._compile_term()
        while True:
            # (op term) *
            token = self._current_token
            if token in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
                self._process() # op
                self._compile_term()
            else:
                break

        self._decrement_indent()
        self._print_with_indent("</expression>")

    def _compile_term(self) -> None:
        self._print_with_indent("<term>")
        self._increment_indent()

        # integerConstant | stringConstant | keywordConstant | varName |
        # varName '[' expression ']' | '(' expression ')' | (unaryOp term) | subroutineCall
        # subroutineCall: subroutineName '(' expressionList ')' | ( className | varName) '.' subroutineName'(' expressionList ')'
        token = self._current_token
        if token == "(":
            # '(' expression ')'
            self._process("(")
            self._compile_expression()
            self._process(")")
        elif token in ["-", "~"]:
            # (unaryOp term)
            self._process() # unaryOp
            self._compile_term()
        else:
            self._process() # integerConstant | stringConstant | keywordConstant | varName | subroutineName | className
            token = self._current_token
            if token == "[":
                # varName '[' expression ']'
                self._process("[")
                self._compile_expression()
                self._process("]")
            elif token == "(":
                # subroutineName '(' expressionList ')'
                self._process("(")
                self._compile_expression_list()
                self._process(")")
            elif token == ".":
                # ( className | varName) '.' subroutineName'(' expressionList ')'
                self._process(".")
                self._process() # subroutineName
                self._process("(")
                self._compile_expression_list()
                self._process(")")
            else:
                # 上の記号以外のケースはそれでtermが終わりという意味になるので何もしない
                pass

        self._decrement_indent()
        self._print_with_indent("</term>")

    def _compile_expression_list(self) -> None:
        self._print_with_indent("<expressionList>")
        self._increment_indent()
        while True:
            # (expression ( ',' expression) *)?
            token = self._current_token
            if token == ")":
                break

            if token == ",":
                self._process(",")
            self._compile_expression()

        self._decrement_indent()
        self._print_with_indent("</expressionList>")

    def _advance_tokenizer(self) -> None:
        tokenizer = self._tokenizer
        if tokenizer.has_more_tokens() == False:
            # 次のトークンがないということは、jackファイルの処理が完了したという意味
            self._current_token = None
            self._current_token_type = None
            return

        tokenizer.advance̶()
        token_type = tokenizer.token_type()
        if token_type == "KEYWORD":
            token = tokenizer.key_word().lower()
        elif token_type == "SYMBOL":
            token = tokenizer.symbol()
        elif token_type == "IDENTIFIER":
            token = tokenizer.identifier()
        elif token_type == "INT_CONST":
            token = str(tokenizer.int_val())
        elif token_type == "STRING_CONST":
            token = tokenizer.string_val()
        else:
            raise RuntimeError(f"サポート外のtoken_typeです: {token_type}")

        self._current_token = token
        self._current_token_type = token_type

    def _process(self, token: str = None) -> None:
        if token is None:
            token = self._current_token
        if (self._current_token == token):
            self._print_xml_token(token)
        else:
            raise RuntimeError(f"syntax error tokenが一致しません: self._current_token = {self._current_token}, token = {token}")

        self._advance_tokenizer()

    def _print_xml_token(self, token: str) -> None:
        token_type = self._current_token_type
        if token_type == "KEYWORD":
            self._print_with_indent(f"<keyword> {token} </keyword>")
        elif token_type == "SYMBOL":
            self._print_with_indent(f"<symbol> {html.escape(token)} </symbol>")
        elif token_type == "IDENTIFIER":
            self._print_with_indent(f"<identifier> {token} </identifier>")
        elif token_type == "INT_CONST":
            self._print_with_indent(f"<integerConstant> {token} </integerConstant>")
        elif token_type == "STRING_CONST":
            self._print_with_indent(f"<stringConstant> {html.escape(token)} </stringConstant>")
        else:
            raise RuntimeError(f"サポート外のtoken_typeです: {token_type}")

    def _increment_indent(self) -> None:
        self._indent += "  "

    def _decrement_indent(self) -> None:
        self._indent = self._indent[:-2]

    def _print_with_indent(self, message: str) -> None:
        f_out = self._f_out
        indent = self._indent
        f_out.write(f"{indent}{message}\n")
