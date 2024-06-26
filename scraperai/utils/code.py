import re
import ast

from scraperai.exceptions import NoCodeFoundError


def polish_code(code: str) -> str:
    """
    Polish the code by removing the leading "python" or "py",  \
    removing surrounding '`' characters  and removing trailing spaces and new lines.

    Args:
        code (str): A string of Python code.

    Returns:
        str: Polished code.

    """
    if re.match(r"^(python|py)", code):
        code = re.sub(r"^(python|py)", "", code)
    if re.match(r"^`.*`$", code):
        code = re.sub(r"^`(.*)`$", r"\1", code)
    code = code.strip()
    return code


def is_python_code(string: str) -> bool:
    """
    Return True if it is valid python code.
    Args:
        string (str):

    Returns (bool): True if Python Code otherwise False

    """
    try:
        ast.parse(string)
        return True
    except SyntaxError:
        return False


def extract_python_code(response: str, separator: str = "```") -> str:
    """
    Extract the code from the response.

    Args:
        response (str): Response
        separator (str, optional): Separator. Defaults to "```".

    Raises:
        NoCodeFoundError: No code found in the response

    Returns:
        str: Extracted code from the response

    """
    code = response

    # If separator is in the response then we want the code in between only
    if separator in response and len(code.split(separator)) > 1:
        code = code.split(separator)[1]
    code = polish_code(code)

    # Even if the separator is not in the response, the output might still be valid python code
    if not is_python_code(code):
        raise NoCodeFoundError("No code found in the response")
    return code
