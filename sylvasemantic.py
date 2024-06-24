class SemanticAnalyzer:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.symbol_table = symbol_table

    def analyze(self):
        results = []
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            if token.type == 'DATA_TYPE':
                declaration_result = self.check_declaration(i)
                if declaration_result:
                    results.append(declaration_result)
                i += 4  # Skip to next token after declaration and assignment
            elif token.type == 'IDENTIFIER':
                if self.is_function_call(i):
                    function_call_result = self.check_function_call(token)
                    if function_call_result:
                        results.append(function_call_result)
                else:
                    usage_result = self.check_variable_usage(token)
                    if usage_result:
                        results.append(usage_result)
            i += 1
        return results

    def check_declaration(self, index):
        datatype = self.tokens[index].value
        variable_name = self.tokens[index + 1].value
        assignment_operator = self.tokens[index + 2].type
        value_token = self.tokens[index + 3]

        existing_entry = self.symbol_table.lookup(variable_name)
        if existing_entry:
            if existing_entry['Type'] != datatype and existing_entry['Entry Type'] == 'variable':
                return f"Semantic Error: Variable '{variable_name}' already declared with type '{existing_entry['Type']}' at line {existing_entry['Line of Declaration']}"

        # Type checking
        if assignment_operator == 'ASSIGNMENT':
            if datatype == 'num' and value_token.type != 'NUMERIC_LITERAL':
                return f"Semantic Error: Variable '{variable_name}' of type 'num' assigned non-numeric value at line {value_token.line}"
            elif datatype == 'line' and value_token.type != 'STRING_LITERAL':
                return f"Semantic Error: Variable '{variable_name}' of type 'line' assigned non-string value at line {value_token.line}"
            elif datatype == 'binal' and value_token.type != 'BOOL_LITERAL':
                return f"Semantic Error: Variable '{variable_name}' of type 'binal' assigned non-boolean value at line {value_token.line}"
            elif datatype == 'point' and value_token.type != 'FLOAT_LITERAL':
                return f"Semantic Error: Variable '{variable_name}' of type 'point' assigned non-float value at line {value_token.line}"
        return None

    def check_variable_usage(self, token):
        variable_name = token.value
        entry = self.symbol_table.lookup(variable_name)
        if not entry:
            return f"Semantic Error: Variable '{variable_name}' not declared before use at line {token.line}"
        elif entry['Entry Type'] != 'variable':
            return None
        return None

    def check_function_call(self, token):
        function_name = token.value
        entry = self.symbol_table.lookup(function_name)
        if not entry:
            return f"Semantic Error: Function '{function_name}' not declared before use at line {token.line}"
        elif entry['Entry Type'] != 'function':
            return f"Semantic Error: '{function_name}' is not a function but used as one at line {token.line}"
        return None

    def is_function_call(self, index):
        return index + 1 < len(self.tokens) and self.tokens[index + 1].type == 'LEFT_PAREN'
