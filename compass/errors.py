class CompassError(Exception):
    pass


class ConfigError(CompassError):
    pass


class PrerequisiteError(CompassError):
    pass


class CollectorError(CompassError):
    pass


class AdapterError(CompassError):
    pass


class ProviderError(AdapterError):
    pass


class SchemaValidationError(AdapterError):
    pass
