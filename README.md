# Seminararbeit Sudoku

## Description
This paper deals with various solution strategies for the game Sudoku. The strategies are categorized into 3 different difficulty levels.
Accordingly, the game Sudoku was implemented using pygame to demonstrate various strategies (listed below).

## Installation & Start

### Install packages from requirements.txt
pip install -r requirements.txt

### Start from main.py
python main.py

## Features
### Toggle Candidates
Toggles all possible candidates for each cell. Candidates can be directly selected as an input, otherwise a number can be entered.

### Toggle Mistakes
Entered numbers are red colored if they violate the rules.

### Hints
There are 4 techniques implemented
* Naked Singles
* Hidden Singles
* Hidden Pairs
* X-Wing

"Show Hint" randomly selects one of the techniques and shows a random hint, if available.
The other hints are specifically for the techniques and also select one randomly 


## Preview
Initial game view: </br>
<img src="/images/sudoku_1.jpg" width="50%"></img>
</br></br></br>
Game view after toggling candidates and X-Wing hint.  </br>
<img src="/images/sudoku_2.jpg" width="50%"></img>
