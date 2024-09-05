class PelicanError(Exception):
    pass


class EmptyExchangeRatesTableError(PelicanError):
    pass


class NonPositiveLimitError(PelicanError):
    pass
