from modempay.resources.base import BaseResource
from modempay.types.balance import Balance


class BalancesResource(BaseResource):
    """
    Resource class for balances.
    """

    def __init__(self, api_key: str, max_retries: int, timeout: int):
        super().__init__(api_key, max_retries, timeout)

    def retrieve(self) -> Balance:
        """
        Retrieves account balances.

        Returns:
            Balance: The balance object.
        """
        return self.request(
            "get",
            f"/v1/balances",
        )
