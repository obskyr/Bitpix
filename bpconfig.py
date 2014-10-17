# -*- coding: utf-8 -*-
import re # For parsing EVERYthing.

# These first functions are ones getConfig uses.



def stripSection(section):
    """Strip a config file section from all comments and surrounding whitespace."""
    commentRe = re.compile(r"^(.*?)[ \t]*?//.*$", re.MULTILINE)
    section = re.sub(commentRe, r'\1', section)
    section = section.strip()
    return section
colorParser = lambda x: x
def parsePalette(section):
    palette = []
    lines = section.split('\n')
    paletteRe = re.compile(r"^\s*(?P<index>[0-9]+)\s*:\s*(?P<color>.*?)\s*$")
    for line in lines:
        curMatch = re.match(paletteRe, line)
        curIndex = int(curMatch.group('index'))
        curColor = colorParser(curMatch.group('color'))
        while len(palette) < curIndex + 1:
            palette.append(None)
        palette[curIndex] = curColor
    return palette
def parsePixelFormat(formatString):
    """Parse a pixel format string and return a bitpix-friendly pixel format tuple of tuples.

    Return format:
    (
        (pixelID0, bitSignificance0),
        (pixelID1, bitSignificance0),
        (etc, etc)
    )"""
    pixelIDs = re.findall('[A-Za-z]+', formatString)
    bitSignificances = [int(bS) for bS in re.findall('[0-9]+', formatString)]
    return zip(pixelIDs, bitSignificances)

def parseTileLevels(section):
    tileLevels = [[]]
    whitespaceRe = re.compile(r'\s+')
    lettersRe = re.compile(r'[A-Za-z]+')
    numbersRe = re.compile(r'[0-9]+')
    lines = section.split('\n')
    curTile = 0
    runningWhitespace = True
    for line in lines:
        line = line.strip()
        if line:
            if re.search(lettersRe, line): # It's an arbitrary-length tile line.
                axis = re.search(lettersRe, line).group(0).lower()
                thickness = int(re.search(numbersRe, line).group(0))
                tileLevels[curTile] = [axis, thickness]
            else: # It's a matrix line.
                runningWhitespace = False
                tileLevels[curTile].append([int(i) for i in re.split(whitespaceRe, line)])
        elif not runningWhitespace:
            runningWhitespace = True
            curTile += 1
            tileLevels.append([])
    return tileLevels

sectionParsers = {
    'palette': parsePalette,
    'pixel format': parsePixelFormat,
    'tile levels': parseTileLevels
}
sectionKeys = {
    'palette': 'palette',
    'pixel format': 'pixelFormat',
    'tile levels': 'tileLevels'
}

def getConfig(infile):
    # Get config from a YAML or JSON or god-knows-what file instead later.
    config = {}

    with open(infile, 'r') as f:
        configData = f.read()

    sectionNameRe = re.compile(r"^[ \t]*-[ \t]*(.*?)[ \t]*-[ \t]*(?://.*)?$", re.MULTILINE)
    sectionSplitRe = re.compile(r"^[ \t]*-.*?-[ \t]*(?://.*)?$", re.MULTILINE)
    sectionNames = [name.lower() for name in re.findall(sectionNameRe, configData)]
    sections = re.split(sectionSplitRe, configData)[1:] # [1:] because the first match is before everything.
    for sectionName, section in zip(sectionNames, sections):
        section = stripSection(section)
        curKey   = sectionKeys[sectionName]
        curValue = sectionParsers[sectionName](section)
        config[curKey] = curValue

    return config

# And now, for the saving.

# These two are pretty much only for tileLevelsToString().
def joinMatrix(matrix, rowJoiner=' ', colJoiner='\n'):
    """Join a matrix into a string with `rowJoiner` and `colJoiner`."""
    matrixString = [rowJoiner.join(row) for row in matrix]
    matrixString = colJoiner.join(matrixString)
    return matrixString
def matrixToString(matrix, rowJoiner=' ', colJoiner='\n'):
    """Convert a matrix to a string, with spaces to align the entries with each other horizontally."""
    maxLength = 0
    for row in matrix:
        for entry in row:
            curLength = len(str(entry))
            maxLength = curLength if curLength > maxLength else maxLength
    stringMatrix = []
    for y, row in enumerate(matrix):
        stringMatrix.append([])
        for x, entry in enumerate(row):
            curString = str(entry)
            curString = ' ' * (maxLength - len(curString)) + curString
            stringMatrix[y].append(curString)
    return joinMatrix(stringMatrix, rowJoiner, colJoiner)

colorCompiler = lambda x: str(x)
def paletteToString(palette):
    paletteString = ""
    for index, color in enumerate(palette):
        paletteString += str(index) + ': ' + colorCompiler(color)
        paletteString += '\n'
    paletteString = paletteString[:-1] # Cut off the last newline.
    return paletteString
def pixelFormatToString(pixelFormat):
    pixelFormatString = ""
    for pair in pixelFormat:
        pixelFormatString += pair[0]
        pixelFormatString += str(pair[1])
    return pixelFormatString
def tileLevelsToString(tileLevels):
    tileLevelsString = ""
    for tile in tileLevels:
        if type(tile[0]) != str: # Normal tile
            tileLevelsString += matrixToString(tile)
        else: # Arbitrary tile
            tileLevelsString += tile[0]
            tileLevelsString += str(tile[1])
        tileLevelsString += '\n\n'
    tileLevelsString = tileLevelsString[:-2] # Cut off last newlines, once again.
    return tileLevelsString

sectionCompilers = {
    'palette': paletteToString,
    'pixelFormat': pixelFormatToString,
    'tileLevels': tileLevelsToString
}
sectionTitles = {
    'palette': 'Palette',
    'pixelFormat': 'Pixel format',
    'tileLevels': 'Tile levels'
}
configOrder = [
    'palette',
    'pixelFormat',
    'tileLevels'
]

def configToString(config):
    """Convert `config` to a string readable by getConfig()."""
    configString = ""
    for key in configOrder:
        value = config[key]

        curTitle        = sectionTitles[key]
        curCompiler     = sectionCompilers[key]
        curConfigString = curCompiler(value)

        configString += '- ' + curTitle + ' -'
        configString += '\n\n'
        configString += curConfigString
        configString += '\n\n'
    configString = configString[:-1] # Removing last newline, once again.
    return configString

def saveConfig(config, path):
    if not type(config) == dict:
        config = config.configDict
    configStr = configToString(config)
    with open(path, 'w') as outfile:
        outfile.write(configStr)
