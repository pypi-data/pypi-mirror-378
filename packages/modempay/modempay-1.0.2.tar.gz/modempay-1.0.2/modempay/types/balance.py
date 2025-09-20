from typing import TypedDict


class Balance(TypedDict, total=False):
    """
    Representation of an account balance.
    """

    available_balance: float
    payout_balance: float
