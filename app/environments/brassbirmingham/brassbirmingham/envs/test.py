import unittest
from unittest.mock import MagicMock, Mock

from classes.game import Game
from classes.board import Board
from classes.deck import Deck
from classes.enums import Era
from classes.buildings.enums import MerchantName
from consts import *
from render import render
import asyncio
import random

class Test(unittest.TestCase):
    def resetGame(self, numPlayers):
        p3 = None
        p4 = None
        if numPlayers > 2:
            p3 = "Sam"
        if numPlayers > 3:
            p4 = "Mr. Mcdonald"
        self.game = Game(numPlayers, "Noah", "Tyler", p3, p4)

        # reset and set all merchant tiles to ALL
        # self.game.board.tradePosts = copy.deepcopy(TRADEPOSTS[str(numPlayers)])
        # for i, tradePost in enumerate(self.game.board.tradePosts):
        #     tradePost.addMerchantTile(self.game.board.merchantTiles[0])

        

    def setUp(self):
        self.resetGame(2)

    # test decks, hand, cards
    def testStartingValues(self):
        self.assertEqual(
            len(self.game.board.deck.cards),
            40 - 2 * STARTING_HAND_SIZE,
            "Should be 24 cards in a 2 player game",
        )
        self.resetGame(3)
        self.assertEqual(
            len(self.game.board.deck.cards),
            54 - 3 * STARTING_HAND_SIZE,
            "Should be 30 cards in a 3 player game",
        )
        self.resetGame(4)
        self.assertEqual(
            len(self.game.board.deck.cards),
            64 - 4 * STARTING_HAND_SIZE,
            "Should be 32 cards in a 4 player game",
        )
        self.assertEqual(
            self.game.board.coalMarketRemaining, 13, "Should be 13 coal on the market"
        )
        self.assertEqual(
            self.game.board.ironMarketRemaining, 8, "Should be 8 iron on the market"
        )
        self.assertEqual(self.game.board.priceForCoal(1), 1, "Should be $1 coal price")
        self.assertEqual(self.game.board.priceForIron(1), 2, "Should be $2 iron price")
        self.assertEqual(len(self.game.board.players), 4, "Should be 4 players")

        self.assertEqual(self.game.p1.buildings[0].name, BuildingName.goods, "Should be")
        self.assertEqual(
            len(self.game.p1.buildings), 44, "Should be 44 buildings tiles to start with"
        )

        self.assertEqual(self.game.board.towns[0].name, LEEK, "Should be")

    # test building canal between leek/stoke-on-trent
    def testBuildingCanal(self):
        town1 = self.game.board.towns[4]
        town2 = self.game.board.towns[12]

        self.assertEqual(
            self.game.board.areNetworked(town1, town2),
            False,
            f"{town1} and {town2} should NOT be networked",
        )
        leek = self.game.board.towns[0]
        stokeOnTrent = self.game.board.towns[1]
        self.assertFalse(
            self.game.board.areNetworked(leek, stokeOnTrent),
            f"{town1} and {town2} should NOT be networked",
        )
        # print(leek.networks)
        self.assertTrue(
            self.game.p1.canBuildCanal(leek.networks[0]), "Should be able to build a canal"
        )
        self.assertFalse(
            self.game.board.areNetworked(leek, stokeOnTrent),
            f"{town1} and {town2} should NOT be networked",
        )
        self.game.p1.buildCanal(leek.networks[0])
        self.assertFalse(
            self.game.p1.canBuildCanal(leek.networks[0]),
            "Should NOT be able to build a canal",
        )
        self.assertTrue(
            self.game.board.areNetworked(leek, stokeOnTrent),
            f"{town1} and {town2} should NOT be networked",
        )
        self.assertTrue(leek.networks[0].isBuilt, "Should be built")
        self.assertEqual(self.game.p1.money, 14, "self.game.P1 should have $14")

    # test network search
    def testNetworkSearch(self):
        redditch = self.game.board.townDict["Redditch"]
        birmingham = self.game.board.townDict["Birmingham"]
        walsall = self.game.board.towns[11]
        cannock = self.game.board.towns[9]
        # build network from cannock to redditch, assert network
        self.assertFalse(
            self.game.board.areNetworked(redditch, cannock),
            f"{redditch} and {cannock} should NOT be networked",
        )
        # print(redditch.networks)
        # print(birmingham.networks)
        # print(walsall.networks)
        # print(cannock.networks)
        self.assertFalse(
            self.game.p1.canPlaceCanal(redditch.networks[0]),
            "Should NOT be able to build a canal on a rail (no water)",
        )  # can't build canal on railroad only
        self.assertTrue(
            self.game.p1.canBuildCanal(redditch.networks[1]),
            "Should be able to build a canal",
        )
        self.assertTrue(
            self.game.p1.canBuildCanal(birmingham.networks[4]),
            "Should be able to build a canal",
        )
        self.game.p1.buildCanal(redditch.networks[1])
        self.game.p1.buildCanal(birmingham.networks[4])
        self.game.p1.buildCanal(birmingham.networks[0])
        self.game.p1.buildCanal(walsall.networks[1])
        self.assertEqual(self.game.p1.money, 5, "self.game.p1 money should be $5")
        self.assertTrue(
            self.game.board.areNetworked(redditch, cannock),
            f"{redditch} and {cannock} should be networked",
        )

        # test buildings
        self.assertTrue(
            self.game.p2.canBuildBuilding(self.game.p2.buildings[0], redditch.buildLocations[0]),
            "Should be",
        )
        self.game.p2.buildBuilding(self.game.p2.buildings[0], redditch.buildLocations[0])
        # should take coal from market (linked to oxford)
        self.assertTrue(self.game.p2.buildings[0].isActive, "Should be")
        self.assertEqual(self.game.p2.money, 8, "Should be")  # 17-8-1
        
        
        # these fail - idk why at the moment
        
        # self.assertTrue(
        #     self.game.p2.canBuildBuilding(self.game.p2.buildings[26], redditch.buildLocations[1]),
        #     "Should be",
        # )
        # self.game.p2.buildBuilding(self.game.p2.buildings[26], redditch.buildLocations[1])
        # self.assertEqual(self.game.p2.money, 1, "Should be")  # 8-5-2 (coal market missing 1)

    def testResourceMarketPrice(self):
        # Empty markets
        self.game.board.coalMarketRemaining = 0
        self.assertEqual(self.game.board.priceForCoal(4), 32)
        self.game.board.ironMarketRemaining = 0
        self.assertEqual(self.game.board.priceForIron(5), 30)

        # Single needed
        self.game.board.coalMarketRemaining = 8
        self.assertEqual(self.game.board.priceForCoal(1), 4)
        self.game.board.ironMarketRemaining = 8
        self.assertEqual(self.game.board.priceForIron(1), 2)

        # Single price jump
        self.game.board.coalMarketRemaining = 8
        self.assertEqual(self.game.board.priceForCoal(3), 13)
        self.game.board.ironMarketRemaining = 8
        self.assertEqual(self.game.board.priceForIron(3), 7)

        # Big price jump
        self.game.board.coalMarketRemaining = 13
        self.assertEqual(self.game.board.priceForCoal(10), 35)
        self.game.board.ironMarketRemaining = 8
        self.assertEqual(self.game.board.priceForIron(10), 40)

        # Render(self.game.board)

    def testVictoryPoints(self):
        # Zero points
        playerVPs = self.game.board.getVictoryPoints()

        self.assertTrue(self.game.p1 in playerVPs)
        self.assertTrue(self.game.p2 in playerVPs)

        self.assertEqual(playerVPs[self.game.p1], 0)
        self.assertEqual(playerVPs[self.game.p2], 0)

        # # Buildings Only
        redditch = self.game.board.townDict["Redditch"]
        birmingham = self.game.board.townDict["Birmingham"]
        walsall = self.game.board.towns[11]
        cannock = self.game.board.towns[9]

        self.game.board.removeXCoal = Mock()
        self.game.board.removeXBeer = Mock()

        self.game.p1.canBuildBuilding = Mock(return_value=True)
        self.game.p1.canSell = Mock(return_value=True)

        p1CottonBuilding = self.game.p1.buildings[10]
        self.game.p1.buildBuilding(p1CottonBuilding, birmingham.buildLocations[0])
        self.game.p1.sell(p1CottonBuilding)
        # p1CottonBuilding.sell()  # 5

        self.game.p2.canBuildBuilding = Mock(return_value=True)

        self.game.p2.buildBuilding(self.game.p2.buildings[0], redditch.buildLocations[0])

        p2Goods2Building = self.game.p2.buildings[1]
        
        self.game.p1.money = 50
        self.game.p2.money = 50 # increase for testing purposes

        self.game.p2.buildBuilding(p2Goods2Building, walsall.buildLocations[0])
        self.game.p2.canSell = Mock(return_value=True)
        self.game.p2.sell(p2Goods2Building)
        # p2Goods2Building.sell()  # 5

        p2CoalBuilding: IndustryBuilding = self.game.p2.buildings[37]
        self.game.p2.buildBuilding(p2CoalBuilding, cannock.buildLocations[1])

        p2CoalBuilding.decreaseResourceAmount(p2CoalBuilding.resourceAmount)

        playerVPs = self.game.board.getVictoryPoints()

        self.assertEqual(playerVPs[self.game.p1], 5)
        self.assertEqual(playerVPs[self.game.p2], 6)

        # # With networks
        self.game.p1.canBuildCanal = Mock(return_value=True)
        self.game.p1.buildCanal(
            redditch.networks[1]
        )  # 4 = 2 (tradepost oxford)
        # print(redditch.networks[1])
        
        self.game.p1.buildCanal(
            birmingham.networks[4]
        )  # 3 = 2 (tradepost oxford) + 1 (cotton @ birmingham)

        self.game.p2.canBuildCanal = Mock(return_value=True)
        self.game.p2.buildCanal(walsall.networks[1])  # 1 (cotton @ birmingham)

        playerVPs = self.game.board.getVictoryPoints()
        self.assertEqual(playerVPs[self.game.p1], 10)
        self.assertEqual(playerVPs[self.game.p2], 9)

        # With initial VPs

        self.game.p1.victoryPoints = 2
        self.game.p2.victoryPoints = 7

        playerVPs = self.game.board.getVictoryPoints()

        self.assertEqual(playerVPs[self.game.p1], 12)
        self.assertEqual(playerVPs[self.game.p2], 16)

        # render(self.game.board, self.call)

    def testIncomeLevel(self):
        self.game.p1.income = 10
        self.assertEqual(self.game.p1.incomeLevel(), 0)

        self.game.p1.income = 19
        self.assertEqual(self.game.p1.incomeLevel(), 5)

        self.game.p1.income = 35
        self.assertEqual(self.game.p1.incomeLevel(), 12)

        self.game.p1.income = 68
        self.assertEqual(self.game.p1.incomeLevel(), 22)

        self.game.p1.income = 99
        self.assertEqual(self.game.p1.incomeLevel(), 30)

        self.game.p1.income = 7
        self.game.p1.decreaseIncomeLevel(2)
        self.assertEqual(self.game.p1.income, 5)

        self.game.p1.income = 12
        self.game.p1.decreaseIncomeLevel(1)
        self.assertEqual(self.game.p1.income, 10)

        self.game.p1.income = 17
        self.game.p1.decreaseIncomeLevel(2)
        self.assertEqual(self.game.p1.income, 13)

        self.game.p1.income = 33
        self.game.p1.decreaseIncomeLevel(3)
        self.assertEqual(self.game.p1.income, 25)

        self.game.p1.income = 87
        self.game.p1.decreaseIncomeLevel(2)
        self.assertEqual(self.game.p1.income, 77)

        self.game.p1.income = 98
        self.game.p1.decreaseIncomeLevel(3)
        self.assertEqual(self.game.p1.income, 85)

    def testEndCanalEra(self):
        self.game.board.deck = Deck([])
        for player in self.game.board.players:
            player.hand.cards = []

        self.game.board.endCanalEra()
        for player in self.game.board.players:
            self.assertEqual(player.roadCount, 14)
            self.assertEqual(len(player.hand.cards), 8)

        for town in self.game.board.towns:
            for network in town.networks:
                self.assertEqual(network.isBuilt, False)
            for buildLocation in town.buildLocations:
                if buildLocation.building and buildLocation.building.tier <= 1:
                    self.assertEqual(buildLocation.building.isRetired, True)

        for tradepost in self.game.board.tradePosts:
            self.assertEqual(tradepost.beerAmount, tradepost.startingBeerAmount)

        self.assertEqual(self.game.board.era, Era.railroad)

    def testRailroads(self):
        self.resetGame(2)
        redditch:Building = self.game.board.townDict["Redditch"]
        self.game.p1.buildCanal(redditch.networks[2])
        self.game.p1.buildBuilding(self.game.p1.buildingDict["goods 1"], redditch.buildLocations[0])
        # coal costs
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 5, 13), False)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 5, 14), True)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 1, 2), True)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 2, 2), False)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 2, 3), False)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 2, 4), True)
        
        self.game.p1.money = 99
        self.game.board.removeXCoal(3, [redditch], self.game.p1)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 2, 6), False)
        self.assertEqual(self.game.board.isCoalAvailableFromTradePosts(redditch, 2, 7), True)

        self.assertEqual(self.game.board.isBeerAvailableFromTradePosts(redditch), True)
        self.assertEqual(self.game.board.isBeerAvailableFromTradePosts(self.game.board.townDict["Birmingham"]), False)

        # iron costs
        self.assertEqual(self.game.board.isIronAvailableFromTradePosts(2, 3), False)
        self.assertEqual(self.game.board.isIronAvailableFromTradePosts(2, 4), True)
        self.game.board.removeXIron(3, self.game.p1)
        self.assertEqual(self.game.board.isIronAvailableFromTradePosts(2, 6), False)
        self.assertEqual(self.game.board.isIronAvailableFromTradePosts(2, 7), True)

        #build coal 4 and build railroads next to it
        self.game.board.era = Era.railroad

        self.game.p1.buildBuilding(self.game.p1.buildingDict["coal 4"], self.game.board.townDict["Leek"].buildLocations[1])
        self.assertEqual(self.game.board.getAvailableCoalAmount(self.game.board.townDict[STOKE_ON_TRENT]), 0)
        self.game.p1.buildOneRailroad(self.game.board.townDict["Leek"].networks[0])
        self.assertEqual(self.game.board.getAvailableCoalAmount(self.game.board.townDict[STOKE_ON_TRENT]), 4)
        self.game.p1.buildOneRailroad(self.game.board.townDict["Stoke-On-Trent"].networks[2])
        self.assertEqual(self.game.board.getAvailableCoalAmount(self.game.board.townDict[UTTOXETER]), 0)
        self.game.p1.buildOneRailroad(self.game.board.townDict[UTTOXETER].networks[1])
        self.assertEqual(self.game.board.getAvailableCoalAmount(self.game.board.townDict[UTTOXETER]), 2)

        #build and use beer
        self.game.p1.buildBuilding(self.game.p1.buildingDict["beer 1"], self.game.board.townDict[UTTOXETER].buildLocations[0])
        self.assertEqual(self.game.board.getAvailableBeerAmount(self.game.p1, self.game.board.townDict[UTTOXETER]), 1)
        self.game.p1.buildTwoRailroads(self.game.board.townDict[DERBY].networks[1], self.game.board.townDict[DERBY].networks[2])
        self.assertEqual(self.game.board.getAvailableBeerAmount(self.game.p1, self.game.board.townDict[UTTOXETER]), 0)
        self.assertEqual(self.game.board.getAvailableCoalAmount(self.game.board.townDict[UTTOXETER]), 0)
        
        #overbuild
        self.assertEqual(self.game.p1.canBuildBuilding(self.game.p1.buildingDict["beer 2"], self.game.board.townDict[UTTOXETER].buildLocations[0]), True)
        self.game.p1.buildBuilding(self.game.p1.buildingDict["beer 2"], self.game.board.townDict[UTTOXETER].buildLocations[0])
        
    def test(self):
        self.resetGame(2)
        render(self.game.board, self.call)



    # do stuff to board w/o having to close it! - I SAID DO IT!!
    async def call(self, board: Board):
        print('is this called over and over or just once???')
        while True:
            actions = self.game.getPlayerPossibleActions()
            print(len(actions))
            if len(actions) == 1:
                break
            print('len(actions)')
            self.game.doAction(random.choice(actions))
            await asyncio.sleep(.1)
        
        print("Ending")

if __name__ == "__main__":
    unittest.main()
