import math
import discord
from discord.ext import commands

# TODO: main funcsions:
# TODO: 1) grid creation - DONE
# TODO: 2) x,o placement - DONE
# TODO: 3) player registarion
# TODO: 4) win detection - DONE
# TODO: 5) target line size - DONE
# TODO: 6) exception catchers
# TODO: 7) fog of war (setting)
# TODO: 8) customization (setting)
# TODO: 9) something else my mind couldn't figure out


TOKEN = ""
prefix = "//"
testChannel = 

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

grid = []
turn = 0
winLength = 3
isWin = False
winner = None
emptySpot = "."

@bot.command(name = "start")
async def StartGame(ctx, *, size, setWinLength):                                              # TODO: add win length (target line size)
    global grid
    global turn
    global winLength

    channel = bot.get_channel(testChannel)

    winLength = int(setWinLength)
    x_size, y_size = size.split("x")
    x_size = int(x_size)
    y_size = int(y_size)
    grid = []
    turn = 0

    grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
    await PrintGrid(grid, channel)
    return

@bot.command(name = "test")                                                     # !Shows grid
async def TEST(ctx):
    channel = bot.get_channel(testChannel)
    await PrintGrid(grid, channel)

@bot.command(name = "test2")
async def TEST2(ctx, *, setWinLength):
    global winLength
    winLength = int(setWinLength)
    await WinDetection(grid)

@bot.command(name = "set")
async def gameTurn(ctx, *, coords):
    channel = bot.get_channel(testChannel)
    x, y = coords.split(" ")
    x = int(x) - 1
    y = int(y) - 1
    await ChangeState(x, y, grid, channel)
    await PrintGrid(grid, channel)
    await WinDetection(grid)
    return

async def PrintGrid(grid, channel):
    channel = channel
    output = []
    for i in grid:
        gridLine = "".join(i) + "\n"
        output.append(gridLine)
    output = "".join(output)
    await channel.send("```\n" + output + "\n```")
    return

async def ChangeState(x, y, grid, channel):
    global turn
    cell = grid[x][y]

    if(cell != "."):
        await channel.send("This spot is already taken, choose another one please.")
        return
    
    if(turn == 0):
        grid[x][y] = "X"
        turn = 1
    elif(turn == 1):
        grid[x][y] = "O"
        turn = 0
    return

async def WinDetection(grid):
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

    if(isWin):
        await WinAnnounce(winner)

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

async def WinAnnounce(winner):
    global isWin
    channel = bot.get_channel(testChannel)

    await channel.send("Winner is: " + winner)
    isWin = False

    return

bot.run(TOKEN)
