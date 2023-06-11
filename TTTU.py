import math
import discord
from discord import Option
from discord.ext import commands
import datetime as dt
import sql

# TODO: main funcsions:
# TODO: 1) grid creation - DONE
# TODO: 2) x,o placement - DONE
# TODO: 3) player registarion - DONE
# TODO: 4) win detection - DONE 
# TODO: 5) target line size - DONE
# TODO: 6) exception catchers - partially done
# TODO: 7) fog of war (setting) - DONE
# TODO: 8) customization (setting) - DONE
# TODO: 9) standart settings (setting) - DONE
# TODO: 10) line numbers on sides like on chess board (setting) (sponge#4716) - DISMISSED
# TODO: 11) optimize win detection (#4) ???
# TODO: 12) switch sides (sponge#4716) - DONE
# TODO: 13) console debug - partially done
# TODO: 14) slash commands - DONE
# TODO: 15) help command - DONE
# TODO: 16) restore default values command - DONE
# TODO: 17) make both slash and prefix commands - DONE

TOKEN = ""
prefix = "//"

intents = discord.Intents.default()                                             # TODO: i think i should remove it and configure on website
intents.message_content = True
intents.messages = True

bot = commands.Bot(
    command_prefix = prefix, 
    intents = intents, 
    help_command = None
    )                    

show_x_size = 3                                                                 # default values for first turn with fogofwar
show_y_size = 3                                                                 # for fogofwar

gameStates = {}                                                                 # holds game grid ([[o],[o]])
gameSettings = {}                                                               # holds grid size and winlength ([x, y, winLength])
gameFogOfWar = {}                                                               # holds disclosed area size ([x, y])
gameVisualSettings = {}                                                         # holds visuals for grid ([Xsign, Osign, emptySpot, isFogOfWar])
gameTurns = {}                                                                  # holds turn and if it's possible to switch sides ([bool, bool])
gamePlayers = {}                                                                # holds players id's (default: [player started, player registered])


@bot.event
async def on_guild_join(guild):                                                 # adds new server to database
    serverID = guild.id
    sql.CreateRow(serverID)
    print(f"Added new server ({serverID}).")
    return


@bot.slash_command(name = "help", description = "Help.")
async def Help(ctx):

    helpEmbed = discord.Embed(                                                  # this syntax triggers my whole human being
        title = "__Commands__",
        color = discord.Color.magenta())
    
    helpEmbed.add_field(
        name = "//start",
        value = "Starts new game.",
        inline = False)
    helpEmbed.add_field(
        name = "//set",
        value = "Places your sign on field.",
        inline = False)
    helpEmbed.add_field(
        name = "//register",
        value = "Registers you for started game.",
        inline = False)
    helpEmbed.add_field(
        name = "//stop",
        value = "Stops current game.",
        inline = False)
    helpEmbed.add_field(
        name = "//switch",
        value = "Switches sides of registered people once per game.",
        inline = False)
    helpEmbed.add_field(
        name = "//settings",
        value = "Shows settings for current server.",
        inline = False)
    helpEmbed.add_field(
        name = "//setup",
        value = "Lets you change settings.",
        inline = False)
    helpEmbed.add_field(
        name = "//reset",
        value = "Resets server settings to default ones.",
        inline = False)
    helpEmbed.add_field(
        name = "",
        value = "",
        inline = False)
    helpEmbed.add_field(
        name = "Github link:",
        value = "https://github.com/DixieCyanide/TicTacToeUltimate",
        inline = False)

    await ctx.respond(embed = helpEmbed)
    return


@bot.slash_command(name = "start", description = "Starts new game.")
async def SlashStartGame(
        ctx,
        size:         Option(str, description = "Field size",           required = False),
        setwinlength: Option(int, description = "Size of winning line", required = False)
        ):
    await StartGame(ctx, size, setwinlength)


@bot.command(name = "start", description = "Starts new game.")
async def StartGame(ctx, size: str, setwinlength: int):
    
    global gameStates
    global gameSettings
    global gameFogOfWar
    global gameTurns

    serverID = ctx.guild.id
    playerID = ctx.author.id

    grid = []
    serverSettings = await GetServerSettings(serverID)
    default_size = serverSettings[0]
    default_win_length = serverSettings[1]                                      # grabbing default settings from sql
    isFogOfWar = serverSettings[2]
    Xsign = serverSettings[3]
    Osign = serverSettings[4]
    emptySpot = serverSettings[5]

    try:                                                                        # if game was not stopped this will prevent weird things that could happen.
        await RemoveGame(serverID)
    except:
        pass

    if(isFogOfWar):
        gameFogOfWar[serverID] = [show_x_size, show_x_size]                     # setting default reveal size

    try:
        winLength = int(setwinlength)
    except:
        winLength = default_win_length

    try:
        size.split("x")
        x_size, y_size = size.split("x")
        x_size = int(x_size)
        y_size = int(y_size)

        if(x_size > 40 or y_size > 40 or x_size < 3 or y_size < 3):             # checks for minimum and maximum grid size
            await ctx.send("You set size wrongly. Using default size settings.")
            raise Exception("Field is out of bounds! (3x3 - 40x40)")
        
        grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
        await UpdateGameSettings(x_size, y_size, winLength, serverID)
    except:
        x_size, y_size = default_size.split("x")
        x_size = int(x_size)
        y_size = int(y_size)
        grid = [[emptySpot for y in range(y_size)] for x in range(x_size)]
        await UpdateGameSettings(x_size, y_size, winLength, serverID)

    turn = [0, 1]
    await UpdateGameState(grid, serverID)
    await UpdateGameTurn(turn, serverID)
    await UpdateGameVisualSettings(Xsign, Osign, emptySpot, isFogOfWar, serverID)
    await AddGamePlayers(ctx, playerID, serverID)
    await PrintGrid(ctx, serverID, grid)

    print(await ShowTime() + f"Game started at ({serverID}) SERVER with ({x_size}x{y_size}) SIZE and ({winLength}) WINLENGTH")

    return


@bot.slash_command(name = "set", description = "Places sign.")
async def SlashGameTurn(ctx, 
        x: Option(int, description = "Select row",    required = True, min_value = 1, max_value = 40),
        y: Option(int, description = "Select column", required = True, min_value = 1, max_value = 40)
        ):
    await GameTurn(ctx, x, y)


@bot.command(name = "set", description = "Places sign.")
async def GameTurn(ctx, x: int, y: int):
    
    playerID = ctx.author.id
    serverID = ctx.guild.id
    
    try:
        grid = gameStates[serverID]
        players = gamePlayers[serverID]
        turn = gameTurns[serverID]
        isFogOfWar = gameVisualSettings[serverID][3]
    except:
        await ctx.respond("Game is not started yet.")
        return

    if(playerID != players[0] and playerID != players[1]):
        await ctx.respond("You are not registered for this game!")
        return

    if(players[turn[0]] != playerID):
        await ctx.respond("This is not your turn!")
        return
    
    try:
        int(x)
        int(y)
    except:
        await ctx.respond("Type two coordinates please.")
        return                                                                  # TODO: probably useless now

    if(int(x) > len(grid) or int(y) > len(grid[0])):
        await ctx.respond("Out of bounds!")
        return
    
    if(isFogOfWar):
        fog_x_size = gameFogOfWar[serverID][0]
        fog_y_size = gameFogOfWar[serverID][1]

        if(int(x) > fog_x_size):
            fog_x_size = int(x)

        if(int(y) > fog_y_size):
            fog_y_size = int(y)
        
        await UpdateGameFogOfWar(fog_x_size, fog_y_size, serverID)
    
    x = int(x) - 1
    y = int(y) - 1

    await ChangeState(ctx, x, y, serverID)
    await PrintGrid(ctx, serverID, grid)
    await WinDetection(ctx, serverID)
    return


@bot.slash_command(name = "register", description = "Registers you for a game.")
async def SlashRegistration(ctx):
    await Registration(ctx)


@bot.command(name = "register", description = "Registers you for a game.")
async def Registration(ctx):
    serverID = ctx.guild.id
    playerID = ctx.author.id

    try:
        players = gamePlayers[serverID]
    except:
        await ctx.respond("Game is not started yet.")
        return
    
    await AddGamePlayers(ctx, playerID, serverID)
    return


@bot.slash_command(name = "stop", description = "Stops current game.")
async def SlashStopGame(ctx):
    await StopGame(ctx)


@bot.command(name = "stop", description = "Stops current game.")
async def StopGame(ctx):
    serverID = ctx.guild.id
    await RemoveGame(serverID)
    await ctx.respond("Game stopped.")
    return


@bot.slash_command(name = "switch", description = "Switch sides.")
async def SlashSwitchGamePlayers(ctx):
    await SwitchGamePlayers(ctx)


@bot.command(name = "switch", description = "Switch sides.")
async def SwitchGamePlayers(ctx):
    global gamePlayers

    serverID = ctx.guild.id
    try:
        turn = gameTurns[serverID]
        isPossible = turn[1]
        players = gamePlayers[serverID]
    except:
        await ctx.respond("Game is not started yet.")
        return

    if(isPossible == 0):
        await ctx.respond("It's not possible to switch sides any more.")
        return
    
    tempContainer = players[0]
    players[0] = players[1]
    players[1] = tempContainer
    tempContainer = None
    turn[1] = 0
    gamePlayers[serverID] = players
    await UpdateGameTurn(turn, serverID)
    await ctx.respond("You have switched sides successfully")

    print(await ShowTime() + f"Players switched at ({serverID}) SERVER")

    return


@bot.slash_command(name = "settings",description = "Shows settings.")
async def SlashShowSettings(ctx):
    await ShowSettings(ctx)


@bot.command(name = "settings",description = "Shows settings.")
async def ShowSettings(ctx):
    serverID = ctx.guild.id

    serverSettings = await GetServerSettings(serverID)
    default_size = serverSettings[0]
    default_win_length = serverSettings[1]
    isFogOfWar = bool(serverSettings[2])
    Xsign = serverSettings[3]
    Osign = serverSettings[4]
    emptySpot = serverSettings[5]

    if(isFogOfWar):
        isFogOfWarText = "Enabled"
    else:
        isFogOfWarText = "Disabled"

    settingsEmbed = discord.Embed(                                              # this syntax triggers my whole human being
        title = "__Server settings__",
        color = discord.Color.magenta())
    
    settingsEmbed.add_field(
        name = "Visual settings:",
        value = f"X sign: `{Xsign}` | O sign: `{Osign}` | Empty spot: `{emptySpot}`",
        inline = False)
    settingsEmbed.add_field(
        name = "Fog of war:",
        value = f"`{isFogOfWarText}`",
        inline = False)
    settingsEmbed.add_field(
        name = "Default game settings:",
        value = f"Size: `{default_size}` | Win length: `{default_win_length}`",
        inline = False)
    await ctx.respond(embed = settingsEmbed)                                    
    return                                                                      


@bot.slash_command(name = "setup", description = "Allows to change settings.")
async def SlashSettingsSetup(
        ctx,
        setting: Option(str, description = "Choose setting", required = True, choices = ["x", "o", "empty", "fog", "size", "length"]),
        value:   Option(str, description = "Imput value",    required = True),
        ):
    await SettingsSetup(ctx, setting, value)


@bot.command(name = "setup", description = "Allows to change settings.")
async def SettingsSetup(ctx, setting: str, value: str):
    serverID = ctx.guild.id
    
    try:
        element = setting
        newValue = value
    except:
        await ctx.respond("You set values wrong!")                              
        return
    
    newValueLen = len(newValue)

    if(newValueLen > 5 or newValueLen < 1):
        await ctx.respond("New value's size is too big.")
        return
    elif(element != "size" and newValueLen != 1):
        await ctx.respond("New values can only be single-symbol.")
        return
    elif(element == "length" and int(newValue) < 3):
        await ctx.respond("Win length is too small.")
        return
    elif(element == "fog"):
        if(newValue != "1" and newValue != "0"):
            ctx.respond("New value can be only 0 or 1")
            return
    elif(element == "size"):
        if(newValueLen < 3):
            await ctx.respond("New value's size is too small")
            return
        
        try:
            x, y = newValue.split("x")
            x = int(x)
            y = int(y)
            if(x > 40 or y > 40 or x < 3 or y < 3):
                await ctx.respond("Your values are out of bounds!")
                return
        except:
            await ctx.respond("New value's syntax is wrong!")
            return                                                              # many many exceptions... too many and i think it can be done more easily
    
    await UpdateServerSettings(element, newValue, serverID)
    await ctx.respond("Settings changed successfully.")
    return


@bot.slash_command(name = "reset", description = "Resets setting to default.")
async def SlashResetToDefault(ctx):
    await ResetToDefault(ctx)


@bot.command(name = "reset", description = "Resets setting to default.")
async def ResetToDefault(ctx):
    serverID = ctx.guild.id
    await UpdateServerSettings("x", "X", serverID)
    await UpdateServerSettings("o", "O", serverID)
    await UpdateServerSettings("empty", ".", serverID)
    await UpdateServerSettings("fog", 0, serverID)
    await UpdateServerSettings("size", "3x3", serverID)
    await UpdateServerSettings("length", 3, serverID)
    await ctx.respond("Default settings restored.")
    return


async def PrintGrid(ctx, serverID, grid):
    output = []
    isFogOfWar = gameVisualSettings[serverID][3]

    if(isFogOfWar):                                                             # if fog of war is enabled
        FogOfWarSize = gameFogOfWar[serverID]
        fog_x_size = FogOfWarSize[0]
        fog_y_size = FogOfWarSize[1]

        fogGrid = grid[:fog_x_size]
        for i in fogGrid:
            fogGridLine = "".join(i[:fog_y_size]) + "\n"
            output.append(fogGridLine)
    else:
        for i in grid:                                                          # if fog of war is disabled
            gridLine = "".join(i) + "\n"
            output.append(gridLine)
    
    output = "".join(output)
    await ctx.respond("```\n" + output + "\n```")
    return


async def ChangeState(ctx, x, y, serverID):
    grid = gameStates[serverID]
    visualSettings = gameVisualSettings[serverID]
    turn = gameTurns[serverID]
    
    cell = grid[x][y]
    Xsign = visualSettings[0]
    Osign = visualSettings[1]
    emptySpot = visualSettings[2]

    if(cell != emptySpot):
        await ctx.respond("This spot is already taken, choose another one please.")
        return
    
    if(turn[0] == 0):
        grid[x][y] = Xsign
        turn[0] = 1
    elif(turn[0] == 1):
        grid[x][y] = Osign
        turn[0] = 0

    await UpdateGameState(grid, serverID)
    await UpdateGameTurn(turn, serverID)
    return


async def WinDetection(ctx, serverID):
    grid = gameStates[serverID]
    gameSetting = gameSettings[serverID]
    visualSettings = gameVisualSettings[serverID]
    
    winLength = gameSetting[2]
    emptySpot = visualSettings[2]

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
        return
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
        return
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
        return
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
        return
    neighbours = 0

    for i in range (-borderSize, borderSize + 1):
        if(grid[x + i][y - i] == grid[x][y]):
            neighbours += 1
    
    if(neighbours == winLength):
        await WinAnnounce(ctx, serverID)

    return


async def WinAnnounce(ctx, serverID):
    winner = ctx.author.mention
    await ctx.send(f"Winner is: {winner}!")
    await RemoveGame(serverID)
    return


async def UpdateServerSettings(element, newValue, serverID):
    #time for big if-elif-else statement cuz python don't accept switch-case superiority
    column = None

    if(element == "x"):
        column = "Xsign"
    elif(element == "o"):
        column = "Osign"
    elif(element == "empty"):
        column = "EmptySign"
    elif(element == "fog"):
        column = "IsFogOfWar"
    elif(element == "size"):
        column = "DefaultGridSize"
    elif(element == "length"):
        column = "DefaultWinLength"
    else:
        print("Something went wrong during server settings update")
        return
    
    try:
        sql.UpdateData("ServerSettings", column, newValue, serverID)
    except:
        print("Couldn't update value in sql")

    return


async def UpdateGameState(grid, serverID):
    global gameStates
    gameStates[serverID] = grid
    return


async def UpdateGameFogOfWar(x, y, serverID):
    global gameFogOfWar
    gameFogOfWar[serverID] = [x, y]
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


async def GetServerSettings(serverID):
    default_size = sql.RetrieveData("ServerSettings", "DefaultGridSize  ", serverID)
    default_win_length = sql.RetrieveData("ServerSettings", "DefaultWinLength", serverID)                     # grabbing default settings from sql
    isFogOfWar = sql.RetrieveData("ServerSettings", "IsFogOfWar", serverID)
    Xsign = sql.RetrieveData("ServerSettings", "Xsign", serverID)
    Osign = sql.RetrieveData("ServerSettings", "OSign", serverID)
    emptySpot = sql.RetrieveData("ServerSettings", "EmptySign", serverID)
    return [default_size, default_win_length, isFogOfWar, Xsign, Osign, emptySpot]


async def UpdateGameVisualSettings(X_sign, O_sign, empty_Spot, isFogOfWar, serverID):
    global gameVisualSettings
    visualSettings = [X_sign, O_sign, empty_Spot, isFogOfWar]
    gameVisualSettings[serverID] = visualSettings
    return


async def AddGamePlayers(ctx, playerID, serverID):
    global gamePlayers
    
    try:
        players = gamePlayers[serverID]
        if(playerID == players[0]):
            await ctx.respond("You are already registered for this game.")
            return
        elif(playerID == players[1]):
            await ctx.respond("Game is full already!")
            return
        players[1] = playerID
        gamePlayers[serverID] = players
        await ctx.respond("You have registered for a game.")
        print(await ShowTime() + f"Second ({playerID}) PLAYER registered at ({serverID}) SERVER")
    except:
        players = [None] * 2
        players[0] = playerID
        gamePlayers[serverID] = players
        await ctx.respond("You have registered for a game.")
        print(await ShowTime() + f"First ({playerID}) PLAYER registered at ({serverID}) SERVER")
    
    return


async def RemoveGame(serverID):
    global gameStates
    global gameSettings
    global gameFogOfWar
    global gameVisualSettings
    global gameTurns
    global gamePlayers
    gameStates.pop(serverID)
    gameSettings.pop(serverID)
    try:
        gameFogOfWar.pop(serverID)
    except:
        pass
    gameVisualSettings.pop(serverID)
    gameTurns.pop(serverID)
    gamePlayers.pop(serverID)
    print(await ShowTime() + f"Game stopped at ({serverID}) SERVER")
    return


async def ShowTime():
    return ("[" + dt.datetime.now().strftime("%x %X") + "] ")


bot.run(TOKEN)
