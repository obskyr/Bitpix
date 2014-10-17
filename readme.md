# Sections of this readme

* [Bitpix](#Bitpix), the Python module for bitmap graphics (from old games, for example).
* [bpconfig](#bpconfig), a save-load configuration module for it.
* [Bitpictures](#Bitpictures), the front-end to convert a rom to an image. If you're not going to be doing any coding, use this!
* [Talk to me!](#Talk to me!) Contact and such.

All of these require [Python 2](https://www.python.org/downloads/), so make sure you've got it installed.

# Bitpix
Bitpix is a Python module / library for reading bit graphics. You can take bit-coded graphics in a format you choose and customize yourself, and get pixel data in a quick and easy way! Check it!

```python
import bitpix, bpconfig
coolGraphix = bitpix.Bitmap('coolgame.gbc', bpconfig.getConfig('coolconfig.cfg'))
```

It's as easy as that! Here are some of the things you can do with your new object.

```python
>>> coolGraphix.paletteIndexMatrix
# A matrix of palette indexes!
>>> coolGraphix.colorMatrix
# A matrix of color codes, according to your palette.
>>> coolGraphix.config('palette')
# Your current palette!
```

By yours truly, [@obskyr](http://twitter.com/obskyr/).

## So how do I use Bitpix?
It's quite simple, really. The class you will be working with is `Bitmap` (or `bitpix.Bitmap`), which takes two parameters to initialize. With this bitmap you can then do all sorts of things with your pixels to your heart's content.

## Initializing a `Bitmap`
A `Bitmap` takes two parameters - `infile` and `config`.

### `infile`
Simply the path to the file you want to read.
### `config`
A dictionary with all of the config parameters set. The config parameters may take some figuring out, and some of them are quite important, so they get their own section!

## Config format for `Bitmap`

Bundled with Bitpix comes a handy-dandy config saver-and-reader, so you don't have to have your configurations hard-coded or write your own config solution. It's called bpconfig, and there's documentation for that too [later in this readme](#bpconfig).

The parameters for a `Bitmap` configuration are as follows:

### `Bitmap.configDict["palette"]`

Type: **list**

A list containing the colors in your palette. The list indexes will be your palette indexes - so the color you have at index 2 will become your color for palette index 2. These will be mapped to a `Bitmap`'s `paletteIndexMatrix` in its `colorMatrix`, and do not need to be in any specific format, so feel free to use whatever color format your project needs.

Usage example:

```python
["#263125", "#4B6649", "#82A780", "#A3D0A0"]
```

### `Bitmap.configDict["pixelFormat"]`

Type: **list**

This is a list which describes the order in which bits are arranged to form the palette indexes. The bits for the palette index of one pixel aren't always right next to each other, which means that several palette indexes must be read at once.

For example, a commonly used Game Boy Color graphics format. Four colors, which means two bits per pixel (`00`-`11` in binary is 0-3 in decimal). These bits are however not stored next to each other, but with a 1-byte offset from each other. This means that (at least) 2 byte must be read at once in order to get full palette indexes without any lone bits. Here, have a visual.

```
Bits: 0011 0101 0101 1111
(8 pixels, 2 bpp [bits per pixel])

Rearranged, so 2-bits are right above 1-bits:
0011 0101
0101 1111

Converted to decimal:
0123 1313

And there's your palette indexes.
```

Now **the important part**: in order for Bitpix to read palette indexes properly, it needs to know in which order the bits are. You do this with `config['pixelFormat']`, which should be a **list of tuples**. Each tuple represents one bit. The first entry in the tuple is a string - the pixel ID, and the second is an integer - the significance of the bit.

Pixels will be read and then added to the `Bitmap`'s `paletteIndexes` *in alphabetical order*. This means that the pixel with the ID "a" will be added before the one with the ID "c". Pixel IDs can of course be longer than 1 character, but will still be in alphabetical order.

Usage example:

```python
[('a', 2), ('b', 2), ('c', 2), ('d', 2), ('e', 2), ('f', 2), ('g', 2), ('h', 2), ('a', 1), ('b', 1), ('c', 1), ('d', 1), ('e', 1), ('f', 1), ('g', 1), ('h', 1)]
```

### `Bitmap.configDict["tileLevels"]`

Type: **list**

Bitpix supports tiling to an arbitrary level. This means that you can put tiles inside tiles inside tiles inside [...]. Generally, what you will use this for is tiling pixels into tiles and then into sprites or a complete image.

Each entry in the `tileLevels` list represents a tile. Each entry is therefore a matrix (a two-dimensional list, a list of lists), with each entry in that matrix being the number of previous-size tile to put there. In the usage example at the end of this section, for example, the first tile (entry in `tileLevels`) is an 8x8 tile (and since it's the first entry, it is of pixels) where each pixel just follows the last one. The second tile is a sprite - and since it's the *second* entry in `tileLevels`, it consists of instances of the *previous tile* instead of pixels. In this tile, the 8x8 tiles are tiled in 4x4 sprites. This type of multi-level tiling can continue any number of levels.

Optionally, the very last tile level entry can be a list with a length of two, with a format like `['x', 5]` or `['y', 1]`. What these two respectively mean is "tile on the x-axis with a height of 5" (which will result in a 5 top-level tiles high and arbitrarily wide image) and "tile on the y-axis with a width of 1" (which will result in a 1 top-level tile high and arbitrarily tall column image). This format for the last tile level can be useful when the image you will be reading can have arbitrarily many of your top-level tiles in it - a ROM containing an unknown amount of sprites, for example.

Usage example:

```python
[
    [   # Tile consisting of pixels
        [ 0,  1,  2,  3,  4,  5,  6,  7],
        [ 8,  9, 10, 11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20, 21, 22, 23],
        [24, 25, 26, 27, 28, 29, 30, 31],
        [32, 33, 34, 35, 36, 37, 38, 39],
        [40, 41, 42, 43, 44, 45, 46, 47],
        [48, 49, 50, 51, 52, 53, 54, 55],
        [56, 57, 58, 59, 60, 61, 62, 63]
    ],
    [   # Sprite consisting of tiles
        [ 0,  2,  4,  6],
        [ 1,  3,  5,  7],
        [ 8, 10, 12, 14],
        [ 9, 11, 13, 15]
    ],
    ['y', 4] # Extend arbitrarily long downward with a width of 4
]
```

### And that's all!

Once you've set these options, you're good to go. The example config we've put together here would (not entirely incidentally) be a perfect fit for a common Game Boy (Color) graphics format, and would look like this:

```python
{
    'palette': ["#263125", "#4B6649", "#82A780", "#A3D0A0"],
    'pixelFormat': [('a', 2), ('b', 2), ('c', 2), ('d', 2), ('e', 2), ('f', 2), ('g', 2), ('h', 2), ('a', 1), ('b', 1), ('c', 1), ('d', 1), ('e', 1), ('f', 1), ('g', 1), ('h', 1)],
    'tileLevels': [
        [   # Tile consisting of pixels
            [ 0,  1,  2,  3,  4,  5,  6,  7],
            [ 8,  9, 10, 11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20, 21, 22, 23],
            [24, 25, 26, 27, 28, 29, 30, 31],
            [32, 33, 34, 35, 36, 37, 38, 39],
            [40, 41, 42, 43, 44, 45, 46, 47],
            [48, 49, 50, 51, 52, 53, 54, 55],
            [56, 57, 58, 59, 60, 61, 62, 63]
        ],
        [   # Sprite consisting of tiles
            [ 0,  2,  4,  6],
            [ 1,  3,  5,  7],
            [ 8, 10, 12, 14],
            [ 9, 11, 13, 15]
        ],
        ['y', 4] # Extend arbitrarily long downward with a width of 4
    ]
}
```

## Methods of a `Bitmap`
### `Bitmap.config(keyOrDict[, value])`

The only method you'll really be using for your `Bitmap`s is `config`. With it, you set the configuration of your `Bitmap` or get the current value of a property. If you've used jQuery before, this approach should be familiar.

#### Setting a property
To set properties in your config, you can do two different things:

* Pass two parameters to `Bitmap.config()` with the first being the property you want to set and the second being what you want to set it to
* Pass a dictionary as the single parameter to `Bitmap.config()`, and all of the properties in your dictionary will be updated.

After changing a `Bitmap`'s configuration, it will automatically update all of its properties (`paletteIndexMatrix`, `colorMatrix`, etc.) to match. This means that Bitpix will do those calculations as soon as you set a property with `.config()`, so set as many as possible at a time.

Usage example:

```python
>>> coolGraphix.config('pixelFormat', [('a', 1), ('a', 2)])
# And bam, you've set your pixel format and everything is updated.
>>> coolGraphix.config({
    'palette': ['#000', '#FFF'],
    'pixelFormat': ['a', 1]
})
# And boom, you've set your config to a two-color format and coolGraphix is updated.
```

#### Getting a property
It's easy! Just call `.config(propertyName)` on your `Bitmap` with a single property name as the sole parameter, and you'll get that property.

If you want to get the **entire dictionary**, use [`Bitmap.configDict`](#`Bitmap.configDict`).

Usage example:

```python
>>> coolGraphix.config('palette')
# And there you get your current palette!
```

### Others

There are of course a *lot* of other methods, but chances are you won't be needing them unless you're modding bitpix or need some *very* specific functionality. Check out the code for these, it's quite well-documented if I do say so myself!

## Properties of a `Bitmap`
The way you will be getting the info your `Bitmap` has gathered is through its non-method properties.

### `Bitmap.paletteIndexMatrix`
A matrix where each point represents a pixel. Each pixel will be represented by its palette index. For example, a four-color 8x8 image's `paletteIndexMatrix` might look like this:

```python
[
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 2, 2, 2, 2, 1, 0],
    [1, 2, 3, 2, 2, 3, 2, 1],
    [1, 2, 3, 2, 2, 3, 2, 1],
    [1, 3, 2, 2, 2, 2, 3, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [0, 1, 2, 2, 2, 2, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0]
]
```

### `Bitmap.colorMatrix`
A matrix where each point represents a color. Each pixel will be represented by the color that corresponds to its palette index in the `Bitmap`'s palette. For example, a four-color 8x8 image's `colorMatrix` might look like this:

```python
[
    ['#263125', '#263125', '#4B6649', '#4B6649', '#4B6649', '#4B6649', '#263125', '#263125'],
    ['#263125', '#4B6649', '#82A780', '#82A780', '#82A780', '#82A780', '#4B6649', '#263125'],
    ['#4B6649', '#82A780', '#A3D0A0', '#82A780', '#82A780', '#A3D0A0', '#82A780', '#4B6649'],
    ['#4B6649', '#82A780', '#A3D0A0', '#82A780', '#82A780', '#A3D0A0', '#82A780', '#4B6649'],
    ['#4B6649', '#A3D0A0', '#82A780', '#82A780', '#82A780', '#82A780', '#A3D0A0', '#4B6649'],
    ['#4B6649', '#82A780', '#A3D0A0', '#A3D0A0', '#A3D0A0', '#A3D0A0', '#82A780', '#4B6649'],
    ['#263125', '#4B6649', '#82A780', '#82A780', '#82A780', '#82A780', '#4B6649', '#263125'],
    ['#263125', '#263125', '#4B6649', '#4B6649', '#4B6649', '#4B6649', '#263125', '#263125']
]

```

### `Bitmap.size`
Simply, the height and width of the `Bitmap` in pixels. It is in the format of a list, where the first entry is the **width** and the second is the **height**.

A `Bitmap` which is 64 pixels wide and 128 pixels tall will have this size:

```python
[64, 128]
```

### `Bitmap.configDict`
The config of the `Bitmap` in `dict` form. No frills!

### Others
Other, probably less useful properties exist, too. Check the code if you're interested!

# bpconfig
bpconfig (.py) is the config utility bundled with Bitpix. With it, you can get configuration from a file and save a `Bitmap`'s configuration to a file.

## Functions
Here are the functions you will be using:

### `bpconfig.getConfig(path)`
Get the configuration saved in the file at `path`. The syntax  for this kind of file can be found [later in this readme](#Config file syntax).

Usage example:

```python
>>>coolGraphix = bitpix.Bitmap('coolgame.gbc', bpconfig.getConfig('coolconfig.cfg'))
# And you've got a Bitmap!
```

### `bpconfig.saveConfig(bitmapOrDict, path)`
Save the configuration for `bitmapOrDict` - either pass a Bitmap as the parameter and have its config saved, or a config dictionary and have it saved. The config will be saved in the format bpconfig reads, to path `path`. A sugestion for extention of this file is `.cfg`, but it *can* be anything.

This has one limitation: a palette where each color isn't a string will be saved and read as a string. For example, RGB colors in `(255, 0, 128)`-like format will be saved and read as `"(255, 0, 128)"`. There is a way to avoid this, though:

bpconfig has a variable named `colorParser`. If you set `bpConfig.colorParser` to a function (be it a lambda or not), that function will be called on every color string and the return value will be used instead. For example, you could set it to `lambda color: color.split(',')` and you'd get a list instead of a string. To complement this feature, you can also set `bpconfig.colorCompiler` to a function, and that function will be called on every color when saving, and the return value will be used. In our example, you'd set `colorCompiler = lambda color: ','.join(color)` or the non-lambda equivalent to it.

Usage example:

```python
>>>bpconfig.saveConfig(coolGraphix, 'coolconfig.cfg')
# And it's saved and ready to be read!
```

## Config file syntax

A bpconfig config file is divided into "sections" - one section for each config parameter. Each section is marked by starting with a title along the lines of `- Palette -` or `- pixel format -`. The important part is that the title is **in between two dashes** and **on its own line**. Here are the needed sections, and their respective syntaxes:

### Comments
Comments aren't *needed*, of course,, but you do have the option to use them. Comments are single-line only, and are only for describing things to readers - they won't have any effect on the config.

A comment starts with `//`, and can be anywhere in a line. Everything after `//` will be ignored.

Usage example:

```
// Look at me, I'm commenting.
// comment comment comment

// THESE ARE PRETTY COOL
```

### `- Palette -`
Each line should take the format `index: color`. The color will always be interpreted as a string, and the index should just be the palette index as a base 10 integer.

Usage example:

```
- Palette -

0: #263125
1: #4B6649
2: #82A780
3: #A3D0A0
```

### `- Pixel format -`
Just a single line, containing a string of characters and numbers where each character is a pixel's pixel ID and each number is its bit significance in base 10. What does this mean, you ask? Read [the `pixelFormat` section of the Bitpix part of this readme](`Bitmap.configDict["pixelFormat"]`). It has to do with the order in which bits are stored for each pixel.

Usage example:

```
- Pixel format -

a2b2c2d2e2f2g2h2a1b1c1d1e1f1g1h1
```

### `- Tile levels -`
Tiles are separated by empty lines, and each line in a normal tile represents a row. Each row is a space-separated (any number of spaces) list of numbers. The number at a position in this matrix will in Bitpix be replaced by the tile number of the previous tile, and each new tile will be built out of instances of the last.

The other type of tile is the arbitrary tiling (which only works as the last tile level), which is in the format along the lines of `x2` or `y7`. The letter - x or y - means in which direction to tile: on the X-axis or Y-axis, left to right or top to bottom, respectively. The number means what width / height to use. This type of tile is useful as the last level when you work with an uncertain number of tiles / sprites / what your top-level tile might be.

More info on how this works  [in the Bitpix section of this readme](#`Bitmap.configDict["tileLevels"]`).

Usage example:

```
- Tile levels -

 0  1  2  3  4  5  6  7
 8  9 10 11 12 13 14 15
16 17 18 19 20 21 22 23
24 25 26 27 28 29 30 31
32 33 34 35 36 37 38 39
40 41 42 43 44 45 46 47
48 49 50 51 52 53 54 55
56 57 58 59 60 61 62 63
// These empty lines are what separate the tile levels
// Ones with comments will count as empty, too, so watch out.

0  2  4  6
1  3  5  7
8 10 12 14
9 11 13 15

y4
```

### And that's all!

A config file for the example config we've put together could look like this:

```
- Palette -

// Hey, I can have comments anywhere.

0: #263125 // EVEN AFTER LINES, YO
1: #4B6649
2: #82A780
3: #A3D0A0

- Pixel format -

a2b2c2d2e2f2g2h2a1b1c1d1e1f1g1h1

- Tile levels -

// Tile
 0  1  2  3  4  5  6  7
 8  9 10 11 12 13 14 15
16 17 18 19 20 21 22 23
24 25 26 27 28 29 30 31
32 33 34 35 36 37 38 39
40 41 42 43 44 45 46 47
48 49 50 51 52 53 54 55
56 57 58 59 60 61 62 63

// Sprite
 0  2  4  6
 1  3  5  7
 8 10 12 14
 9 11 13 15

// Arbitrary vertical tiles!
y4

```

# Bitpictures
---

**Note:** Bitpictures requires [Pillow](https://pillow.readthedocs.org/) to be installed. This can easily be done with `pip install pillow` from the command line ([get pip](http://pip.readthedocs.org/en/latest/installing.html) first).

---

Bitpictures is an easy way to save an entire rom (or a part of it that you've cut out) to an image file. To run it, open the command line in the directory you've got Bitpictures (and Bitpix and bpconfig), and run a command with this syntax:

```
bitpictures.py mygame.gbc myimage.png myconfig.cfg
```

Bitpictures will then read `mygame.gbc` (can of course have any extension) and save the image representing it to `myimage.png`.

The third parameter, the config file, is a file containing info about your rom and the image you want. The syntax for a file like this is outlined in the section [Config file syntax](#Config file syntax). The config parameter defaults to `config.cfg`, so if that's what your config is named you can omit that parameter entirely.

Note that saving an entire rom to an image *will take a while*: don't fret if it takes more than a minute - it probably hasn't frozen.

# Talk to me!

If you've got any questions, issues or even just general talk, feel free to get in touch with me! Here's how:

* [@obskyr](http://twitter.com/obskyr/) on Twitter!
* [E-mail](mailto:powpowd@gmail.com) me
* Submit an issue on GitHub

Twitter is definitely the best way! I'm guaranteed to see it, I'll answer fast, and it's just good times all around. If there's a bug in or problem with Bitpix, an issue is the way to go, though.
