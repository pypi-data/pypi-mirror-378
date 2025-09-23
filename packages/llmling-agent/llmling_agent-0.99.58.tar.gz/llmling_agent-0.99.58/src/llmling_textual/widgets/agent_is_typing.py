"""Typing-widget. Credits to Elia (https://github.com/darrenburns/elia)."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import Reactive, reactive
from textual.widgets import Label, LoadingIndicator


class ResponseStatus(Vertical):
    """A widget that displays the status of the response from the node."""

    message: Reactive[str] = reactive("Node is responding", recompose=True)

    def compose(self) -> ComposeResult:
        yield Label(f" {self.message}")
        yield LoadingIndicator()

    def set_awaiting_response(self):
        self.message = "Awaiting response"
        self.add_class("-awaiting-response")
        self.remove_class("-agent-responding")

    def set_node_responding(self):
        self.message = "Agent is responding"
        self.add_class("-agent-responding")
        self.remove_class("-awaiting-response")


if __name__ == "__main__":
    from textualicious import show

    show(ResponseStatus())
