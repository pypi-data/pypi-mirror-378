"""Utils for documentation."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

import mknodes as mk


def create_example_doc(
    name: str,
    *,
    style: Literal["simple", "full"] = "full",
) -> mk.MkContainer:
    """Create documentation for an example file.

    Args:
        name: Name of example file (e.g. "download_agents.py")
        examples_dir: Directory containing examples (default: examples/)
        style: Documentation style:
            - simple: Just the code
            - full: Title, description from docstring, code, etc.

    Returns:
        Container with all documentation elements
    """
    path = Path("src/llmling_agent_examples") / name

    if not path.exists():
        msg = f"Example {name} not found"
        raise FileNotFoundError(msg)

    container = mk.MkContainer()

    if style == "full":
        # Extract title/description from example's docstring
        title = path.stem.replace("_", " ").title()
        container += mk.MkHeader(title, level=2)

        # Add description from docstring if available
        if docstring := ast.get_docstring(ast.parse(path.read_text())):
            container += docstring

    # Add the code itself
    container += mk.MkCode(path.read_text(), language="python")

    return container
