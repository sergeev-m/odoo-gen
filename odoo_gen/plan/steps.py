from dataclasses import dataclass
from pathlib import Path
from odoo_gen.enums import WriteMode, StepAction


@dataclass(frozen=True)
class PlanStep:
    action: StepAction            # "mkdir", "write"
    path: Path
    content: str | None = None
    details: str | None = None
    mode: WriteMode = WriteMode.CREATE
