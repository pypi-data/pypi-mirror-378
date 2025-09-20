from dars.core.component import Component
from typing import Optional

class Tooltip(Component):
    """
    Tooltip: information box on hover.
    text: text to display
    child: wrapped component or HTML
    position: top, right, bottom, left (optional)
    """

    def __init__(self, text: str, child: Component, position: Optional[str] = "top", **props):
        super().__init__(**props)
        self.text = text
        self.child = child
        self.position = position

    def render(self) -> str:
        return f'<div class="dars-tooltip dars-tooltip-{self.position}">{self.child.render() if hasattr(self.child, "render") else self.child}<span class="dars-tooltip-text">{self.text}</span></div>'
