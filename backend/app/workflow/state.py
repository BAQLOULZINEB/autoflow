"""Graph state shared by every node. One thread per customer request."""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AutoFlowState(TypedDict, total=False):
    request_id: str
    customer_name: str
    channel: str
    raw_message: str
    today: str                       # ISO date, demo-clock aware

    structured: dict                 # Intake output
    availability: dict               # Availability output
    followup: dict                   # Follow-up output (draft + action)

    workflow_state: str              # new | incomplete | checked | quote_ready | ...
    review: dict                     # {level, priority, reason} when a human is needed
    decision: dict                   # human decision received through interrupt()
    hops: int
    trace: Annotated[list, add_messages]   # short log lines for the UI
