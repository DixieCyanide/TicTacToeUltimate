import math
import discord
from discord.ext import commands

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

grid = []
turn = 0
isWin = False
winner = None
winLength = None

players = [None] * 2
isRegClosed = False

emptySpot = "."

@bot.command(name = "start")
async def StartGame(ctx, size = None, setWinLength:int = None):
    global grid
    global turn
    global winLength
    global players

    grid = []

    playerID = ctx.author.id
    players[0] = playerID
    await ctx.send("You have registered for a game.")

    try:
        winLength = int(setWinLength)
    except:
        winLength = default_win_length
    
    try:
        size.split("x")
    except:
        grid = [[emptySpot for y in range(default_y_size)] for x in range(default_x_size)]
        await PrintGrid(ctx)
        return

    x_size, y_size = size.split("x")
    x_size = int(x_size)
    y_size = int(y_size)
    turn = 0

    grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
    await PrintGrid(ctx)
    return

@bot.command(name = "set")
async def GameTurn(ctx, *, coords = None):
    playerID = ctx.author.id

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

    await ChangeState(ctx, x, y)
    await PrintGrid(ctx)
    await WinDetection()

    if(isWin):
        await WinAnnounce(winner)

    return

@bot.command(name = "register")
async def Registration(ctx):
    global players

    playerID = ctx.author.id

    if(players[1] == None):
        players[1] = playerID
    elif(players[1] == playerID):
        await ctx.send("You are already registered for this game.")
        return
    else:
        await ctx.send("Game is full already!")
        return
    
    await ctx.send("You have registered for a game.")
    return

async def PrintGrid(ctx):
    output = []

    for i in grid:
        gridLine = "".join(i) + "\n"
        output.append(gridLine)
    
    output = "".join(output)
    await ctx.send("```\n" + output + "\n```")
    return

async def ChangeState(ctx, x, y):
    global grid
    global turn
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
    return

async def WinDetection():
    borderSize = math.floor((winLength / 2))
    x_size = len(grid) - borderSize
    y_size = len(grid[0]) - borderSize

    for i in range(borderSize, x_size):                                         #general/core checking
        for j in range(borderSize, y_size):
            if(grid[i][j] != emptySpot):
                await HorizontalWinDetection(i, j, borderSize)
                await VerticalWinDetection(i, j, borderSize)
                await LRdiagonalWinDetection(i, j, borderSize)
                await RLdiagonalWinDetection(i, j, borderSize)

    for i in range(-borderSize, borderSize):                                    #horizontal border checking
        for j in range(borderSize, y_size):
            if(grid[i][j] != emptySpot):
                await HorizontalWinDetection(i, j, borderSize)

    for i in range(borderSize, x_size):                                         #vertical border checking
        for j in range(-borderSize, borderSize):
            if(grid[i][j] != emptySpot):
                await VerticalWinDetection(i, j, borderSize)

    return

async def HorizontalWinDetection(x, y, borderSize):
    global isWin
    global winner
    neighbours = 0
    for i in range (-borderSize, borderSize + 1):
        if(grid[x][y + i] == grid[x][y]):
            neighbours += 1

    if(neighbours == winLength):
        isWin = True
        winner = grid[x][y]

    return

async def VerticalWinDetection(x, y, borderSize):
    global isWin
    global winner
    neighbours = 0
    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        isWin = True
        winner = grid[x][y]

    return

async def LRdiagonalWinDetection(x, y, borderSize):
    global isWin
    global winner
    neighbours = 0
    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y + i] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        isWin = True
        winner = grid[x][y]

    return

async def RLdiagonalWinDetection(x, y, borderSize):
    global isWin
    global winner
    neighbours = 0
    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y - i] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        isWin = True
        winner = grid[x][y]

    return

async def WinAnnounce(ctx, winner):
    global isWin
    global players

    await ctx.send("Winner is: " + players[turn])
    isWin = False
    players = [None] * 2

    return

bot.run(TOKEN)
