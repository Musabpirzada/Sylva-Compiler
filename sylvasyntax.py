class Token:
    def __init__(self, line, type, value):
        self.line = line
        self.type = type
        self.value = value

class SyntaxAnalyzer:
    def __init__(self, tokens, symbol_table=None):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = symbol_table

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next_token(self):
        self.pos += 1
        return self.current_token()

    def expect(self, expected_type, expected_value=None):
        token = self.current_token()
        if not token:
            raise SyntaxError(f"Unexpected end of input. Expected {expected_type} {expected_value}")

        if token.type != expected_type or (expected_value and token.value != expected_value):
            expected = expected_value if expected_value else expected_type
            raise SyntaxError(f"Expected {expected} at line {token.line}, got {token.value}")

        self.pos += 1
        return token

    def match(self, expected_type, expected_value=None):
        token = self.current_token()
        if not token:
            return False
        return token.type == expected_type and (expected_value is None or token.value == expected_value)

    def analyze_statement(self):
        statement_type = self.identify_statement_type()
        if statement_type == 'declaration':
            return self.analyze_declaration()
        elif statement_type == 'if_statement':
            return self.analyze_condition()
        elif statement_type == 'for_loop':
            return self.analyze_for_loop()
        elif statement_type == 'while_loop':
            return self.analyze_while_loop()
        elif statement_type == 'function':
            return self.analyze_function_statement()
        elif statement_type == 'function_call':
            return self.analyze_function_call()
        else:
            raise SyntaxError(f"Syntax error: Unexpected statement at line {self.current_token().line}")

    def identify_statement_type(self):
        token = self.current_token()
        if token:
            if token.type == 'KEYWORD':
                if token.value == 'if':
                    return 'if_statement'
                elif token.value == 'for':
                    return 'for_loop'
                elif token.value == 'while':
                    return 'while_loop'
                elif token.value == 'func':
                    return 'function'
            elif token.type == 'DATA_TYPE':
                return 'declaration'
            elif token.type == 'IDENTIFIER':
                next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                if next_token and next_token.type == 'LEFT_PAREN':
                    return 'function_call'
        return 'unknown'

    def analyze_declaration(self):
        try:
            self.expect('DATA_TYPE')
            self.expect('IDENTIFIER')
            self.expect('ASSIGNMENT')
            if not self.expression():
                raise SyntaxError(f"Syntax Error: Invalid expression after assignment operator at line {self.current_token().line}")
            self.expect('STATEMENT_END')
            return True, "Declaration statement is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_condition(self):
        try:
            self.expect('KEYWORD', 'if')
            self.expect('LEFT_PAREN')
            self.analyze_condition_block()
            self.expect('RIGHT_PAREN')
            self.expect('COLON')
            self.expect('KEYWORD', 'then')
            self.expect('LEFT_PAREN')
            self.analyze_then_block()
            self.expect('RIGHT_PAREN')

            while self.match('KEYWORD', 'if not') or self.match('KEYWORD', 'else'):
                if self.match('KEYWORD', 'if not'):
                    self.next_token()  # Skip 'if not'
                    self.expect('LEFT_PAREN')
                    self.analyze_condition_block()
                    self.expect('RIGHT_PAREN')
                    self.expect('COLON')
                    self.expect('KEYWORD', 'then')
                    self.expect('LEFT_PAREN')
                    self.analyze_then_block()
                    self.expect('RIGHT_PAREN')
                elif self.match('KEYWORD', 'else'):
                    self.next_token()  # Skip 'else'
                    self.expect('COLON')
                    self.expect('KEYWORD', 'then')
                    self.expect('LEFT_PAREN')
                    self.analyze_then_block()
                    self.expect('RIGHT_PAREN')

            self.expect('STATEMENT_END')
            return True, "Conditional statement is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_assignment(self):
        try:
            self.expect('IDENTIFIER')
            self.expect('ASSIGNMENT')
            self.expression()
            self.expect('STATEMENT_END')
            return True, "Assignment statement is correct"
        except SyntaxError as e:
            return False, f"Syntax Error: {str(e)}"

    def expression(self):
        valid_types = ['NUMERIC_LITERAL', 'ARITHMETIC_OPERATOR', 'FLOAT_LITERAL', 'COMPARISON', 'STRING_LITERAL', 'BOOL_LITERAL', 'IDENTIFIER']
        if self.current_token() and self.current_token().type in valid_types:
            self.pos += 1
            while self.current_token() and self.current_token().type in valid_types:
                self.pos += 1
            return True
        else:
            raise SyntaxError(f"Syntax error: Invalid expression at line {self.current_token().line}")

    def skip_to_statement_end(self):
        while self.current_token() and self.current_token().type != 'STATEMENT_END':
            self.next_token()
        self.next_token()  # Skip the STATEMENT_END

    def parse(self):
        results = []
        while self.pos < len(self.tokens):
            statement_type = self.identify_statement_type()
            if statement_type == 'declaration':
                result, message = self.analyze_declaration()
            elif statement_type == 'if_statement':
                result, message = self.analyze_condition()
            elif statement_type == 'for_loop':
                result, message = self.analyze_for_loop()
            elif statement_type == 'while_loop':
                result, message = self.analyze_while_loop()
            elif statement_type == 'function':
                result, message = self.analyze_function_statement()
            elif statement_type == 'function_call':
                result, message = self.analyze_function_call()
            else:
                self.skip_to_statement_end()
                result = False
                message = f"Unexpected statement at line {self.current_token().line if self.current_token() else 'EOF'}"
            if not result:
                results.append((result, message))
        return results

    def analyze_for_loop(self):
        try:
            self.expect('KEYWORD', 'for')
            self.expect('LEFT_PAREN')
            self.analyze_declaration()  # Analyze the declarative statement
            self.expect('SEPARATOR', ',')
            self.analyze_condition_block()  # Analyze the condition block
            self.expect('SEPARATOR', ',')
            self.analyze_iteration_block()  # Analyze the iteration block
            self.expect('RIGHT_PAREN')
            self.expect('COLON')
            self.expect('KEYWORD', 'then')
            self.expect('LEFT_PAREN')
            self.analyze_then_block()  # Analyze the then block
            self.expect('RIGHT_PAREN')
            self.expect('STATEMENT_END')
            return True, "For loop statement is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_while_loop(self):
        try:
            self.expect('KEYWORD', 'while')
            self.expect('LEFT_PAREN')
            self.analyze_condition_block()  # Analyze the condition block
            self.expect('RIGHT_PAREN')
            self.expect('COLON')
            self.expect('KEYWORD', 'then')
            self.expect('LEFT_PAREN')
            self.analyze_then_block()  # Analyze the then block
            self.expect('RIGHT_PAREN')
            self.expect('STATEMENT_END')
            return True, "While loop statement is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_condition_block(self):
        self.expect('IDENTIFIER')
        self.expect('COMPARISON')
        self.expect('NUMERIC_LITERAL')

    def analyze_iteration_block(self):
        if self.match('IDENTIFIER'):
            self.expect('IDENTIFIER')
            if self.match('INCREMENT'):
                self.expect('INCREMENT')
            elif self.match('DECREMENT'):
                self.expect('DECREMENT')
            else:
                raise SyntaxError(f"Unexpected token in iteration block at line {self.current_token().line}")

    def analyze_then_block(self):
        while not self.match('RIGHT_PAREN'):
            self.expect('IDENTIFIER')
            self.expect('ASSIGNMENT')
            if self.match('STRING_LITERAL'):
                self.expect('STRING_LITERAL')
            elif self.match('FLOAT_LITERAL'):
                self.expect('FLOAT_LITERAL')
            elif self.match('NUMERIC_LITERAL'):
                self.expect('NUMERIC_LITERAL')
            elif self.match('BOOL_LITERAL'):
                self.expect('BOOL_LITERAL')
            else:
                raise SyntaxError(f"Unexpected token at line {self.tokens[self.pos].line}")
            self.expect('STATEMENT_END')

    def analyze_function_statement(self):
        try:
            self.expect('KEYWORD', 'func')
            self.expect('IDENTIFIER')  # Function name
            self.expect('LEFT_PAREN')
            self.analyze_parameter_block()  # Analyze the parameter block
            self.expect('RIGHT_PAREN')
            self.expect('COLON')
            self.expect('KEYWORD', 'then')
            self.expect('LEFT_PAREN')
            self.analyze_then_block()  # Analyze the then block
            self.expect('RIGHT_PAREN')
            self.expect('STATEMENT_END')
            return True, "Function declaration is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_parameter_block(self):
        if not self.match('RIGHT_PAREN'):
            while True:
                self.expect('DATA_TYPE')
                self.expect('IDENTIFIER')
                if self.match('SEPARATOR', ','):
                    self.next_token()  # Skip the comma
                else:
                    break

    def analyze_function_call(self):
        try:
            self.expect('IDENTIFIER')  # Function name
            self.expect('LEFT_PAREN')
            if not self.match('RIGHT_PAREN'):
                self.analyze_arguments()
            self.expect('RIGHT_PAREN')
            self.expect('STATEMENT_END')
            return True, "Function call is correct"
        except SyntaxError as e:
            return False, str(e)

    def analyze_arguments(self):
        while True:
            if self.match('STRING_LITERAL'):
                self.expect('STRING_LITERAL')
            elif self.match('NUMERIC_LITERAL'):
                self.expect('NUMERIC_LITERAL')
            elif self.match('FLOAT_LITERAL'):
                self.expect('FLOAT_LITERAL')
            elif self.match('IDENTIFIER'):
                self.expect('IDENTIFIER')
            else:
                raise SyntaxError(f"Unexpected token in function arguments at line {self.current_token().line}")
            if self.match('SEPARATOR', ','):
                self.next_token()  # Skip the comma
            else:
                break
