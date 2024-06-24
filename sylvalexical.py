import re
from tabulate import tabulate

token_types = [
    ('KEYWORD', r'\bif\s+not\b'),
    ('KEYWORD', r'\b(?:if|while|func|for|else|then)\b'),  # Keywords
    ('DATA_TYPE', r'\b(?:num|line|binal|point)\b'),  # Data Types
    ('BOOL_LITERAL', r'True|False'),  # Boolean literals
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),  # Identifiers
    ('ASSIGNMENT', r'='),  # Assignment operator
    ('COMPARISON', r'(?:<=|>=|==|!=|<|>)'),  # Comparison operators
    ('INCREMENT', r'\+\+'),  # Increment operator
    ('DECREMENT', r'--'),  # Decrement operator
    ('ARITHMETIC_OPERATOR', r'[+\-*/%]'),  # Arithmetic operators
    ('LOGICAL_OPERATOR', r'\b(?:and|or|not)\b'),  # Logical operators
    ('BITWISE_OPERATOR', r'[&|^~<>]'),  # Bitwise operators
    ('LEFT_PAREN', r'\('),  # Left Parenthesis
    ('RIGHT_PAREN', r'\)'),  # Right Parenthesis
    ('FLOAT_LITERAL', r'\d+\.\d+'),  # Float/Decimal literals
    ('NUMERIC_LITERAL', r'\d+'),  # Numeric literals
    ('STRING_LITERAL', r'"(.*?)"'),  # String literals
    ('WHITESPACE', r'\s+'),  # Whitespace
    ('NEWLINE', r'\n'),  # Newline
    ('STATEMENT_END', r';'),  # Statement end
    ('SEPARATOR', r','),  # Separator
    ('COLON', r':'),  # Colon
]

class SymbolTable:
    def __init__(self):
        self.table = []

    def add_entry(self, name, type, line, usage=None, entry_type='variable'):
        entry = {
            'Name': name,
            'Type': type,
            'Size': self.determine_size(type) if entry_type == 'variable' else None,
            'Dimension': '1D' if entry_type == 'variable' else None,
            'Line of Declaration': line,
            'Line of Usage': usage,
            'Address': len(self.table) + 1,
            'Entry Type': entry_type
        }
        self.table.append(entry)

    def determine_size(self, type):
        if type == 'num':
            return 4
        elif type == 'point':
            return 8
        elif type == 'line':
            return 0
        elif type == 'binal':
            return 1
        return 0

    def update_usage(self, name, line):
        for entry in self.table:
            if entry['Name'] == name:
                entry['Line of Usage'] = line

    def lookup(self, name):
        for entry in self.table:
            if entry['Name'] == name:
                return entry
        return None

    def get_all_entries(self):
        return self.table

    def __str__(self):
        headers = ["Name", "Type", "Size", "Dimension", "Line of Declaration", "Line of Usage", "Address", "Entry Type"]
        rows = [[entry['Name'], entry['Type'], entry['Size'], entry['Dimension'],
                 entry['Line of Declaration'], entry['Line of Usage'], entry['Address'], entry['Entry Type']] for entry in self.table]
        return tabulate(rows, headers, tablefmt='grid')



def lex(code):
    tokens = []
    line_number = 1
    symbol_table = SymbolTable()
    for line in code.split('\n'):
        line = line.strip()
        if line:
            while line:
                match = None
                for token_type, pattern in token_types:
                    regex = re.compile(pattern)
                    match = regex.match(line)
                    if match:
                        value = match.group(0)
                        if token_type == 'KEYWORD' and value == 'func':
                            tokens.append((line_number, token_type, value))
                            line = line[match.end():].strip()
                            id_match = re.match(r'[a-zA-Z_]\w*', line)
                            if id_match:
                                function_name = id_match.group(0)
                                tokens.append((line_number, 'IDENTIFIER', function_name))
                                symbol_table.add_entry(function_name, 'function', line_number, entry_type='function')
                                line = line[id_match.end():].strip()
                            continue
                        elif token_type == 'DATA_TYPE':
                            tokens.append((line_number, token_type, value))
                            line = line[match.end():].strip()
                            id_match = re.match(r'[a-zA-Z_]\w*', line)
                            if id_match:
                                identifier = id_match.group(0)
                                tokens.append((line_number, 'IDENTIFIER', identifier))
                                symbol_table.add_entry(identifier, value, line_number)
                                line = line[id_match.end():].strip()
                            continue
                        elif token_type == 'IDENTIFIER':
                            symbol_table.update_usage(value, line_number)
                        if token_type != 'WHITESPACE' and token_type != 'NEWLINE':
                            tokens.append((line_number, token_type, value))
                        line = line[match.end():]
                        break
                if not match:
                    print(f"Invalid token on line {line_number}: {line}")
                    break
            line_number += 1
    return tokens, symbol_table
