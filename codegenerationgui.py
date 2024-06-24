class CodeGenerator:
    def __init__(self, tokens, symbol_table):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.assembly_code = []
        self.label_count = 0
        self.registers = {
            'R0': None, 'R1': None, 'R2': None, 'R3': None, 'R4': None,
            'R5': None, 'R6': None, 'R7': None
        }

    def generate_code(self):
        i = 0
        while i < len(self.tokens):
            line_number, token_type, value = self.tokens[i]
            if token_type == 'DATA_TYPE':
                # Handle variable declarations and assignments
                datatype = value
                variable_name = self.tokens[i + 1][2]
                if self.tokens[i + 2][1] == 'ASSIGNMENT':
                    value_token = self.tokens[i + 3]
                    self.assembly_code.append(f"LOAD R0, {value_token[2]}")
                    self.assembly_code.append(f"STORE R0, {variable_name}")
                i += 4
            elif token_type == 'IDENTIFIER':
                if self.is_function_call(i):
                    # Handle function calls
                    function_name = value
                    arguments = self.get_function_arguments(i + 1)
                    for j, arg in enumerate(arguments):
                        self.assembly_code.append(f"LOAD R{j}, {arg}")
                    self.assembly_code.append(f"CALL {function_name}")
                else:
                    # Handle variable usage
                    variable_name = value
                    self.assembly_code.append(f"LOAD R0, {variable_name}")
                i += 1
            elif token_type == 'KEYWORD' and value in ['if', 'while', 'for']:
                # Handle control structures
                if value == 'if':
                    condition = self.tokens[i + 1]
                    self.label_count += 1
                    label = f"L{self.label_count}"
                    self.assembly_code.append(f"LOAD R0, {condition[2]}")
                    self.assembly_code.append(f"JZ R0, {label}")
                    i += self.handle_block(i + 2)
                    self.assembly_code.append(f"{label}:")
                elif value == 'while':
                    condition = self.tokens[i + 1]
                    self.label_count += 1
                    start_label = f"L{self.label_count}"
                    self.label_count += 1
                    end_label = f"L{self.label_count}"
                    self.assembly_code.append(f"{start_label}:")
                    self.assembly_code.append(f"LOAD R0, {condition[2]}")
                    self.assembly_code.append(f"JZ R0, {end_label}")
                    i += self.handle_block(i + 2)
                    self.assembly_code.append(f"JMP {start_label}")
                    self.assembly_code.append(f"{end_label}:")
                elif value == 'for':
                    init = self.tokens[i + 1]
                    condition = self.tokens[i + 3]
                    increment = self.tokens[i + 5]
                    self.label_count += 1
                    start_label = f"L{self.label_count}"
                    self.label_count += 1
                    end_label = f"L{self.label_count}"
                    self.assembly_code.append(f"LOAD R0, {init[2]}")
                    self.assembly_code.append(f"{start_label}:")
                    self.assembly_code.append(f"LOAD R0, {condition[2]}")
                    self.assembly_code.append(f"JZ R0, {end_label}")
                    i += self.handle_block(i + 6)
                    self.assembly_code.append(f"LOAD R0, {increment[2]}")
                    self.assembly_code.append(f"JMP {start_label}")
                    self.assembly_code.append(f"{end_label}:")
            elif token_type == 'KEYWORD' and value == 'func':
                # Handle function definitions
                function_name = self.tokens[i + 1][2]
                self.label_count += 1
                start_label = f"{function_name}_start"
                self.assembly_code.append(f"{start_label}:")
                i += self.handle_block(i + 4)
                self.assembly_code.append("RET")
            i += 1
        return "\n".join(self.assembly_code)

    def is_function_call(self, index):
        return index + 1 < len(self.tokens) and self.tokens[index + 1][1] == 'LEFT_PAREN'

    def get_function_arguments(self, index):
        args = []
        i = index + 1  # Skip the opening parenthesis
        while self.tokens[i][1] != 'RIGHT_PAREN':
            if self.tokens[i][1] in {'IDENTIFIER', 'NUMERIC_LITERAL', 'STRING_LITERAL', 'FLOAT_LITERAL', 'BOOL_LITERAL'}:
                args.append(self.tokens[i][2])
            i += 1
        return args

    def handle_block(self, index):
        # Handle the block of code inside control structures or function definitions
        i = index
        while self.tokens[i][1] != 'RIGHT_PAREN':
            if self.tokens[i][1] == 'IDENTIFIER':
                if self.is_function_call(i):
                    function_name = self.tokens[i][2]
                    arguments = self.get_function_arguments(i + 1)
                    for j, arg in enumerate(arguments):
                        self.assembly_code.append(f"LOAD R{j}, {arg}")
                    self.assembly_code.append(f"CALL {function_name}")
                else:
                    variable_name = self.tokens[i][2]
                    self.assembly_code.append(f"LOAD R0, {variable_name}")
                i += 1
            i += 1
        return i - index + 1
