class IdeationToolsError(Exception):
    """Base error for deterministic tools."""


class ValidationRejected(IdeationToolsError):
    pass


class ConcurrencyConflict(IdeationToolsError):
    pass


class CommitFailed(IdeationToolsError):
    pass


class VerificationIndeterminate(IdeationToolsError):
    pass


class ReconciliationRequired(IdeationToolsError):
    pass
