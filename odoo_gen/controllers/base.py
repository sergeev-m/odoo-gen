from ..core.context import ProjectContext


class BaseController:

    def on_error(self, error, ctx: ProjectContext) -> bool:
        return False

    def before_generate(self, ctx: ProjectContext):
        pass

    def after_generate(self, ctx: ProjectContext):
        pass

    def before_step(self, step, ctx: ProjectContext):
        pass

    def after_step(self, step, ctx: ProjectContext):
        pass

    def on_step(self, name, ctx):
        pass

    def on_signal(self, signal, ctx: ProjectContext) -> bool:
        return False
