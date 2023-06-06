from python.print_colors import (prCyan, prGreen, prLightGray, prPurple, prRed,
                                 prYellow)

from .card import Card
from .enums import CardName, CardType

# from consts import *
# from consts import (STOKE_ON_TRENT, LEEK, STONE, UTTOXETER, BELPER, DERBY, STAFFORD, CANNOCK, WALSALL, BURTON_UPON_TRENT, TAMWORTH,
#                 WOLVERHAMPTON, COALBROOKDALE, DUDLEY, KIDDERMINSTER, WORCESTER, NUNEATON, BIRMINGHAM, COVENTRY, REDDITCH, BEER1, BEER2)

class LocationCard(Card):
    def __init__(self, name: CardName, isWild=False):
        super(LocationCard, self).__init__(CardType.location, name=name)
        self.isWild = isWild
        self.isWild = name == CardName.wild_location

    def __str__(self) -> str:
        if self.isWild:
            return self.name

        if self.name in ["Stoke-On-Trent", 'Leek', 'Stone', 'Uttoxeter']:
            return prCyan(self.name)
        elif self.name in ["Belper", 'Derby']:
            return prGreen(self.name)
        elif self.name in [
            "Stafford",
            'Cannock',
            'Walsall',
            "Burton-Upon-Trent",
            'Tamworth',
        ]:
            return prRed(self.name)
        elif self.name in [
            'Wolverhampton',
            'Coalbrookdale',
            'Dudley',
            'Kidderminster',
            'Worcester',
        ]:
            return prYellow(self.name)
        elif self.name in ['Nuneaton', 'Birmingham', 'Coventry', 'Redditch']:
            return prPurple(self.name)
        elif self.name == "beer1" or self.name == "beer2":
            return prLightGray(self.name)
        return self.name

    def __repr__(self) -> str:
        return str(self)
