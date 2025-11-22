"""Hello World Markdown Widget.

A simple example widget that demonstrates basic markdown rendering
with a text parameter.
"""


def hello_world(name: str = ""):
    """Returns a personalized greeting message.

    Args:
        name (str, optional): Name to include in the greeting. Defaults to empty string.

    Returns:
        str: A greeting message with the provided name in markdown format.
    """
    return f"# Hello World {name}"
