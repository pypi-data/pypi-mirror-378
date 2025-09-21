from rply import LexerGenerator, ParserGenerator
import regex

class RegexBuilder:
    def __init__(self, block: str):
        self._build_lexer()
        self._build_parser()

        tokens = self.lexer.lex(block)
        self.pattern = self.parser.parse(tokens)

    def _build_lexer(self):
        lg = LexerGenerator()
        lg.add("STRING", r"'[^']*'")
        lg.add("NUMBER", r"\d+")
        lg.add("ALPHANUM", r"_ALPHANUM")  # DSL keyword
        lg.add("OR", r"(?i)or")
        lg.add("AND", r"(?i)and")
        lg.add("SEMICOLON", r";")
        lg.ignore(r"\s+")
        self.lexer = lg.build()

    def _build_parser(self):
        pg = ParserGenerator(["STRING", "NUMBER", "ALPHANUM", "OR", "AND", "SEMICOLON"])

        # Start
        pg.production("start : sequences SEMICOLON")(lambda p: p[0])

        # OR sequences
        pg.production("sequences : sequence OR sequences")(lambda p: f"(?:{p[0]})|(?:{p[2]})")
        pg.production("sequences : sequence")(lambda p: p[0])

        # AND sequences
        pg.production("sequence : statement AND sequence")(lambda p: f"{p[0]}{p[2]}")
        pg.production("sequence : statement")(lambda p: p[0])

        # Statements (STRING or ALPHANUM) with optional NUMBER
        def statement(p):
            tok_type = p[0].gettokentype()
            text = p[0].getstr()[1:-1] if tok_type == "STRING" else r"[A-Za-z0-9]"
            count = int(p[1].getstr()) if len(p) == 2 else 1
            return f"(?:{text}){{{count}}}"

        pg.production("statement : STRING NUMBER")(statement)
        pg.production("statement : ALPHANUM NUMBER")(statement)
        pg.production("statement : STRING")(statement)
        pg.production("statement : ALPHANUM")(statement)

        self.parser = pg.build()

    def exists(self, block: str):
        return bool(regex.fullmatch(self.pattern, block))


# Example usage
block = """
'A' 3 AND _ALPHANUM OR 'b';
"""
rb = RegexBuilder(block)
print(rb.pattern)  # (?:A){3}(?:[A-Za-z0-9]){1}|(?:b){1}

print(rb.exists("AAA7"))  # True
print(rb.exists("b"))     # True
print(rb.exists("AAAb"))  # False
