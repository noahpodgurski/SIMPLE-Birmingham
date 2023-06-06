from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Dict, List

from python.id import id
from python.print_colors import *

from .board import Board
import random

from .player import Player
from classes.cards.enums import CardName
from classes.buildings.enums import BuildingName, BuildingType
import time
from consts import (STOKE_ON_TRENT, LEEK, STONE, UTTOXETER, BELPER, DERBY, STAFFORD, CANNOCK, WALSALL, BURTON_UPON_TRENT, TAMWORTH,
                    WOLVERHAMPTON, COALBROOKDALE, DUDLEY, KIDDERMINSTER, WORCESTER, NUNEATON, BIRMINGHAM, COVENTRY, REDDITCH, BEER1, BEER2)
import itertools

class Game:
    """
    Game - keeps track of players, turn, board, player possible action generation
    
    :param: numPlayers
    :param: p1Name
    :param: p2Name
    :param: p3Name
    :param: p4Name
    """
    def __init__(self, numPlayers:int, p1Name:str, p2Name:str, p3Name:str=None, p4Name:str=None):
        self.id = id()
        self.board = Board(numPlayers)

        self.p1 = Player(p1Name, self.board)
        self.p2 = Player(p2Name, self.board)
        self.players = [self.p1, self.p2]
        if p3Name:
            self.p3 = Player(p3Name, self.board)
            self.players.append(self.p3)
        if p4Name:
            self.p4 = Player(p4Name, self.board)
            self.players.append(self.p4)


        self.playerTurnIndex = random.randint(0, numPlayers-1)

    def getPlayerPossibleActions(self):
        start = time.time()
        player = self.players[self.playerTurnIndex]

        possibleActions = []
        possibleBuildToBuildingName = {
            CardName.iron_works: BuildingName.iron,
            CardName.coal_mine: BuildingName.coal,
            CardName.brewery: BuildingName.beer,
            CardName.pottery: BuildingName.pottery,
            CardName.man_goods_or_cotton: BuildingName.goods,
        }

        ##### 1. BUILD

        # todo optimize for once network is built (can only build on network)
        # can also optimize by just iterating thru cards in hand first
        # for now, check all build locations
        for town in self.board.towns:
            for buildLocation in town.buildLocations:
                for possibleBuild in buildLocation.possibleBuilds:
                    if player.buildingDict.get(f"{possibleBuild.value} 1") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 1"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 1"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 2") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 2"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 2"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 3") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 3"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 3"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 4") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 4"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 4"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 5") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 5"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 5"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 6") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 6"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 6"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 7") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 7"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 7"], buildLocation])
                    elif player.buildingDict.get(f"{possibleBuild.value} 8") and \
                    player.canBuildBuilding(player.buildingDict[f"{possibleBuild.value} 8"], buildLocation):
                        possibleActions.append([player.buildBuilding, player.buildingDict[f"{possibleBuild.value} 8"], buildLocation])

        
        ##### 2. NETWORK
        for roadLocation in self.board.roadLocations:
            if player.canBuildCanal(roadLocation):
                possibleActions.append([player.buildCanal, roadLocation])

            if player.canBuildOneRailroad(roadLocation):
                possibleActions.append([player.buildOneRailroad, roadLocation])

            for r in self.board.roadLocations:
                if roadLocation.id != r.id:
                    if player.canBuildTwoRailroads(roadLocation, r):
                        possibleActions.append([player.buildTwoRailroads, roadLocation, r])

        ##### 3. DEVELOP
        for building in player.buildings:
            if player.canDevelopOne(building):
                possibleActions.append([player.developOne, building])
            
            for b in player.buildings:
                if building.id != b.id:
                    if player.canDevelopTwo(building, b):
                        possibleActions.append([player.developTwo, building, b])

        ##### 4. SELL
        activeBuildings = list(filter(lambda b: b.isActive, player.buildings))
        combos = []
        for i in range(2, len(activeBuildings)+1):
            combos.append(itertools.combinations(activeBuildings, i))

        for combo in combos:
            for buildingCombo in list(combo):
                if building.type == BuildingType.market and player.canSellMultiple(buildingCombo):
                    possibleActions.append([player.sellMultiple, buildingCombo])


        # for building in player.buildings:
        #     if building.type == BuildingType.market and player.canSell(building):
        #         possibleActions.append([player.sell, building])

        ##### 5. LOAN
        if player.canLoan():
            possibleActions.append([player.loan])

        ##### 6. SCOUT
        for card in player.hand.cards:
            if player.canScout(card):
                possibleActions.append([player.scout, card])

        ##### 7. PASS
        if player.canPassTurn():
            possibleActions.append([player.passTurn])

        # print(possibleActions[0:10])
        
        end = time.time()
        print(f"possible actions: {len(possibleActions)}. ({round((end - start)*1000)}ms to generate)")
        return possibleActions

    def doAction(self, actionArray):
        action = actionArray[0]
        args = actionArray[1:]
        action(*args)

        #take income

        # other player's turn
        self.playerTurnIndex += 1
        self.playerTurnIndex %= len(self.players)

