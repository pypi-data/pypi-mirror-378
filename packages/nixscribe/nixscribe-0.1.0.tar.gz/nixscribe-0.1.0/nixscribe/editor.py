from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import PythonLexer, HtmlLexer, CssLexer, JavascriptLexer
from rich.syntax import Syntax
from rich.console import Console
from pathlib import Path
import os

console = Console()


def create(file: str):
    with open(file, "w"):
        ...
    print("File created Successfully.")


def view(file: str):
    with open(file, "r") as f:
        file_data = f.read()
    ext_map = {".py": "python", ".html": "html", ".css": "css", ".js": "javascript"}
    lang = ext_map.get(Path(file).suffix)
    if lang:
        syntax = Syntax(file_data, lang, theme="monokai", line_numbers=True)
        console.print(syntax)
    else:
        console.print(file_data)


def edit(file: str):
    os.system("cls" if os.name == "nt" else "clear")
    text = ""
    if Path(file).exists():
        with open(file, "r") as f:
            text = f.read()

    ext_map = {
        ".py": PythonLexer,
        ".html": HtmlLexer,
        ".css": CssLexer,
        ".js": JavascriptLexer,
    }

    lexer_class = ext_map.get(Path(file).suffix)
    lexer = PygmentsLexer(lexer_class) if lexer_class else None

    kb = KeyBindings()

    @kb.add("c-s")
    def _(event):
        with open(file, "w") as f:
            f.write(event.app.current_buffer.text)
        print(f"\nSaved {file}!")

    @kb.add("f3")
    def _(event):
        with open(file, "w") as f:
            f.write(event.app.current_buffer.text)
        event.app.exit()

    @kb.add("c-q")
    def _(event):
        event.app.exit()

    @kb.add("tab")
    def _(event):
        event.app.current_buffer.insert_text("    ")

    session = PromptSession(
        lexer=lexer,
        key_bindings=kb,
        multiline=True,
        bottom_toolbar="Ctrl+Q: Quit | Ctrl+S: Save | F3: Save & Quit",
    )

    session.prompt("> ", default=text)
