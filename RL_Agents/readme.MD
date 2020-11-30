## RL Agents 


Different types of RL Agents used for this project are 

1. Max Damage Agent 
2. Random Player Agent 
3. Deep Q Neural Network(DQN) Agent
4. CEM Algorithm
5. SARSA Algorithm


## Environment Setup

1. Download Poke-env package [https://github.com/hsahovic/poke-env] using pip installation:

``` pip install keras-rl2==1.0.3 
    pip install poke-env 
```


2. Use the heroku application that uses Showdown Server open source version to create a copy of the game with our modified rules. 

Link: https://usc-pokemon-showdown.herokuapp.com/


Add this line to ```\poke-env\src\poke_env\server_configuration.py```

```
LocalhostServerConfiguration = ServerConfiguration(
   "usc-pokemon-showdown.herokuapp.com",
   "https://play.pokemonshowdown.com/action.php?"
)

```

