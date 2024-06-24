from youlexical import lex, SymbolTable
from sylvasyntax import Token, SyntaxAnalyzer
from sylvasemantic import SemanticAnalyzer
from codegeneration import CodeGenerator
from intermediatecode import IntermediateCodeGenerator  # Importing the IntermediateCodeGenerator class

def main():
    code = """
    num rr = 88;
    line sample = "s";
    point vae = 9.9;
    binal ees = True;
    if(rr >= 3):
    then( sample = "hello"; 
    )
    else:
    then( sample = "done";
    );
    if(rr < 8):
    then(
    sample = "second";
    )
    if not( vae < 10):
    then(
    sample = "condition";
    );
    for(num i = 0, i <= 3, i++):
    then(
    sample = "print";
    );
    while(i >= 5):
    then(
    sample = "pp";
    );
    func add(num x, num y):
    then( sample = "ss";
    );
    func sum(num a, num b):
    then( sample = "uihsvdgh";
    );
    add(3,5);
    sum(7,9);
    """
    raw_tokens, symbol_table = lex(code)
    for token in raw_tokens:
        print(f"Line {token[0]}: {token[1]} - {token[2]}")
    tokens = [Token(line, type, value) for line, type, value in raw_tokens]

    print(symbol_table)

    # Syntax analysis
    analyzer = SyntaxAnalyzer(tokens, symbol_table)
    syntax_results = analyzer.parse()

    # Semantic analysis
    semantic_analyzer = SemanticAnalyzer(tokens, symbol_table)
    semantic_results = semantic_analyzer.analyze()

    print("Syntax Analysis Results:")
    if not syntax_results:
        print("No errors")
    else:
        for result, message in syntax_results:
            print(message)

    print("\nSemantic Analysis Results:")
    if not semantic_results:
        print("No errors")
    else:
        for message in semantic_results:
            print(message)



    # Code generation
    code_generator = CodeGenerator(tokens, symbol_table)
    assembly_code = code_generator.generate_code()
    print("\nGenerated Assembly Code:")
    print(assembly_code)

if __name__ == "__main__":
    main()
