from r_token import Token
from r_environment import Rib
import r_utils as utils


class Scanner:
    def __init__(self, source):
        # Source meaning a source file
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.errors = []

    @staticmethod
    def error(line, error):
        """
        Appends an error to the error list

        Parameters
        ----------
        :param line: the line the error is at
        :param error: the message to be appended to the error list
        """
        Rib.report(line, "", error)

    def isAtEnd(self) -> bool:
        """
        Tells us if we have consumed all of our characters in the source file

        Returns
        -------
        :return end_bool: tells us if we are at the end of our characters
        """
        return self.current >= len(self.source)

    def advance(self):
        """
        Consumes the next character in the source file

        Returns
        -------
        :return next_source_char: the next character in the source file
        """
        self.current += 1
        return self.source[self.current - 1]

    def match(self, expected):
        """
        Sees if the next token in the source is a match to what we expect

        Parameters
        :param expected: the expected token we expect to come next and are looking for

        Returns
        -------
        :return found: if we found the expected token or if we reached the EOF
        """
        if self.isAtEnd():
            return False
        elif self.source[self.current] != expected:
            return False
        else:
            self.current += 1
            return True

    def peek(self):
        """
        Peeks ahead without consuming the next token, looks to see if we are at the end of the file or a new line

        Returns
        -------
        :return peek: tells the next character
        """
        if self.isAtEnd():
            return None
        else:
            # Want to look ahead, so we do self.current instead of self.current - 1
            return self.source[self.current]

    def peekNext(self):
        """
        A module for the few times we need to peek after the previous peek, but can't use a for or while loop

        Returns
        -------
        :return peek_next: tells the character after the next
        """
        if self.current + 1 >= len(self.source):
            return None
        else:
            return self.source[self.current + 1]

    def string(self):
        """
        A module used to see if we have a completed string, and if that string is complete what the literal is
        """
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == "\n":
                self.line += 1

            self.advance()

        if self.isAtEnd():
            self.error(self.line, "Unterminated string.")
            # Want to return out, so we don't try to overreach our source file
            return

        # Want to consume the closing "
        self.advance()

        # Get the text, but trim the surrounding quotes to be added to the literal
        string_value = self.source[self.start + 1:self.current - 1]
        self.addToken("STRING", string_value)

    def number(self):
        while utils.isDigit(self.peek()) or (self.peek() == '.' and utils.isDigit(self.peekNext())):
            # used to consume the '.' for a float
            self.advance()

        number_value = float(self.source[self.start:self.current])
        self.addToken("NUMBER", number_value)

    def identifier(self):
        keywords = {
            "and": "AND",
            "class": "CLASS",
            "else": "ELSE",
            "false": "FALSE",
            "for": "FOR",
            "fun": "FUN",
            "if": "IF",
            "nil": "NIL",
            "or": "OR",
            "print": "PRINT",
            "return": "RETURN",
            "super": "SUPER",
            "this": "THIS",
            "true": "TRUE",
            "var": "VAR",
            "while": "WHILE"
        }

        while utils.isAlphaNumeric(self.peek()):
            self.advance()

        token_text = self.source[self.start:self.current]

        # If a token isn't a special keyword, or any of that other stuff, then it is an identifier
        try:
            token_type = keywords[token_text]
        except KeyError:
            token_type = "IDENTIFIER"

        self.addToken(token_type)

    def addToken(self, token_type: str, literal=None):
        """
        Adding information about the token to the token list. It grabs the text of the current lexeme and creates a
        new token for it.

        :param token_type: The type of token that is then getting appended to the token list
        :param literal: An expression like an identifier, string, or number
        """
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def scanAToken(self):
        """
        Gets the token from the token dictionary.
        Adds them to the token list or do some other special cases
        """
        tokens = {
            "(": "LEFT_PAREN",
            ")": "RIGHT_PAREN",
            "{": "LEFT_BRACE",
            "}": "RIGHT_BRACE",
            "*": "STAR",
            ".": "DOT",
            ",": "COMMA",
            "+": "PLUS",
            "-": "MINUS",
            ";": "SEMICOLON",
            "=": "EQUAL",
            "!": "BANG",
            "<": "LESS",
            ">": "GREATER",
            "/": "SLASH",
            " ": "SPACE",
            "\t": "TAB",
            "\n": "NEW_LINE",
            "\"": "STRING",
        }
        char = self.advance()
        # Because of this loop, ensures we won't ever get a KeyError
        for key in tokens.keys():
            if char == key:
                # A couple of cases where there are double tokens together
                if key == "=" and self.match("="):
                    self.addToken("EQUAL_EQUAL")
                elif key == "!" and self.match("="):
                    self.addToken("BANG_EQUAL")
                elif key == "<" and self.match("="):
                    self.addToken("LESS_EQUAL")
                elif key == ">" and self.match("="):
                    self.addToken("GREATER_EQUAL")
                elif key == "\"":
                    self.string()
                elif key == "/" and self.match("/"):
                    # We want to make sure that '//' are seen as comments
                    # Nothing is tokenized after them for that line
                    # Also want to ensure we aren't at EOF, so we don't try to go beyond
                    while (self.peek() is not (None or '\n')) and not self.isAtEnd():
                        self.advance()

                # Cases that involve white space
                elif key in [" ", "\t"]:
                    # If there is any white space, we don't want to tokenize anything
                    # Just break and continue onto the next char
                    break
                elif key == "\n":
                    # New line, want to increase the line number by 1
                    self.line += 1
                else:
                    self.addToken(tokens[key])

                break
        else:
            if utils.isDigit(char):
                self.number()
            elif utils.isAlpha(char):
                self.identifier()
            else:
                self.error(self.line, f"Unexpected character: {char}")

    def scanTokens(self):
        """
        Works its way through the source code, adding tokens until it runs out of characters.
        Then it appends one final 'END OF FILE' token.

        Returns
        -------
        :return tokens: a list of all the tokens
        :return errors: a list of all errors that occurred
        """
        while not self.isAtEnd():
            # We are starting at the beginning of the next lexeme
            self.start = self.current
            self.scanAToken()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens, self.errors
