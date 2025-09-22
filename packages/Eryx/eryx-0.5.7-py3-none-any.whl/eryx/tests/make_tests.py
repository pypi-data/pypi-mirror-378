"""Script to generate test files."""

import os
import sys
import tkinter as tk
from io import StringIO
from tkinter import messagebox
from tkinter.filedialog import askdirectory, askopenfilename

from eryx.__init__ import CURRENT_VERSION
from eryx.frontend.parser import Parser
from eryx.runtime.environment import Environment
from eryx.runtime.interpreter import evaluate
from eryx.utils.pretty_print import pprint

current_path = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(current_path, "test"), exist_ok=True)


def generate_ast(code):
    """Generate AST from code using the parser."""
    parser = Parser()
    return parser.produce_ast(code)


def capture_output(func, *args, **kwargs):
    """Capture output printed during the execution of the code."""
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        func(*args, **kwargs)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


def read_info(file_path: str) -> dict:
    """Read the info.test file to get the metadata."""
    with open(file_path, "r", encoding="utf8") as file:
        lines = file.readlines()
        info = {
            "version": lines[0].split(":")[1].strip(),
            "name": lines[1].split(":")[1].strip(),
            "description": lines[2].split(":")[1].strip(),
        }
    return info


def write_files(test_folder, code, test_name, description):
    """Write the test files to the test folder."""
    # Generate AST
    test_ast = generate_ast(code)
    with open(
        os.path.join(test_folder, f"{test_name}.eryx.ast"), "w", encoding="utf8"
    ) as f:
        try:
            f.write(str(pprint(test_ast, print_output=False, use_color=False)))
        except RuntimeError as e:
            print(f"Parser Error: {e}")
            return

    # Capture printed output
    try:
        output = capture_output(evaluate, test_ast, Environment())
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
        return
    with open(
        os.path.join(test_folder, f"{test_name}.eryx.output"), "w", encoding="utf8"
    ) as f:
        f.write(output[:-1])

    # Create info.test file
    with open(os.path.join(test_folder, "test.info"), "w", encoding="utf8") as f:
        f.write(f"Version: {CURRENT_VERSION}\n")
        f.write(f"Name: {test_name}\n")
        f.write(f"Description: {description}")


def create_test_files(code, description, test_name):
    """Create the test files with actual values."""
    # Create the folder to store the test files
    test_folder = os.path.join(current_path, "test", test_name)
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Create .eryx file (the code itself)
    with open(
        os.path.join(test_folder, f"{test_name}.eryx"), "w", encoding="utf8"
    ) as f:
        f.write(code)

    write_files(test_folder, code, test_name, description)

    messagebox.showinfo("Success", f"Test files for {test_name} have been created.")


def on_create_test():
    """Handle the create test button click."""
    code = code_text.get("1.0", tk.END).strip()
    description = description_entry.get()
    test_name = name_entry.get()

    if not code or not test_name:
        messagebox.showerror("Error", "Please provide both code and test name.")
        return

    # Call the function to create the test files
    create_test_files(code, description, test_name)


def on_remake_all_tests():
    """Handle remaking of all tests."""
    for test_folder in os.listdir(os.path.join(current_path, "test")):
        try:
            info = read_info(
                os.path.join(current_path, "test", test_folder, "test.info")
            )

            # Get the code from the .eryx file
            with open(
                os.path.join(current_path, "test", test_folder, f"{info['name']}.eryx"),
                "r",
                encoding="utf8",
            ) as f:
                code = f.read()

            write_files(
                os.path.join(current_path, "test", test_folder),
                code,
                info["name"],
                info["description"],
            )
        except Exception as e:  # pylint: disable=broad-except
            print(f"{test_folder}: {e}")

    messagebox.showinfo("Success", "All test files have been regenerated.")


def on_remake_test():
    """Handle remaking of a test."""
    test_folder = askdirectory(
        initialdir=os.path.join(current_path, "test"),
        mustexist=True,
        title="Select Test Folder",
    )
    if not test_folder:
        return

    info = read_info(os.path.join(test_folder, "test.info"))

    # Get the code from the .eryx file
    with open(
        os.path.join(test_folder, f"{info['name']}.eryx"), "r", encoding="utf8"
    ) as f:
        code = f.read()

    write_files(test_folder, code, info["name"], info["description"])

    messagebox.showinfo(
        "Success", f"Test files for {info['name']} have been regenerated."
    )


def on_make_test():
    """Handle making a test from a file."""
    test_file = askopenfilename(
        initialdir=os.path.join(current_path, "test"),
        title="Select File",
        filetypes=[("Eryx Files", "*.eryx")],
    )

    if not test_file:
        return

    with open(test_file, "r", encoding="utf8") as f:
        code = f.read()

    test_name = os.path.basename(test_file).replace(".eryx", "")
    description = ""

    create_test_files(code, description, test_name)


# Set up the Tkinter GUI
root = tk.Tk()
root.title("Test File Generator")
root.resizable(False, False)

# Remake test
remake_button = tk.Button(root, text="Remake Test", command=on_remake_test)
remake_button.pack()

# Remake test
remake_all_button = tk.Button(
    root, text="Remake All Tests", command=on_remake_all_tests
)
remake_all_button.pack()

# Make test from file
make_test_button = tk.Button(root, text="From File", command=on_make_test)
make_test_button.pack()

# Code input
code_label = tk.Label(root, text="Code:")
code_label.pack()
code_text = tk.Text(root, height=10, width=50)
code_text.pack()

# Test name
name_label = tk.Label(root, text="Test Name:")
name_label.pack()
name_entry = tk.Entry(root, width=50)
name_entry.pack()

# Description
description_label = tk.Label(root, text="Description:")
description_label.pack()
description_entry = tk.Entry(root, width=50)
description_entry.pack()

# Create button
create_button = tk.Button(root, text="Create Test Files", command=on_create_test)
create_button.pack(pady=(0, 10))

# Run the Tkinter event loop
root.mainloop()
