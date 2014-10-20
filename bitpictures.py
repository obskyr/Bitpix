# -*- coding: utf-8 -*-

import bitpix
import bpconfig
from PIL import Image

def bitmapToImage(bitmap, alpha=True):
    if alpha:
        mode = 'RGBA'
        alphaChannel = Image.new('L', bitmap.size, 0)
    else:
        mode = 'RGB'
    image = Image.new(mode, bitmap.size, (0, 0, 0))
    for y, row in enumerate(bitmap.colorMatrix):
        for x, color in enumerate(row):
            if alpha:
                try:
                    alphaChannel.putpixel((x, y), color[3])
                except IndexError:
                    alphaChannel.putpixel((x, y), 255) # Defaults to fully opaque pixel.
            image.putpixel((x, y), color[:3])
    if alpha:
        image.putalpha(alphaChannel)
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

    # Some formats have commonly used alternate extensions.
    altExtensions = {
        'jpg': 'jpeg',
        'tif': 'tiff',
        'dib': 'bmp'
    }
    # Not the formats that actually support an alpha channel, but...
    # the formats that PIL won't raise an error saving an RGBA image as.
    alphaFormats = ['png', 'jpeg', 'gif', 'ppm', 'tiff', 'webp']
    defaultFormat = 'bmp'

    extensionRe = re.compile(r"^.*\.([a-zA-Z0-9]+)$")
    outFormat = re.search(extensionRe, outPath)
    outFormat = outFormat.group(1) if outFormat != None else outFormat
    outFormat = outFormat.lower()
    outFormat = altExtensions[outFormat] if outFormat in altExtensions else outFormat

    alpha = outFormat in alphaFormats

    def parseColorString(colorString):
        if colorString[0] == '#':
            c = colorString[1:]
            color = c[0:2], c[2:4], c[4:6], c[6:8]
            color = tuple(int(c, 16) if c else 255 for c in color) # Defaults to 255 for leaving alpha out
        else:
            color = tuple(int(v) for v in re.split(r"\s*,\s*", colorString))
        return color

    bpconfig.colorParser = parseColorString # To get the tuple format.
    config = bpconfig.getConfig(configPath)
    bitmap = bitpix.Bitmap(inPath, config)
    image = bitmapToImage(bitmap, alpha)
    try:
        image.save(outPath, outFormat)
    except KeyError:
        image.save(outPath, defaultFormat)
