#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict # For pixel unit dictionaries without try-except.
from io import BytesIO # For iterating through bytes in a string quickly
from bitstring import BitArray # For getting the bits of bytes... as bytes.
from copy import deepcopy # For copying matrixes without modification.

class Bitmap(object):
    def __init__(self, infile, config):
        self.configDict = config

        with open(infile, 'rb') as romFile:
            self.romData = romFile.read()

        self.updatePaletteIndexes()
        self.updateDeepMatrix()
        self.updateShallowMatrix()
        self.updateColorMatrix()

    def updatePaletteIndexes(self):
        """Read the ROM data and return a list of palette indexes, in order stored according to `self.configDict['pixelFormatList']`."""
        binaryData = BitArray(hex=self.romData.encode('hex')).bin
        paletteIndexes = []
        with BytesIO(binaryData) as binaryFile:
            minimumBits = len(self.configDict['pixelFormat'])
            minBitsChunk = binaryFile.read(minimumBits)
            while minBitsChunk != '':
                paletteIndexes.extend(self.stringToPaletteIndexes(minBitsChunk)) # Get the palette indexes for that chunk
                minBitsChunk = binaryFile.read(minimumBits) # Prep for next loop-around
        self.paletteIndexes = paletteIndexes
    def stringToPaletteIndexes(self, s):
        """Take a string of 1s and 0s and output a list of palette indexes, ordered by pixel order found in self.configDict['pixelFormatList']."""
        pixelUnitsDict = defaultdict(int)
        for bit, bitInfo in zip(s, self.configDict['pixelFormat']):
            bit = int(bit, 2) # bitToValue() takes a bit in int form.
            curValuePair = self.bitToValue(bit, bitInfo)
            pixelUnitsDict[curValuePair[0]] += curValuePair[1]
        paletteIndexes = [cv[1] for cv in sorted(pixelUnitsDict.items(), key=lambda x: x[0])]
        return paletteIndexes
    def bitToValue(self, bit, bitInfo):
        """Take a bit (in int form) and a bitInfo (tuple) and return a tuple containing [pixelId, value]."""
        # bitInfo[0] is the pixel ID (a, b, c...) and bitInfo[1] is the significance (1, 2, 4, 8...).
        colorValue = bitInfo[1] * bit
        return (bitInfo[0], colorValue)

    def updateDeepMatrix(self):
        self.deepPaletteIndexMatrix = self.tileAllTheWayDown(self.paletteIndexes)[0]
        # self.tileAllTheWayDown returns a list of tiles, even if it's just 1 "tile"
        # and that tile is the complete pixel matrix. Hence the [0].
    def tileAllTheWayDown(self, units, tileLevel=0): # "Units" in the first case is probably pixels.
        """Tile `units` in several steps according to `self.configDict['tileLevels']`.
        Useful for first tiling into tiles, then tiling into sprites, etc.
        """

        tileFormat = self.configDict['tileLevels'][tileLevel]
        newUnits = []
        if len(tileFormat) and type(tileFormat[0]) == str: # For row / column tiling
            tileLength = len(units) # For arbitrary tiling no less than all the units should be used.
        else: # For to-matrix tiling
            tileLength = len(tileFormat) * len(tileFormat[0]) # Number of units.
        curStartIndex = 0
        for i in range(len(units) / tileLength):
            curStopIndex = curStartIndex + tileLength
            curTileUnits = units[curStartIndex:curStopIndex]
            newUnits.append(self.tileUnits(curTileUnits, tileFormat))
            curStartIndex = curStopIndex
        if self.configDict['tileLevels'][tileLevel + 1:]:
            newUnits = self.tileAllTheWayDown(newUnits, tileLevel + 1)
        return newUnits
    def tileUnits(self, units, tileFormat):
        """Tile the entries found in units in a matrix according to `tileFormat`."""
        # So, Samuel, why do you check for tileFormat type both here and in tileAllTheWayDown?
        # Well, it's so tileUnits COULD be used in other functions, too. Not that it will, but you know.
        if len(tileFormat) and type(tileFormat[0]) == str:
            tile = self.tileOnAxis(units, tileFormat[0], tileFormat[1])
        else:
            tile = self.tileToMatrix(units, tileFormat)
        return tile
    def tileToMatrix(self, units, tileFormat):
        """Tile the entries found in units in a matrix according to matrix `tileFormat`."""
        tileFormat = deepcopy(tileFormat)
        height = len(tileFormat)
        width  = len(tileFormat[0])
        for row in range(height):
            for col in range(width):
                # tileFormat's template values get replaced with the units at those indexes.
                tileFormat[row][col] = units[tileFormat[row][col]]
        return tileFormat
    def tileOnAxis(self, units, axis, thickness):
        """Tile the entries found in units in a matrix according to non-matrix `tileFormat`."""
        # This function ain't as elegant with the handling of axes, but whatevehrfbhere
        tile = []
        if axis == 'y':
            for unitNum, unit in enumerate(units):
                curRowNum = int(unitNum / thickness)
                if len(tile) < curRowNum + 1:
                    tile.append([])
                tile[curRowNum].append(unit)
        elif axis == 'x':
            for startIndex in range(thickness):
                tile.append(units[startIndex::thickness]) # Ah, the list step! Oft-forgotten!
        return tile

    def updateShallowMatrix(self):
        self.paletteIndexMatrix, self.size = self.deepToShallowMatrix(self.deepPaletteIndexMatrix)
    def deepToShallowMatrix(self, units, pixelMatrix=None, unitsCoords=None):
        """Take a matrix of tiles (which may be matrixes or may be non-lists/tuples) and return a matrix of the most basic units and the size of that matrix.

        Return format:
        ([['row0col0', 'row0col1'], ['row1col0', 'row1col1']], [width, height])
        """
        pixelMatrix = [] if pixelMatrix == None else pixelMatrix
        unitsCoords = [0, 0] if unitsCoords == None else unitsCoords # The top-left coordinates of these units in the pixel matrix.
        localCoords = [0, 0] # Will be used to track where in the unit the function is
        localSize = [0, 0] # Will be used to track the max value of localCoords
        pixelMatrixCoords = [0, 0] # Will later be used to store unitsCoords + localCoords.
        for row in units:
            localCoords[0] = 0 # Return to the beginning of the row each time
            pixelMatrixCoords[1] = localCoords[1] + unitsCoords[1]
            if len(pixelMatrix) == pixelMatrixCoords[1]: # Initializing a row
                pixelMatrix.append([])

            for unit in row:
                pixelMatrixCoords[0] = localCoords[0] + unitsCoords[0]
                if type(unit) in [list, tuple]:
                    nextunitsCoords = [pixelMatrixCoords[0], pixelMatrixCoords[1]]
                    pixelMatrix, unitSize = self.deepToShallowMatrix(unit, pixelMatrix, nextunitsCoords)
                    # The beauty of this approach is that each "unit" can be one pixel, one tile, or even more than that.
                    # The function treats them all the same way, and gets their dimensions and pixels recursively.
                else:
                    if len(pixelMatrix[pixelMatrixCoords[1]]) == pixelMatrixCoords[0]: # Initializing a unit index in a row
                        pixelMatrix[pixelMatrixCoords[1]].append(None)
                    pixelMatrix[pixelMatrixCoords[1]][pixelMatrixCoords[0]] = unit # ...For later placing the unit at that index.
                    unitSize = [1, 1]

                localCoords[0] += unitSize[0] # Add a unit (x-coord) each unit
                localSize[0] = max([localCoords[0], localSize[0]])
            localCoords[1] += unitSize[1] # Only add a row (y-coord) each row
            localSize[1] = max([localCoords[1], localSize[1]])

        return pixelMatrix, localSize
    def updateColorMatrix(self):
        colorMatrix = []
        for row in self.paletteIndexMatrix:
            colorMatrix.append([self.configDict['palette'][i] for i in row])
        self.colorMatrix = colorMatrix

    def updateChanges(self, oldConfig):
        updateHierarchy = [ # When a function earlier in this list needs updating, those after do too.
            'updatePaletteIndexes',
            'updateDeepMatrix',
            'updateShallowMatrix',
            'updateColorMatrix'
        ]
        consequences = { # {changedValue: consequentFunction}
            'pixelFormat': 'updatePaletteIndexes',
            'tileLevels': 'updateDeepMatrix',
            'palette': 'updateColorMatrix'
        }
        updateIndex = len(updateHierarchy)
        for key in consequences:
            if self.configDict[key] != oldConfig[key]:
                curUpdateIndex = updateHierarchy.index(consequences[key])
                updateIndex = curUpdateIndex if curUpdateIndex < updateIndex else updateIndex

        for functionName in updateHierarchy[updateIndex:]:
            getattr(self, functionName)()


    # Methods and variables that are actually meant to be used / gotten!
    def config(self, keyOrDict, value=None):
        """Set the config property `keyOrDict` to `value`, or update config with dict `keyOrDict` - OR get current value for `keyOrDict`."""
        # jQuery-style!
        # Note: Bitmap.config is the FUNCTION - Bitmap.configDict is the actual configuration.
        oldConfig = deepcopy(self.configDict)
        if type(keyOrDict) == dict: # Setting values with a dictionary
            self.configDict.update(keyOrDict)
        elif value != None: # Setting one value with a key and a value
            self.configDict[keyOrDict] = value
        else: # Getting value in config
            return self.configDict[keyOrDict] # Never updates changes, 'cause it returns :^)
        self.updateChanges(oldConfig)

    configDict = {}
    paletteIndexMatrix = []
    size = ()
    colorMatrix = []

if __name__ == '__main__':
    import bpconfig
    import bpdebug
    panda = Bitmap('pandablush-incomplete.gbc', bpconfig.getConfig('config.cfg'))
    print panda.colorMatrix
