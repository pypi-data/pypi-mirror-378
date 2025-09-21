from .exceptions import AuthenticationError
from .stock import Stock
from .trading import Trading


class PyAlpacaAPI:
    def __init__(self, api_key: str, api_secret: str, api_paper: bool = True) -> None:
        if not api_key or not api_secret:
            raise AuthenticationError()
        self._initialize_components(
            api_key=api_key, api_secret=api_secret, api_paper=api_paper
        )

    def _initialize_components(
        self, api_key: str, api_secret: str, api_paper: bool = True
    ):
        self.trading = Trading(
            api_key=api_key, api_secret=api_secret, api_paper=api_paper
        )
        self.stock = Stock(
            api_key=api_key,
            api_secret=api_secret,
            api_paper=api_paper,
            market=self.trading.market,
        )
