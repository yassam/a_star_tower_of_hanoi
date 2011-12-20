# A* for the Tower of Hanoi using 3 rods.
#
# I wrote this to work out how many steps needed for the optimal solution for
# the 4 disk case. This was part (c) of Q1 on the final of ai-class.com
# (Dec 2011).
# 
# Works on Python 2.7 (should work on earlier versions of Python - but haven't
# tested on them).
#
# Yasir Assam

import copy
import heapq
import sys

class State:
    """
    Represents a legal disk configuration in the Towers of Hanoi Game

    The number of rods is hardcoded to 3: 0-2 from left to right.
    The number of disks can vary from 1 upwards. A disk is identified by an
    integer >= 1, e.g. for the 4 disk game the disks are 1, 2, 3, 4 with 4
    being the largest and 1 the smallest.
    """
    def __init__(self, copyFrom=None):
        if copyFrom:
            self.rods = copy.deepcopy(copyFrom.rods)
        else:
            self.rods = [ [], [], [] ]

    def numDisksInRod(self, rodNum):
        return len(self.rods[rodNum])

    def nextStates(self):
        "Return list of all legal states that follow one step from this state"
        states = [ ]
        for rodNum, rod in enumerate(self.rods):
            if rod:
                diskToMove = rod[-1]
                for otherRodNum, otherRod in enumerate(self.rods):
                    # If another rod has no disks or the top disk is smaller
                    # than this disk, then we can move this disk on to it
                    if (otherRod is not rod and
                        (otherRod and otherRod[-1] > diskToMove or
                         not otherRod)):
                        newState = State(self)
                        newState.rods[rodNum].pop()
                        newState.rods[otherRodNum].append(diskToMove)
                        states.append(newState)
        return states
    
    def addDiskToRod(self, diskNum, rodNum):
        """
        Initialise state using this function repeatedly, one for each disk.
        Make sure you add disks in reverse order, e.g. disk 4 before disk 3
        (on any particular rod)
        """
        assert diskNum > 0
        assert rodNum >= 0 and rodNum <= 3
        assert self.rods and self.rods[-1] > diskNum or not self.rods
        self.rods[rodNum].append(diskNum)

    def __eq__(self, other):
        for rodNum, rod in enumerate(self.rods):
            if rod != other.rods[rodNum]:
                return False
        return True

    def maxDiskSize(self):
        "e.g. got the 4 disk game returns 4"
        return max(max(self.rods))

    def __hash__(self):
        "Hash function used for set container type to check quality"
        hash = 0
        shiftBy = self.maxDiskSize()
        for rodNum, rod in enumerate(self.rods):
            subHash = 0
            for disk in rod:
                subHash += 1 << (disk - 1)
            hash += subHash << (shiftBy * rodNum)
        return hash

    def __repr__(self):
        "Disk configuration in ASCII representation"
        maxDiskSize = self.maxDiskSize()
        fullRodWidth = maxDiskSize * 2 + 1
        ROD_GAP = 2
        numRods = len(self.rods)
        gridWidth = fullRodWidth * numRods + (numRods - 1) * ROD_GAP
        numLines = maxDiskSize
        charGrid = [ [' '] * gridWidth for i in range(numLines) ]
        for rod in range(numRods):
            rodX = rod * (fullRodWidth + ROD_GAP) + numLines
            for line in range(numLines):
                charGrid[line][rodX] = '|'
            for pos, disk in enumerate(self.rods[rod]):
                rodY = (maxDiskSize - 1) - pos
                for x in range(rodX - disk, rodX + disk + 1):
                    if x != rodX:
                        charGrid[rodY][x] = '_'
                    
        ret = '\n'
        for line in charGrid:
            ret += ''.join(line) + '\n'
        return ret + '\n'


class Path(list):
    """
    Just a list with two extras:
    
    * A cost function using heuristic
    * A less-than function used by the heapq container
    """
    def cost(self):
        """
        The cost is path length so far (number of steps) + heuristic (no. of
        disks left on left rod).

        NOTE: We don't include the zeroth step (the initial state) in the cost
        """
        if len(self) > 0:
            endOfPath = self[-1]
            heuristic = endOfPath.numDisksInRod(0)
            return len(self) - 1 + heuristic
        else:
            return 0
        
    def __lt__(self, other):
        return self.cost() < other.cost()

def graphSearch(initialState, goal):
    "Based on algorithm given in AI class"
    explored = set()
    initialPath = Path([initialState])
    frontier = [ ]
    # Priority queue
    heapq.heappush(frontier, initialPath)
    while True:
        if not frontier:
            return False
        # This is the 'remove_choice' line from the algorithm 
        # taught to us by Peter
        path = heapq.heappop(frontier)
        s = path[-1]
        explored.add(s)
        if s == goal:
            return path
        # The algorithm talked about getting the set of actions for the current
        # state and then iterating through the states that result from those
        # actions on the current state. I've simplified it slightly by adding
        # just getting the set of legal states that flow on from current state
        for ns in s.nextStates():
            # The algorithm said to check if the next state is in either
            # the explored set or the frontier, but I'm only checking the
            # explored set and adding unexplored states to the explored set
            # below, rather than check the frontier. This works in this case
            # but may not work in other cases, so it's probably wrong.
            if ns not in explored:
                newPath = Path(path + [ns])
                heapq.heappush(frontier, newPath)
                # The original agorithm doesn't do the following, but rather than
                # check the frontier I'm adding next states to the explored set
                # (probably wrong).
                explored.add(ns)

initialState = State()
goalState = State()

numDisks = int(raw_input("Enter number of disks (must be greater than 0): "))
if numDisks <= 0:
    sys.exit("Number of disks must be greater than 0")

for i in range(numDisks, 0, -1):
    initialState.addDiskToRod(i, 0)
    goalState.addDiskToRod(i, 2)

optimalPath = graphSearch(initialState, goalState)
print "The optimal path is %s steps long" % (len(optimalPath) - 1)

ans = raw_input("Do you want to see steps taken in optimal path (Y/N)? ")
if ans.lower()[0] == 'y':
    print optimalPath


# The following code attempts to explore all possible states using recursive
# function. Seems to work ok with num_disks == 4 but get stack overflow for
# higher values of num_disks - probably a bug
# 
# def explore(state, explored):
#     if state not in explored:
#         explored.add(state)
#         for s in state.nextStates():
#             explore(s, explored)
#
# fullState = set()
# explore(initialState, fullState)
# print "The size of the state space is ", len(fullState)
