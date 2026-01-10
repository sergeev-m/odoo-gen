from .base import BaseController
from ..core.context import ProjectContext
from ..core.signals import Signal


class ControllerChain:
    def __init__(self, controllers: list[BaseController | None]):
        self.controllers = [c for c in controllers if c]

    # def handle(self, error, ctx: ProjectContext):
    #     for c in self.controllers:
    #         if c.on_error(error, ctx):
    #             return
    #     raise error

    def on_step(self, step: str, ctx):
        for c in self.controllers:
            c.on_step(step, ctx)

    def before_generate(self, ctx):
        for c in self.controllers:
            c.before_generate(ctx)

    def after_generate(self, ctx):
        for c in self.controllers:
            c.after_generate(ctx)

    def before_step(self, step, ctx):
        for c in self.controllers:
            c.before_step(step, ctx)

    def after_step(self, step, ctx):
        for c in self.controllers:
            c.after_step(step, ctx)

    def handle_signal(self, signal: Signal, ctx) -> bool:
        for c in self.controllers:
            if c and c.on_signal(signal, ctx):
                return True
        return False
