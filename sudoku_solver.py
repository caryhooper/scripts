#!/usr/bin/python3
import sys

#Initialize the data structure to save progress
#9x9 board, array of arrays.
def initialize_board():
	board = list('.'*9)
	for i in range(0,len(board)):
		board[i] = list('?'*9)
	return board

#logic_board is an array of arrays with a set of numbers 1-9
#this init function also inputs the game board state and updates
#the logic board
def initialize_logic(gameboard):
	logicboard = list()
	for i in range(0,9):
		logicboard.append([])
		for j in range(0,9):
			logicboard[i].append(set())
			for k in range(0,9):
				logicboard[i][j].add(k+1)
	#print(logicboard)

	for i in range(0,len(gameboard)):
		for j in range(len(gameboard[i])):
			#Iterate through gameboard cells
			if gameboard[i][j] != '.':
				#If the number is known, remove all other numbers from the set
				gameNumber = gameboard[i][j]
				print(gameNumber)
				#Remove all but the one known number from the set.
				for k in range(1,len(gameboard)+1):
					if k != gameNumber:
						logicboard[i][j].remove(k)
	print(logicboard)
	return logicboard


def printBoard(board):
	#i is top to bottomn
	#j is left to right
	print("-" * 30 + "\n", end='')
	for i in range(0,len(board)):
		print("|", end='')
		for j in range(0,len(board[i])):
			print(" " + str(board[i][j]) + " ",end='')
			if j%3 == 2:
				print("|", end='')
		print("\n", end='')
		if i%3 == 2:
			print("" + "-"*30 + "\n", end='')

def squarePosition(pos):
	if pos == 0:
		offset = [1,2]
	elif pos == 1:
		offset = [-1,1]
	else:
		offset = [-2,-1]
	return offset

def rowLogic(gameboard,logicboard):
	#For each known cell, remove possiblity for other cells
	#horizontal, vertical, and square
	for i in range(0,len(gameboard)):
		for j in range(0,len(gameboard[i])):
			if gameboard[i][j] != '.':
				gameNumber = gameboard[i][j]
				#Horizontal.  For each (j,i), array[i][j] i is contstant


				#For each column (y), remove gameNumber from the set
				#i is rows, x are rows
				for y in range(0,len(gameboard[i])):
					#exception when (j,i) equals (y,i)
					if y != j:
						if gameNumber in logicboard[i][y]: #keeps row constant, change col
							logicboard[i][y].remove(gameNumber)
				#Vertical.   For each (j,i), array[i][j] j is contstant
				#j is columns, x are columns
				for x in range(0,len(gameboard[i])):
					if x != i:
						if gameNumber in logicboard[x][j]: #keep column constant, change row
							logicboard[x][j].remove(gameNumber) 
				#Within the box.  Fuck
				#For a given coordinate (j,i) , iterate through the coordinates around it (within the 3x3 box)
				#Treat all these the same.  1) Find where we are in the box.  
				#Do operations on the 8 possibilities in logicboard
				#Find horizontal position (j).  Super sloppy code :(
				horizontalPosition = j % 3 #column (x)
				verticalPosition = i % 3 #row (y)
				hOffset = squarePosition(horizontalPosition)
				vOffset = squarePosition(verticalPosition)

				absHorizontalPosition = [j,j+hOffset[0],j+hOffset[1]]
				absVerticalPosition = [i,i+vOffset[0],i+vOffset[1]]
				#absPosition arrays populated with three abs positions of the box
				#Iterate over those, but skip j,i ~ x,y, removing num from set
				for y in absVerticalPosition:
					for x in absHorizontalPosition:
						if i != y and j != x:
							#Do the thing... remove num from set
							if gameNumber in logicboard[y][x]:
								logicboard[y][x].remove(gameNumber)
	return logicboard

def updateGame(gameboard,logicboard):
	for i in range(0,len(logicboard)):
		for j in range(0,len(logicboard[i])):
			if len(logicboard[i][j]) == 1:
				foundNumber = logicboard[i][j].pop()
				print("Updating (" + str(j) + "," + str(i) + ") with: " + str(foundNumber))
				#printBoard(gameboard)
				gameboard[i][j] = foundNumber

	return gameboard

def checkFinished(gameboard):
	#Game is finished when no entries in gameboard are '.'
	finished = True
	for row in gameboard:
		if '.' in row:
			finished = False
	return finished



#####STOPPED HERE ###### trying to make this function smarter / give up after 2 rounds of same activity.
def easySolve(gameboard,logicboard):
	for rounds in range(0,99):
		print("Round " + str(rounds) + ":  FIGHT!!!")
		logicboard = rowLogic(gameboard,logicboard) #updated logicboard
		gameboard = updateGame(gameboard,logicboard) #updated gameboard
		#printBoard(gameboard)
		if checkFinished(gameboard):
			print("Congrats! The sudoku is solved after " + str(rounds) + " rounds.")
			printBoard(gameboard)
			sys.exit(0)
	return logicboard
	#No changes to logicboard between iterations?  complete!

def main():
	gameboard = initialize_board()
	gameboard = [ #easy difficulty
					[ 5 ,'.','.','.', 2 ,'.', 3 ,'.', 7 ],
					[ 3 , 2 ,'.','.','.', 9 , 8 ,'.', 1 ],
					['.','.', 1 , 7 , 3 ,'.','.','.','.'],
					['.', 8 , 4 , 3 ,'.','.','.', 9 ,'.'],
					['.', 5 ,'.', 9 ,'.', 2 ,'.', 3 ,'.'],
					['.', 3 ,'.','.','.', 1 , 6 , 2 ,'.'],
					['.','.','.','.', 4 , 7 , 5 ,'.','.'],
					[ 8 ,'.', 5 , 2 ,'.','.','.', 7 , 6 ],
					[ 6 ,'.', 2 ,'.', 9 ,'.','.','.', 3 ]
				]
	# gameboard = [ 	#medium difficulty // cant solve
	# 				[ 2 ,'.', 3 ,'.','.', 6 ,'.', 1 ,'.'],
	# 				['.','.', 6 , 7 ,'.', 8 , 4 ,'.','.'],
	# 				[ 4 ,'.','.', 3 ,'.','.','.', 6 ,'.'],
	# 				[ 7 , 2 ,'.','.', 9 ,'.', 3 ,'.','.'],
	# 				['.', 6 ,'.','.', 7 ,'.','.', 9 ,'.'],
	# 				['.','.', 5 ,'.', 8 ,'.','.', 7 , 2 ],
	# 				['.', 9 ,'.','.','.', 7 ,'.','.', 6 ],
	# 				['.','.', 2 , 5 ,'.', 9 , 7 ,'.','.'],
	# 				['.', 5 , '.', 4 ,'.','.', 9 ,'.', 3]
	# 			]
	# gameboard = [
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.'],
	# 				['.','.','.','.','.','.','.','.','.']l
	# 														]


	#Can't solve, maybe need to go 1-9 to find number location
	#Fuzz it up until it is solved
	#Need more logic techniques first
	#printBoard(gameboard)
	logicboard = initialize_logic(gameboard)
	gameboard = gameboard
	printBoard(gameboard)
	logicboard = easySolve(gameboard,logicboard)


	#After max logic rounds, if it isn't solved, we need to fuzz/guess numbers . 
	#Take logicboard, find sets with len() = 2
	#Choose one of the two and sub it into gameboard
	#Try to solve again.  If solved good! If not, try the other number.  
	#Keep trying 
	#Need a validate function for this to assure game rules aren't broken.
main()