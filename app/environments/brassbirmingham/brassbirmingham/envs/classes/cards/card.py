from python.id import id

from typing import Union
from .enums import CardName, CardType


class Card:
    """
    Card object

    :param type: any of ['location', 'industry']
    :param name: name of location or industry
    """

    def __init__(self, type: CardType, name: Union[CardName, str]):
        self.id = id()
        self.name = name
        self.type = type
        self.isWild = name == CardName.wild_location or name == CardName.wild_industry
