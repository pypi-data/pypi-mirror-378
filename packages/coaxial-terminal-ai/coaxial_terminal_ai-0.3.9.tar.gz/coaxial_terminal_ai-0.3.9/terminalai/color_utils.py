from pygments import highlight
from pygments.lexers.shell import BashLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.special import TextLexer
from pygments.formatters.terminal import TerminalFormatter
import re

# ANSI color codes - Revert to original color scheme
AI_COLOR = "\033[96m"  # Bright cyan
COMMAND_COLOR = "\033[95;1m"  # Bright bold magenta
INFO_COLOR = "\033[36m"  # Cyan for info text
ERROR_COLOR = "\033[91m"  # Red for errors
SUCCESS_COLOR = "\033[92m"  # Green for success messages
PROMPT_COLOR = "\033[33m"  # Yellow for prompts
HIGHLIGHT_COLOR = "\033[36m"  # Cyan for highlights
RESET = "\033[0m"
BOLD = "\033[1m"


def colorize_ai(text):
    return f"{AI_COLOR}{text}{RESET}"

def colorize_command(text):
    return f"{COMMAND_COLOR}{text}{RESET}"

def colorize_info(text):
    return f"{INFO_COLOR}{text}{RESET}"

def colorize_error(text):
    return f"{ERROR_COLOR}{text}{RESET}"

def colorize_success(text):
    return f"{SUCCESS_COLOR}{text}{RESET}"

def colorize_prompt(text):
    return f"{PROMPT_COLOR}{text}{RESET}"

def colorize_highlight(text):
    return f"{HIGHLIGHT_COLOR}{text}{RESET}"

def highlight_code_blocks(text):
    # Highlight triple backtick code blocks
    def block_replacer(match):
        code = match.group(2)
        lang = match.group(1)
        if lang == 'bash' or lang == 'sh':
            lexer = BashLexer()
        elif lang == 'python':
            lexer = PythonLexer()
        else:
            lexer = TextLexer()
        return highlight(code, lexer, TerminalFormatter())
    text = re.sub(r'```(\w+)?\n([\s\S]*?)```', block_replacer, text)

    # Highlight inline code (single backticks)
    def inline_replacer(match):
        code = match.group(1)
        return highlight(code, BashLexer(), TerminalFormatter()).strip()
    text = re.sub(r'`([^`]+)`', inline_replacer, text)
    return text
