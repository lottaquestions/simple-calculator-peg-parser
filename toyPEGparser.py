from enum import Enum
from re import Scanner

class TokenType(Enum):
    NAME = "Name"
    NUMBER = "Number"
    IF = "if"
    COLON = ":"
    EQUAL = "="
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"

class Node:
    def __init__(self, type, children):
        self.type = type
        self.children = children
class Token:
  type = ''
  string = ''
  def __init__(self, type, string):
    self.type = type
    self.string = string
  def __str__(self):
    return "(\""+self.type+"\", \""+self.string+"\")"

class Tokenizer:
    def __init__(self, tokengen):
        """Call with tokenize.generate_tokens(...)."""
        self.tokengen = tokengen
        self.tokens = []
        self.pos = 0
    def mark(self):
        return self.pos
    def reset(self, pos):
        self.pos = pos
    def get_token(self):
        token = self.peek_token()
        self.pos += 1
        return token
    def peek_token(self):
        if self.pos == len(self.tokens):
            self.tokens.append(next(self.tokengen))
        return self.tokens[self.pos]

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer    
    def mark(self):
        return self.tokenizer.mark()
    def reset(self, pos):
        self.tokenizer.reset(pos)
    def expect(self, arg):
        token = self.tokenizer.peek_token()
        if token.type == arg or token.string == arg:
            return self.tokenizer.get_token()
        return None

class ToyParser(Parser):
    def __init__(self, tokenizer):
        super().__init__(tokenizer)

    def statement(self):
        if a := self.assignment():
            return a
        if e := self.expr():
            return e
        if i := self.if_statement():
            return i
        return None
    
    def assignment(self):
        if target := self.expect(TokenType.NAME):
            if eql := self.expect(TokenType.EQUAL):
                if exprn := self.expr():
                    return Node("assign", target, eql, exprn)
        return None

    
    def if_statement(self):
        if token_if := self.expect(TokenType.IF):
            if e := self.statement():
                if TokenType.COLON:
                    if s := self.statement():
                        return Node("if", [e,s])
        return None


    
    def expr(self):
        if t := self.term():
            pos = self.mark()
            if op := self.expect("+"):
                if e := self.expr():
                    return Node("add", [t, e])
            self.reset(pos)
            if op := self.expect("-"):
                if e := self.expr():
                    return Node("sub", [t, e])
            self.reset(pos)
            return t
        return None
    
    def term(self):
        if (a := self.atom()):
            pos = self.mark()
            if op := self.expect("*"):
                if t := self.term():
                    return Node("mul", [a, t])
            self.reset(pos)
            if op := self.expect("/"):
                if t := self.term():
                    return Node("div", [a, t])
            self.reset(pos)
            return a
        return None 

    def atom(self):
        if token := self.expect(TokenType.NAME):
            return token
        if token := self.expect(TokenType.NUMBER):
            return token
        pos = self.mark()
        if self.expect("("):
            if e := self.expr():
                if self.expect(")"):
                    return e
        self.reset(pos)
        return None
    

if __name__ == "__main__" :
    scanner = Scanner([
        (r"[0-9]+", lambda scanner, token:Token(TokenType.NUMBER, token)),
        (r"[a-zA-Z_]+", lambda scanner, token:Token(TokenType.NAME, token)),
        (r"=", lambda scanner, token:Token(TokenType.EQUAL, token)),
        (r"\+", lambda scanner, token:Token(TokenType.PLUS, token)),
        (r"\-", lambda scanner, token:Token(TokenType.MINUS, token)),
        (r"\*", lambda scanner, token:Token(TokenType.MULT, token)),
        (r"/", lambda scanner, token:Token(TokenType.DIV, token)),
        (r":", lambda scanner, token:Token(TokenType.COLON, token)),
        (r"if", lambda scanner, token:Token(TokenType.IF,token)),
        (r"\s+", None), # None == skip token.
    ])
    sample_python = "answer = 1 + 2"
    scanner_results, remainder = scanner.scan(sample_python)
    tokengen = iter(scanner_results)
    tokenizer = Tokenizer(tokengen=tokengen)
    parser = ToyParser(tokenizer)
    parse_result= parser.statement()