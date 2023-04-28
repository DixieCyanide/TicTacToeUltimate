import math
import asyncio
import discord
from discord.ext import commands
import sql

# TODO: main funcsions:
# TODO: 1) grid creation - DONE
# TODO: 2) x,o placement - DONE
# TODO: 3) player registarion - DONE
# TODO: 4) win detection - DONE 
# TODO: 5) target line size - DONE
# TODO: 6) exception catchers - partially done
# TODO: 7) fog of war (setting)
# TODO: 8) customization (setting)
# TODO: 9) standart settings (setting) - partially done
# TODO: 10) line numbers on sides like on chess board (setting) (sponge#4716)
# TODO: 11) optimize win detection (#4)
# TODO: 12) switch sides (sponge#4716)


TOKEN = ""
prefix = "//"
testChannel = 

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix = prefix, intents = intents)

default_win_length = 3
default_y_size = 3
default_x_size = 3

emptySpot = "."

gameStates = {}
gameSettings = {}
gameVisualSettings = {}
gameTurns = {}
gamePlayers = {}


@bot.event
async def on_guild_join(guild):                                                 # adds new server to database
    serverID = guild.id
    sql.CreateRow(serverID)
    return


@bot.command(name = "start")
async def StartGame(ctx, size = None, setWinLength:int = None):
    global turn

    global gameStates
    global gameSettings
    global gameTurns

    grid = []
    serverID = ctx.guild.id
    playerID = ctx.author.id

    try:
        await RemoveGame(serverID)
    except:
        print("first start")                                                    # !for testing purposes

    try:
        winLength = int(setWinLength)
    except:
        winLength = default_win_length              # TODO: grab default values from sql
    
    try:
        size.split("x")
        x_size, y_size = size.split("x")
        x_size = int(x_size)
        y_size = int(y_size)
        grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
        await UpdateGameSettings(x_size, y_size, winLength, serverID)
    except:
        x_size = default_x_size
        y_size = default_y_size
        grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
        await UpdateGameSettings(x_size, y_size, winLength, serverID)

    turn = 0
    await UpdateGameState(grid, serverID)
    await UpdateGameTurn(turn, serverID)
    await AddGamePlayers(ctx, playerID, serverID)
    await PrintGrid(ctx, grid)
    return


@bot.command(name = "set")
async def GameTurn(ctx, *, coords = None):
    playerID = ctx.author.id
    serverID = ctx.guild.id
    grid = gameStates[serverID]
    players = gamePlayers[serverID]
    turn = gameTurns[serverID]

    if(playerID != players[0] and playerID != players[1]):
        await ctx.send("You are not registered for this game!")
        return

    if(players[turn] != playerID):
        await ctx.send("This is not your turn!")
        return
    
    try:
        x, y = coords.split(" ")
        int(x)
        int(y)
    except:
        await ctx.send("Type two coordinates please.")
        return

    if(int(x) > len(grid)):
        await ctx.send("Out of bounds!")
        return

    if(int(y) > len(grid[0])):
        await ctx.send("Out of bounds!")
        return
    
    x = int(x) - 1
    y = int(y) - 1

    await ChangeState(ctx, x, y, serverID)
    await PrintGrid(ctx, grid)
    await WinDetection(ctx, serverID)

    return


@bot.command(name = "register")
async def Registration(ctx):
    serverID = ctx.guild.id
    playerID = ctx.author.id
    await AddGamePlayers(ctx, playerID, serverID)
    return


async def PrintGrid(ctx, grid):
    output = []

    for i in grid:
        gridLine = "".join(i) + "\n"
        output.append(gridLine)
    
    output = "".join(output)
    await ctx.send("```\n" + output + "\n```")
    return


async def ChangeState(ctx, x, y, serverID):
    global gameStates
    global gameTurns
    
    grid = gameStates[serverID]
    turn = gameTurns[serverID]
    cell = grid[x][y]

    if(cell != emptySpot):
        await ctx.send("This spot is already taken, choose another one please.")
        return
    
    if(turn == 0):
        grid[x][y] = "X"
        turn = 1
    elif(turn == 1):
        grid[x][y] = "O"
        turn = 0

    gameStates[serverID] = grid
    gameTurns[serverID] = turn
    return


async def WinDetection(ctx, serverID):
    gameSetting = gameSettings[serverID]
    winLength = gameSetting[2]
    grid = gameStates[serverID]

    borderSize = math.floor((winLength / 2))
    x_size = len(grid) - borderSize
    y_size = len(grid[0]) - borderSize

    for i in range(borderSize, x_size):                                         #general/core checking
        for j in range(borderSize, y_size):
            if(grid[i][j] != emptySpot):
                await HorizontalWinDetection(i, j, borderSize, winLength, serverID, ctx)
                await VerticalWinDetection(i, j, borderSize, winLength, serverID, ctx)
                await LRdiagonalWinDetection(i, j, borderSize, winLength, serverID, ctx)
                await RLdiagonalWinDetection(i, j, borderSize, winLength, serverID, ctx)

    for i in range(-borderSize, borderSize):                                    #horizontal border checking
        for j in range(borderSize, y_size):
            if(grid[i][j] != emptySpot):
                await HorizontalWinDetection(i, j, borderSize, winLength, serverID, ctx)

    for i in range(borderSize, x_size):                                         #vertical border checking
        for j in range(-borderSize, borderSize):
            if(grid[i][j] != emptySpot):
                await VerticalWinDetection(i, j, borderSize, winLength, serverID, ctx)

    return


async def HorizontalWinDetection(x, y, borderSize, winLength, serverID, ctx):
    try:                                                                        # not a great thing, but i need it
        grid = gameStates[serverID]
    except:
        pass
    neighbours = 0

    for i in range (-borderSize, borderSize + 1):
        if(grid[x][y + i] == grid[x][y]):
            neighbours += 1

    if(neighbours == winLength):
        await WinAnnounce(ctx, serverID)

    return


async def VerticalWinDetection(x, y, borderSize, winLength, serverID, ctx):
    try:                                                                        # not a great thing, but i need it
        grid = gameStates[serverID]
    except:
        pass
    neighbours = 0

    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        await WinAnnounce(ctx, serverID)

    return


async def LRdiagonalWinDetection(x, y, borderSize, winLength, serverID, ctx):
    try:                                                                        # not a great thing, but i need it
        grid = gameStates[serverID]
    except:
        pass
    neighbours = 0

    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y + i] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        await WinAnnounce(ctx, serverID)

    return


async def RLdiagonalWinDetection(x, y, borderSize, winLength, serverID, ctx):
    try:                                                                        # not a great thing, but i need it
        grid = gameStates[serverID]
    except:
        pass
    neighbours = 0

    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y - i] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        await WinAnnounce(ctx, serverID)

    return


async def WinAnnounce(ctx, serverID):
    winner = ctx.author.mention
    await ctx.send("Winner is: " + winner + " !")
    await asyncio.sleep(1)
    await RemoveGame(serverID)
    return


async def UpdateGameState(grid, serverID):
    global gameStates
    gameStates[serverID] = grid
    return


async def UpdateGameTurn(turn, serverID):
    global gameTurns
    gameTurns[serverID] = turn
    return


async def UpdateGameSettings(x, y, winLength, serverID):
    global gameSettings
    settings = [x, y, winLength]
    gameSettings[serverID] = settings
    return


async def AddGamePlayers(ctx, playerID, serverID):
    global gamePlayers
    
    try:
        players = gamePlayers[serverID]
        if(playerID == players[0]):
            await ctx.send("You are already registered for this game.")
            return
        elif(playerID == players[1]):
            await ctx.send("Game is full already!")
            return
        players[1] = playerID
        gamePlayers[serverID] = players
        await ctx.send("You have registered for a game.")
    except:
        players = [None] * 2
        players[0] = playerID
        gamePlayers[serverID] = players
        await ctx.send("You have registered for a game.")
    
    return


async def SwitchGamePlayers():
                                            # TODO
    return


async def RemoveGame(serverID):
    global gameStates
    global gameSettings
    global gameTurns
    global gamePlayers
    gameStates.pop(serverID)
    gameSettings.pop(serverID)
    gameTurns.pop(serverID)
    gamePlayers.pop(serverID)
    return


bot.run(TOKEN)
