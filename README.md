# Python Minesweeper Solver

A little side project.

The code is **REALLY** bad

## **SETUP**

**note!** This solver only works on Windows system

1. Download [Minesweeper X](https://minesweepergame.com/download/minesweeper-x.php)、[Arbiter](https://minesweepergame.com/download/arbiter.php), or any minesweeper game clone(Arbiter is recommended). Open the game.
2. Change the scale to 125% in display settings.
3. In terminal, run:
```
$ git clone https://github.com/jasonjustin/python-minesweeper-solver.git
$ cd python-minesweeper-solver
```

# **USAGE**

## **SYNOPSIS**

```
$ python solver.py [-m <mode>] [-t <times>] [-h | --help]
```

## **DESCRIPTION**

The solver will automatically find the game on screen and solve it.

It can play the game from the beginning, or finish the already started game.

**Note: The top left corner cell must be covered when run in the middle of the game**

The solver supports multi-game mode, user can specify the time. Statistics will be shown after all games are finished.

## **OPTIONS**

**`-h`  
`--help`**  
Show all the options.  

**`-m`  
`--mode`**  
Game mode, B for Beginner, I for Intermediate, E for Expert. Default is Expert mdoe.

**`-t`  
`--times`**  
Multi-game mode, default is one time.

TODO:
- Refactor
- Rewrite with all CSP solving (may be faster)
- Introduce [`Frontier Dynamic Programming`](https://www.youtube.com/watch?v=G2kd745uYuo)
