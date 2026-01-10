from .base import BaseController
from ..core.context import ProjectContext


class VerboseController(BaseController):
    def on_step(self, step, ctx: ProjectContext):
        print(f"[resolve] {step}")

    def before_step(self, step, ctx: ProjectContext):
        if step.details:
            print(f"→ {step.details}")
