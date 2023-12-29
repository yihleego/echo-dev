from enum import Enum


class State(str, Enum):
    ENABLED = "enabled"
    FOCUSABLE = "focusable"
    VISIBLE = "visible"
    EDITABLE = "editable"
    CHECKED = "checked"
    FOCUSED = "focused"
    SHOWING = "showing"
    OPAQUE = "opaque"
