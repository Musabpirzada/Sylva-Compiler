import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from youlexical import lex, SymbolTable  # Importing the lexical analysis and symbol table classes
from codegenerationgui import CodeGenerator  # Importing the CodeGenerator class
from sylvasyntax import SyntaxAnalyzer, Token  # Importing the SyntaxAnalyzer class
from sylvasemantic import SemanticAnalyzer  # Importing the SemanticAnalyzer class

# Initialize the main window
root = ctk.CTk()
root.title("Sylva Compiler")
root.geometry("800x600")

# Set the theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Title
title_label = ctk.CTkLabel(root, text="Sylva Compiler", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

# Create a main frame
main_frame = ctk.CTkFrame(root)
main_frame.pack(pady=20, expand=True, fill="both")

# Configure grid layout in the main frame
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Editor Text Area
editor_label = ctk.CTkLabel(main_frame, text="Editor")
editor_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

editor_text = ctk.CTkTextbox(main_frame, width=300, height=300)
editor_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Output and Errors Frame
output_errors_frame = ctk.CTkFrame(main_frame)
output_errors_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

output_errors_frame.grid_rowconfigure(0, weight=1)
output_errors_frame.grid_rowconfigure(1, weight=1)
output_errors_frame.grid_columnconfigure(0, weight=1)

# Output Text Area
output_label = ctk.CTkLabel(output_errors_frame, text="Output")
output_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

output_text = ctk.CTkTextbox(output_errors_frame, width=300, height=150, state="disabled")
output_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Errors Text Area
errors_label = ctk.CTkLabel(output_errors_frame, text="Errors")
errors_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

errors_text = ctk.CTkTextbox(output_errors_frame, width=300, height=150, state="disabled")
errors_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")


# Function to show symbol table in a new window
def show_symbol_table():
    code = editor_text.get("1.0", tk.END)
    tokens, symbol_table = lex(code)

    symbol_table_window = ctk.CTkToplevel(root)
    symbol_table_window.title("Symbol Table")
    symbol_table_window.geometry("600x400")

    tree = ttk.Treeview(symbol_table_window)

    # Define columns
    columns = ("Name", "Type", "Size", "Dimension", "Line of Declaration", "Line of Usage", "Address", "Entry Type")
    tree['columns'] = columns

    # Format columns
    for col in columns:
        tree.column(col, width=100, minwidth=100, stretch=tk.NO)
        tree.heading(col, text=col, anchor=tk.W)

    tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    symbol_table_data = symbol_table.get_all_entries()
    for entry in symbol_table_data:
        tree.insert("", "end", values=(entry['Name'], entry['Type'], entry['Size'], entry['Dimension'],
                                       entry['Line of Declaration'], entry['Line of Usage'],
                                       entry['Address'], entry['Entry Type']))


# Function to show assembly code in a new window
def show_assembly_code():
    code = editor_text.get("1.0", tk.END)
    tokens, symbol_table = lex(code)
    code_generator = CodeGenerator(tokens, symbol_table)
    assembly_code = code_generator.generate_code()

    assembly_code_window = ctk.CTkToplevel(root)
    assembly_code_window.title("Assembly Code")
    assembly_code_window.geometry("600x400")

    assembly_text = ctk.CTkTextbox(assembly_code_window, width=580, height=380)
    assembly_text.pack(padx=10, pady=10)
    assembly_text.insert(tk.END, assembly_code)
    assembly_text.configure(state="disabled")


# Function to run the code
def run_code():
    code = editor_text.get("1.0", tk.END)
    raw_tokens, symbol_table = lex(code)
    tokens = [Token(line, type, value) for line, type, value in raw_tokens]

    syntax_analyzer = SyntaxAnalyzer(tokens, symbol_table)
    syntax_results = syntax_analyzer.parse()

    errors_text.configure(state="normal")
    errors_text.delete("1.0", tk.END)

    if syntax_results:
        for result, message in syntax_results:
            errors_text.insert(tk.END, message + "\n")
        errors_text.configure(state="disabled")
        return

    semantic_analyzer = SemanticAnalyzer(tokens, symbol_table)
    semantic_results = semantic_analyzer.analyze()

    if semantic_results:
        for message in semantic_results:
            errors_text.insert(tk.END, message + "\n")
        errors_text.configure(state="disabled")
        return


    errors_text.insert(tk.END, "Code executed successfully without errors.")
    errors_text.configure(state="disabled")

    errors_text.insert(tk.END, "Code executed successfully without errors.")
    errors_text.configure(state="disabled")


# Run and Compile Buttons
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

run_button = ctk.CTkButton(button_frame, text="Run", width=100, command=run_code)
run_button.grid(row=0, column=0, padx=10)

compile_button = ctk.CTkButton(button_frame, text="Compile", width=100)
compile_button.grid(row=0, column=1, padx=10)

# Errors, Symbol Table, and Assembly Code Buttons
bottom_frame = ctk.CTkFrame(root)
bottom_frame.pack(pady=10)

symbol_table_button = ctk.CTkButton(bottom_frame, text="Symbol Table", width=100, command=show_symbol_table)
symbol_table_button.grid(row=0, column=1, padx=10)

assembly_button = ctk.CTkButton(bottom_frame, text="Assembly Code", width=100, command=show_assembly_code)
assembly_button.grid(row=0, column=2, padx=10)

# Start the main loop
root.mainloop()