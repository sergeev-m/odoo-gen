class OdooGenError(Exception):
    pass


class ModulesNotFound(OdooGenError):
    pass


class AddonsPathNotFound(OdooGenError):
    pass


class ManifestParseError(OdooGenError):
    pass
