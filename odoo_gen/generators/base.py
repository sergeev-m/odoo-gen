from abc import ABC, abstractmethod
from jinja2 import Environment, PackageLoader

from odoo_gen.core import manifest
from odoo_gen.core.context import ProjectContext
from odoo_gen.plan.steps import PlanStep
from odoo_gen.enums import WriteMode, StepAction


class AbstractGenerator(ABC):
    @abstractmethod
    def is_applicable(self, ctx: ProjectContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def plan(self, ctx) -> list[PlanStep]:
        raise NotImplementedError

    # @abstractmethod
    # def generate(self, ctx):
    #     raise NotImplementedError
 

class BaseGenerator(AbstractGenerator):
    priority = 100
    
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader("odoo_gen", "templates")
        )

    def is_applicable(self, ctx: ProjectContext) -> bool:
        return True

    def _mkdir(self, path, details=None):
        return PlanStep(
            action=StepAction.MKDIR,
            path=path,
            details=details,
        )

    def _write(self, path, content, *, mode=WriteMode.CREATE, details=None):
        return PlanStep(
            action=StepAction.WRITE,
            path=path,
            content=content,
            mode=mode,
            details=details,
        )

    def _render_manifest(self, ctx: ProjectContext) -> str:
        if ctx.manifest is not None:
            return ctx.manifest.raw

        tpl = self.env.get_template("__manifest__.py.j2")
        return tpl.render(
            module_name=ctx.module_name,
            file_name=ctx.view_file_name,
        )

    def _render_access(self, ctx: ProjectContext) -> str:
        return (
            f"access_{ctx.module_name}_{ctx.model_underscore},"
            f"{ctx.module_model},"
            f"model_{ctx.module_name}_{ctx.model_underscore},"
            f"base.group_user,1,1,1,1\n"
        )

    def _render_model(self, ctx: ProjectContext) -> str:
        tpl = self.env.get_template("model.py.j2")
        return tpl.render(
            model=ctx.module_model,
            class_name=ctx.model_class_name,
            description=ctx.model_str
        )

    def _render_view(self, ctx: ProjectContext) -> str:
        tpl = self.env.get_template("view.xml.j2")
        return tpl.render(
            model=ctx.module_model,
            model_underscore=ctx.model_underscore,
            model_str=ctx.model,
            action_id=ctx.action_xml_id,
        )
