DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS_DIGIT = LETTERS + "_0123456789"
KEYWORDS = ["LET"]

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EQ = "EQ"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"

class Error:
  def __init__(self, error_name, details):
    self.error_name = error_name
    self.details = details
  def __repr__(self):
    return f"{self.error_name}: {self.details}"
  
class IllegalCharError(Error):
  def __init__(self, details):
    super().__init__("Illegal Character", details)

class InvalidSyntaxError(Error):
  def __init__(self, details):
    super().__init__("Invalid Syntax", details)

class ParseResult:
  def __init__(self):
    self.node = None
    self.error = None

  def success(self, node):
    self.node = node
    return self
  
  def failure(self, error):
    self.error = error
    return self
  
  def register(self, res):
    if isinstance(res, ParseResult):
      if res.error: self.error = res.error
      return res.node
    return res

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
      elif self.current_char() == "=":
        tokens.append(Token(TT_EQ, "="))
        self.advance()
      elif self.current_char() in " \t":
        self.skip_whitespace()
      elif self.current_char() in LETTERS:
        tokens.append(self.make_identifier())
      else:
        return [], IllegalCharError(self.current_char())
    return tokens, None
  def make_identifier(self):
    word = ""
    while self.current_char() is not None and self.current_char() in LETTERS_DIGIT:
      word += self.current_char()
      self.advance()
    if word in KEYWORDS:
      return Token(TT_KEYWORD, word)
    else:
      return Token(TT_IDENTIFIER, word)
    
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
  
class VarAccessNode:
  def __init__(self, token):
    self.token = token

  def __repr__(self):
    return f"VarAccessNode({self.token})"
  
class VarAssignNode:
  def __init__(self, varname, value):
    self.varname = varname
    self.value = value
  def __repr__(self):
    return f"VarAssignNode({self.varname}, {self.value})"

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0

  def current_token(self):
    return self.tokens[self.pos] if self.pos < len(self.tokens) else None

  def advance(self):
    self.pos += 1

  def parse_factor(self):
    res = ParseResult()
    token = self.current_token()
    if token.type == TT_MINUS:
      self.advance()
      factor = res.register(self.parse_factor())
      if res.error: return res.failure(res.error)
      return res.success(UnaryOpNode(token.type, factor))
    elif token.type == TT_LPAREN:
      self.advance()
      result = res.register(self.parse_expr())
      if res.error: return res.failure(res.error)
      if self.current_token() is not None and self.current_token().type == TT_RPAREN:
        self.advance()
      else:
        return res.failure(InvalidSyntaxError("Expected \")\""))
      return res.success(result)
    if token.type in (TT_INT, TT_FLOAT):
      self.advance()
      return res.success(NumberNode(token))
    else:
      return res.failure(InvalidSyntaxError("Expected a number"))
  
  def parse_term(self):
    res = ParseResult()
    left = res.register(self.parse_factor())
    if res.error: return res.failure(res.error)
    while self.current_token() is not None:
      if self.current_token().type in (TT_MUL, TT_DIV):
        op_token = self.current_token()
        self.advance()
        right = res.register(self.parse_factor())
        if res.error: return res.failure(res.error)
        left = BinOpNode(left, op_token, right)
      else:
        break
    return res.success(left)
  
  def parse_expr(self):
    res = ParseResult()
    left = res.register(self.parse_term())
    if res.error: return res.failure(res.error)
    while self.current_token() is not None:
      if self.current_token().type in (TT_PLUS, TT_MINUS):
        op_token = self.current_token()
        self.advance()
        right = res.register(self.parse_term())
        if res.error: return res.failure(res.error)
        left = BinOpNode(left, op_token, right)
      else:
        break
    return res.success(left)

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
  if text.strip() == "": return None
  lexer = Lexer(text)
  tokens, error = lexer.make_tokens()
  if error: return error
  parser = Parser(tokens)
  result = parser.parse_expr()
  if result.error: return result.error
  tree = result.node
  interpreter = Interpreter()
  return interpreter.visit(tree)

if __name__ == "__main__":
  lexer = Lexer("42 - 7 * 8 - 7  * 4")
  tokens, error = lexer.make_tokens()
  parser = Parser(tokens)
  result = parser.parse_expr()
  tree = result.node
  interpreter = Interpreter()
  print(interpreter.visit(tree))
  error = IllegalCharError("\"@\"")
  print(error)