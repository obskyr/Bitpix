# -*- coding: utf-8 -*-

import bitpix
import bpconfig
from PIL import Image

def bitmapToImage(bitmap):
    alpha = Image.new('1', bitmap.size, 0)
    image = Image.new('RGBA', bitmap.size, (0, 0, 0))
    for y, row in enumerate(bitmap.colorMatrix):
        for x, color in enumerate(row):
            alpha.putpixel((x, y), color[3])
            image.putpixel((x, y), color[:3])
    image.putalpha(alpha)
    return image

if __name__ == '__main__':
    import sys
    import re
    try:
        inPath = sys.argv[1]
    except IndexError:
        print "No input file specified!"
    try:
        outPath = sys.argv[2]
    except IndexError:
        print "No output file specified!"
    try:
        configPath = sys.argv[3]
    except IndexError:
        configPath = 'config.cfg'

    extensionRe = re.compile(r"^.*\.([a-zA-Z0-9]+)$")
    outFormat = re.search(extensionRe, outPath)
    outFormat = outFormat.group(1) if outFormat != None else outFormat

    def parseColorString(colorString):
        return tuple(int(v) for v in re.split(r"\s*,\s*", colorString))

    bpconfig.colorParser = parseColorString # To get the tuple format.
    config = bpconfig.getConfig(configPath)
    bitmap = bitpix.Bitmap(inPath, config)
    image = bitmapToImage(bitmap)

    try:
        image.save(outPath, outFormat)
    except KeyError:
        image.save(outPath)
