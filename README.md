# TicTacToeUltimate

Bot prefix: //

Bot commands:

//start (size) (win length)
  Starts a new game with applied setting.
  If you do not type any settings, default ones will be applied (you can setup them separately).
  Registers author for a game.
  Author will represent "X" side (can be switched, look at //switch)
  There can be only 1 game per server.
  If you type command during a game, game will be overwritten with new one.
  
//set (x) (y)
  Places your sign on selected spot if it's empty.
  Spot is being selected by typing it's coordinates:
    X for rows
    Y for columns
    
//register
  Registers author for a game with person who typed //start command.
  
//stop
  Stops a game despite it's state.
  
//switch
  Allows to switch sides for register players once before anyone types //set command.
  
//settings
  Shows default game settings and visual settings for server.
  
//setup (setting)
  Allow to change default game settings and visual settings.
  Temporarily case-sensetive!!!
  Variants:
  
  //setup x (value)
    Sets new visual symbol for side X.
    Value can only be single-character.
    Value can not be ' character.  (I'll try to fix it)
    ASCII characters are prefered.
      Example: //setup x X
    
  //setup o (value)
    Sets new visual symbol for side O.
    Value can only be single-character.
    Value can not be ' character.  (I'll try to fix it)
    ASCII characters are prefered.
      Example: //setup x O
    
  //setup empty (value)
    Sets new visual symbol for empty "background" spots.
    Value can only be single-character.
    Value can not be ' character.  (I'll try to fix it)
    ASCII characters are prefered.
      Example: //setup empty .
      
  //setup fog (value)
    Sets if game will have fog of war effect or not.
    Value can only be 0 or 1.
      Example: //setup fog 1
    
  //setup size (value)
    Sets default value for field size.
    Value can only be @x@.
    @ is a number in range from 3 to 40.
      Example: //setup size 10x15
    
  //setup length (value)
    Sets default value for ein length.
    Value can only be in range from 3 to 40.
      Example: //setup length 5
