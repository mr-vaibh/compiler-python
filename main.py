import re

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.current_pos = 0

    def tokenize(self):
        token_specification = [
            ('NUMBER',   r'\d+'),          # Integer
            ('PLUS',     r'\+'),           # Addition
            ('MINUS',    r'-'),            # Subtraction
            ('TIMES',    r'\*'),           # Multiplication
            ('DIVIDE',   r'/'),            # Division
            ('LPAREN',   r'\('),           # Left Parenthesis
            ('RPAREN',   r'\)'),           # Right Parenthesis
            ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
            ('MISMATCH', r'.'),             # Any other character
        ]

        tok_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
        line_num = 1
        line_start = 0

        for match in re.finditer(tok_regex, self.source):
            kind = match.lastgroup
            value = match.group()

            if kind == 'NUMBER':
                self.tokens.append(('NUMBER', int(value)))
            elif kind == 'PLUS':
                self.tokens.append(('PLUS', value))
            elif kind == 'MINUS':
                self.tokens.append(('MINUS', value))
            elif kind == 'TIMES':
                self.tokens.append(('TIMES', value))
            elif kind == 'DIVIDE':
                self.tokens.append(('DIVIDE', value))
            elif kind == 'LPAREN':
                self.tokens.append(('LPAREN', value))
            elif kind == 'RPAREN':
                self.tokens.append(('RPAREN', value))
            elif kind == 'SKIP':
                continue
            else:
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')

        self.tokens.append(('EOF', None))  # End of file
        return self.tokens

class ASTNode:
    pass

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(ASTNode):
    def __init__(self, value):
        self.value = value

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.expr()

    def expr(self):
        node = self.term()

        while self.current_token()[0] in ('PLUS', 'MINUS'):
            token = self.current_token()
            self.pos += 1
            node = BinOp(left=node, op=token[1], right=self.term())

        return node

    def term(self):
        node = self.factor()

        while self.current_token()[0] in ('TIMES', 'DIVIDE'):
            token = self.current_token()
            self.pos += 1
            node = BinOp(left=node, op=token[1], right=self.factor())

        return node

    def factor(self):
        token = self.current_token()
        if token[0] == 'NUMBER':
            self.pos += 1
            return Num(value=token[1])
        elif token[0] == 'LPAREN':
            self.pos += 1
            node = self.expr()
            if self.current_token()[0] != 'RPAREN':
                raise RuntimeError('Expected )')
            self.pos += 1
            return node
        else:
            raise RuntimeError('Expected NUMBER or LPAREN')

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)

class Interpreter:
    def visit(self, node):
        if isinstance(node, Num):
            return node.value
        elif isinstance(node, BinOp):
            if node.op == '+':
                return self.visit(node.left) + self.visit(node.right)
            elif node.op == '-':
                return self.visit(node.left) - self.visit(node.right)
            elif node.op == '*':
                return self.visit(node.left) * self.visit(node.right)
            elif node.op == '/':
                return self.visit(node.left) / self.visit(node.right)

def interpret(source):
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    return interpreter.visit(ast)

if __name__ == '__main__':
    source = "3 + 5 * (10 - 4)"
    result = interpret(source)
    print("Result:", result)  # Output: Result: 33
