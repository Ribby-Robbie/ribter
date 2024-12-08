class Token:

    def __init__(self, token_type, lexeme, literal, line):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        """
        Converts the token type, lexeme, and literal all into one string

        Returns
        -------
        :return token_string: a string telling the token type, lexeme, and literal
        """
        literal_str = "null" if self.literal is None else str(self.literal)
        return f"{self.token_type} {self.lexeme} {literal_str}"

    def __repr__(self):
        """
        Converts itself to a string to serve as a representation

        Returns
        -------
        :return self_string: a string of self, whatever is passed
        """
        return str(self)
