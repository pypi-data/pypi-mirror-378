from rply import LexerGenerator, ParserGenerator
import regex

class Rex:
    def __init__(self, block: str):
        self._build_lexer()
        self._build_parser()

        tokens = self.lexer.lex(block)
        self.pattern = self.parser.parse(tokens)

    def _build_lexer(self):
        rules = {
            "STRING":    r"'[^']*'",
            "NUMBER":    r"\d+",
            "OR":        r"(?i)or",
            "AND":       r"(?i)and",
            "SEMICOLON": r";",

            # constants
            "ALPHANUM":  r"_ALPHANUM",
        }

        lg = LexerGenerator()
        for name, pattern in rules.items():
            lg.add(name, pattern)

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

        # Unified statement handler
        def statement(p, x):
            tok_type = p[0].gettokentype()
            match tok_type:
                case "STRING":
                    text = p[0].getstr()[1:-1]
                case "_ALPHANUM":
                    text = r"[A-Za-z0-9]"
            count = int(p[1].getstr()) if x == 2 else 1
            return f"(?:{text}){{{count}}}"


        pg.production("statement : STRING NUMBER")(lambda p: statement(p, len(p)))
        pg.production("statement : STRING")(lambda p: statement(p, len(p)))


        pg.production("statement : ALPHANUM NUMBER")(lambda p: statement(p, len(p)))
        pg.production("statement : ALPHANUM")(lambda p: statement(p, len(p)))

        self.parser = pg.build()

    def exists(self, block: str):
        return bool(regex.fullmatch(self.pattern, block))


if __name__ == '__main__':

    code = """

        'negro' 3;


    """
    x = Rex(code)
    print(x.exists("negronegronegro "))
