class RDSRepositoryError(Exception):
    pass


class TimeoutErrorRDS(RDSRepositoryError):
    pass
