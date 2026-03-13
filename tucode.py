DIGITS = "0123456789"

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"

class Token:
  def __init__(self, type_, value):
    self.type = type_
    self.value = value

  def __repr__(self):
    return f"Token({self.type}, {self.value})"

class Lexer:
  def __init__(self, text):
    self.text = text
    self.pos = 0

  def current_char(self):
    return self.text[self.pos] if self.pos < len(self.text) else None

  def advance(self):
    self.pos += 1

  def skip_whitespace(self):
    while self.current_char() is not None and self.current_char() in " \t":
      self.advance()

  def make_number(self):
    digit_str = ""
    dot_count = 0
    while self.current_char() is not None and self.current_char() in DIGITS:
      digit_str += self.current_char()
      self.advance()
    if self.current_char() is not None and self.current_char() == ".":
      dot_count += 1
      digit_str += self.current_char()
      self.advance()
    while self.current_char() is not None and self.current_char() in DIGITS:
      digit_str += self.current_char()
      self.advance()
    if dot_count == 1:
      return Token(TT_FLOAT, float(digit_str))
    return Token(TT_INT, int(digit_str))

  def make_tokens(self):
    tokens = []
    while self.current_char() is not None:
      if self.current_char() in DIGITS:
        tokens.append(self.make_number())
      elif self.current_char() == "+":
        tokens.append(Token(TT_PLUS, "+"))
        self.advance()
      elif self.current_char() == "-":
        tokens.append(Token(TT_MINUS, "-"))
        self.advance()
      elif self.current_char() == "*":
        tokens.append(Token(TT_MUL, "*"))
        self.advance()
      elif self.current_char() == "/":
        tokens.append(Token(TT_DIV, "/"))
        self.advance()
      elif self.current_char() == "(":
        tokens.append(Token(TT_LPAREN, "("))
        self.advance()
      elif self.current_char() == ")":
        tokens.append(Token(TT_RPAREN, ")"))
        self.advance()
      elif self.current_char() in " \t":
        self.skip_whitespace()
    return tokens

class NumberNode:
  def __init__(self, token):
    self.token = token

  def __repr__(self):
    return f"NumberNode({self.token})"

class BinOpNode:
  def __init__(self, left, op_token, right):
    self.left = left
    self.op_token = op_token
    self.right = right

  def __repr__(self):
    return f"BinOpNode({self.left}, {self.op_token}, {self.right})"
  
class UnaryOpNode:
  def __init__(self, op_token, node):
    self.op_token = op_token
    self.node = node

  def __repr__(self):
    return f"UnaryOpNode({self.op_token}, {self.node})"

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0

  def current_token(self):
    return self.tokens[self.pos] if self.pos < len(self.tokens) else None

  def advance(self):
    self.pos += 1

  def parse_factor(self):
    token = self.current_token()
    if token.type == TT_MINUS:
      self.advance()
      return UnaryOpNode(token.type, self.parse_factor())
    elif token.type == TT_LPAREN:
      self.advance()
      result = self.parse_expr()
      self.advance()
      return result
    self.advance()
    return NumberNode(token)
  
  def parse_term(self):
    left = self.parse_factor()
    while self.current_token() is not None:
      if self.current_token().type in (TT_MUL, TT_DIV):
        op_token = self.current_token()
        self.advance()
        right = self.parse_factor()
        left = BinOpNode(left, op_token, right)
      else:
        break
    return left
  
  def parse_expr(self):
    left = self.parse_term()
    while self.current_token() is not None:
      if self.current_token().type in (TT_PLUS, TT_MINUS):
        op_token = self.current_token()
        self.advance()
        right = self.parse_term()
        left = BinOpNode(left, op_token, right)
      else:
        break
    return left

class Interpreter:
  def visit(self, node):
    if isinstance(node, NumberNode):
      return node.token.value
    elif isinstance(node, BinOpNode):
      left = self.visit(node.left)
      right = self.visit(node.right)
      if node.op_token.type == TT_PLUS:
        return left + right
      elif node.op_token.type == TT_MINUS:
        return left - right
      elif node.op_token.type == TT_MUL:
        return left * right
      elif node.op_token.type == TT_DIV:
        return left / right
      else:
        return None
    elif isinstance(node, UnaryOpNode):
      return -self.visit(node.node)

def run(text):
  lexer = Lexer(text)
  tokens = lexer.make_tokens()
  parser = Parser(tokens)
  tree = parser.parse_expr()
  interpreter = Interpreter()
  return interpreter.visit(tree)

if __name__ == "__main__":
  lexer = Lexer("42 - 7 * 8 - 7  * 4")
  tokens = lexer.make_tokens()
  parser = Parser(tokens)
  tree = parser.parse_expr()
  interpreter = Interpreter()
  print(interpreter.visit(tree))