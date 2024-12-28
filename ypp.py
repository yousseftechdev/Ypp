DIGITS:str      = '0123456789'

TT_INT:str      = "INT"
TT_FLOAT:str    = "FLOAT"
TT_PLUS:str     = "PLUS"
TT_MINUS:str    = "MINUS"
TT_MULTIPLY:str = "MUL"
TT_DIVIDE:str   = "DIV"
TT_LPAREN:str   = "LP"
TT_RPAREN:str   = "RP"

class Error:
    def __init__(self, posStart, posEnd, errorName, details) -> None:
        self.posStart = posStart
        self.posEnd = posEnd
        self.errorName:str = errorName
        self.details:str = details
        
    def asString(self) -> str:
        result:str = f'{self.errorName}: {self.details}'
        result += f'\nFile {self.posStart.fn}, Line {self.posEnd.ln + 1}'
        return result

class IllegalCharacter(Error):
    def __init__(self, posStart, posEnd, details):
        super().__init__(posStart, posEnd, "Illegal Character", details)

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    def advance(self, curruntChar):
        self.idx += 1
        self.col += 1
        if curruntChar == '\n':
            self.ln += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Token:
    def __init__(self, type, value = None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type} : {self.value}'
        return f'{self.type}'


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.pos.advance(self.currentChar)
        self.currentChar = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
    
    def makeTokens(self):
        tokens = []
        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumber())
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()

            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()

            elif self.currentChar == '*':
                tokens.append(Token(TT_MULTIPLY))
                self.advance()

            elif self.currentChar == '/':
                tokens.append(Token(TT_DIVIDE))
                self.advance()

            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()

            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                posStart = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharacter(posStart, self.pos, "'" + char + "'")
        return tokens, None

    def makeNumber(self):
        num = ''
        dot = False

        while self.currentChar != None and self.currentChar in DIGITS + '.':
            if self.currentChar == '.':
                if dot: break
                dot = True
                num += '.'
            else:
                num += self.currentChar
            self.advance()
            
        if not dot:
            return Token(TT_INT, int(num))
        else:
            return Token(TT_FLOAT, float(num))



class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        # self.posStart = tok.posStart
        # self.posEnd = tok.posEnd

    def __repr__(self):
        return f'{self.tok}'
    

class BinOpNode:
    def __init__(self, leftNode, opTok, rightNode):
        self.leftNode = leftNode
        self.opTok = opTok
        self.rightNode = rightNode
        # self.posStart = leftNode.posStart
        # self.posEnd = rightNode.posEnd

    def __repr__(self):
        return f'({self.leftNode}, {self.opTok}, {self.rightNode})'


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = -1
        self.advance()

    def advance(self):
        self.idx += 1
        if self.idx < len(self.tokens):
            self.currentToken = self.tokens[self.idx]

        return self.currentToken

    def parse(self):
        result = self.expr()
        return result

    def factor(self):
        tok = self.currentToken
        if tok.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(tok)
        return None

    def term(self):
        left = self.factor()
        
        while self.currentToken.type in (TT_MULTIPLY, TT_DIVIDE):
            opTok = self.currentToken
            self.advance()
            right = self.factor()
            left = BinOpNode(left, opTok, right)
        return left

    def expr(self):
        return self.binOp(self.term, (TT_PLUS, TT_MINUS))

    def binOp(self, func, ops):
        left = func()
        while self.currentToken.type in ops:
            opTok = self.currentToken
            self.advance()
            right = func()
            left = BinOpNode(left, opTok, right)
        return left


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.makeTokens()
    
    return tokens, error