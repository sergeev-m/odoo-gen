from .context import ProjectContext


class Signal:
    def can_auto_resolve(self, ctx: ProjectContext) -> bool:
        return False

    def auto_resolve(self, ctx: ProjectContext) -> bool:
        return False


class RequireAddonsPath(Signal):
    pass


class RequireModulePath(Signal):
    pass


class CreateModule(Signal):
    def __init__(self, path):
        self.path = path


class ChooseAddons(Signal):
    def __init__(self, paths):
        self.paths = paths

    def can_auto_resolve(self, ctx: ProjectContext):
        return len(self.paths) == 1

    def auto_resolve(self, ctx):
        ctx.addons_path = self.paths[0]
        return True
    

class ChooseModule(Signal):
    def __init__(self, modules):
        self.modules = modules


class RequireMenuPlacement(Signal):
    pass
