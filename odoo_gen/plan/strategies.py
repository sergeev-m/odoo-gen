from odoo_gen.plan.steps import WriteMode


class WriteStrategy:
    def __init__(self, *, force: bool, skip: bool):
        self.force = force
        self.skip = skip

    def resolve(self, mode: WriteMode, exists: bool) -> WriteMode | None:
        """Resolve final write mode based on CLI flags."""
        match mode:

            case WriteMode.CREATE:
                if exists:
                    if self.force:
                        return WriteMode.OVERWRITE
                    if self.skip:
                        return None   # SKIP
                    raise FileExistsError
                return WriteMode.CREATE

            case WriteMode.OVERWRITE:
                if exists and not self.force:
                    raise FileExistsError
                return WriteMode.OVERWRITE

            case WriteMode.APPEND:
                return WriteMode.APPEND if exists else WriteMode.CREATE

            case WriteMode.MODIFY:
                # всегда разрешено
                return WriteMode.MODIFY

            case WriteMode.SKIP:
                return None
