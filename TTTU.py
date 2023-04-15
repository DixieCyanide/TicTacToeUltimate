import discord
from discord.ext import commands
from discord.utils import get

# TODO: bot settings:
# TODO: 1) element selection (bg, x, o)
# TODO: 2) for field larger than 3x3 - "fog of war"

# TODO: main funcsions:
# TODO: 1) grid creation
# TODO: 2) x,o placement - DONE
# TODO: 3) player registarion
# TODO: 4) win detection
# TODO: 5) exception catchers

TOKEN = ""
prefix = "//"
testChannel = 0

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix=prefix, intents=intents)

grid = []

turn = 0

@bot.command(name = "start")
async def startGame(ctx, *, size):
    global grid
    global turn
    x_size, y_size = size.split("x")
    x_size = int(x_size)
    y_size = int(y_size)
    grid = []
    emptySpot = "."
    turn = 0

    grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
    
    return

@bot.command(name = "test")                                                     # !Shows grid
async def TEST(ctx):
    channel = bot.get_channel(testChannel)
    await printGrid(grid, channel)

@bot.command(name = "testset")
async def TESTSET(ctx):
    channel = bot.get_channel(testChannel)
    grid[1][1] = "5"
    await printGrid(grid, channel)

@bot.command(name = "set")
async def gameTurn(ctx, *, coords):
    channel = bot.get_channel(testChannel)
    x, y = coords.split(" ")
    x = int(x) - 1
    y = int(y) - 1
    await changeState(x, y, grid, channel)
    await printGrid(grid, channel)
    return

async def printGrid(grid, channel):
    channel = channel
    output = []
    for i in grid:
        gridLine = "".join(i) + "\n"
        output.append(gridLine)
    output = "".join(output)
    await channel.send("```\n" + output + "\n```")
    return

async def changeState(x, y, grid, channel):
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

bot.run(TOKEN)
