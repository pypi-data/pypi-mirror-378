# PyPNM - PPM and PGM image files reading, viewing and writing in pure Python

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pypnm) ![PyPI - Version](https://img.shields.io/pypi/v/pypnm)

## Overview and Justification

PyPNM is a Python module for reading PPM and PGM image files (both 8 and 16 bits per channel color depth) to image 3D integer lists for further editing, displaying 3D lists obtained by converting to Tkinter-compatible data in memory, and subsequent writing edited image 3D lists to disk as PPM or PGM files, either binary or ASCII.

PPM ([Portable Pixel Map](https://netpbm.sourceforge.net/doc/ppm.html)) and PGM ([Portable Gray Map](https://netpbm.sourceforge.net/doc/pgm.html)) (particular cases of PNM format group) are simplest file formats for RGB and L images, correspondingly. Not surprisingly for this decaying Universe, such a simplicity lead to some adverse consequences:

- lack of strict official specification. Instead, you may find words like "usual" in format description. Surely, there is always someone who implement this part of image format in unprohibited, yet a totally unusual way.

- unwillingness of many professional software developers to spend their precious time on such a trivial task as supporting simple open format. It took years for almighty Adobe team to include PNM module in Photoshop rather than count on third-party developers, and surely (see above) they took their chance to implement a header scheme nobody else seem to use. What as to PNM support in Python, say, Pillow, it's often incomplete and/or requires counterintuitive measures when dealing with specific image types (like 16-bit per channel) in rare cases such a support exist.

As a result, novice Python user (like the writer of these words) may find it difficult to get simple yet reliable input/output modules for PPM and PGM image formats.

## Objectives

1. To obtain suitable facility for **visualization** of image-like data (images first and foremost), represented as 3D nested lists, via Tkinter `PhotoImage(data=...)` method. That is, something to easily view images without downloading excessively large packages.

2. To obtain simple and compact cross-platform module for **reading** PPM and PGM files as 3D nested lists for further processing with Python, and subsequent **writing** of processed 3D nested lists data to PPM or PGM files.

3. To inspire and facilitate further development of image **editing** algorithms in Python (meaning Python, not something else) by attaining objectives No. 1 and 2. That is, once you can read and write images, and view the result of analyzing/filtering image with your algorithm, you, as a developer, may finally concentrate on image processing algorithm itself, rather than any auxiliary facilities.

To accomplish this, current PyPNM module was developed, combining read/write functions for binary and ASCII PGM and PPM files (*i.e.* P2, P5, P3 and P6 PNM file types), and suitable facilities for image display. Both greyscale and RGB color spaces with 8-bit and 16-bit per channel color depths (0..255 and 0..65535 ranges respectively) are supported directly, without limitations and without any dances with tambourine like using separate methods for different bit depths *etc*.

Thus, PyPNM may simplify writing image processing applications in Python, either as a part of rapid prototyping or as finalized software.

| Fig. 1. *Example of pure Python image filtering application utilizing PyPNM* |
| :---: |
| [![Pure Python image adaptive averaging application, largely based on PyPNM](https://dnyarri.github.io/thread/ave.png "Pure Python image filtering application, largely based on PyPNM")](https://dnyarri.github.io/povthread.html#averager) |
| *Adaptive image averaging application. PNM image file open/save, as well as image filtering before/after display are based on PyPNM. Nested list structure, produced by PyPNM, allows easy processing of arbitrary number of channels with the same algorithm; for example, in this filter* `map`*s are actively used to create compact omnivorous algorithm.* |

Noteworthy that PyPNM is pure Python module, which makes it pretty compact and OS-independent. No third-party imports, no Numpy version conflicts (some may find it surprising, but list reshaping in Python can be done with one line without Numpy) *etc*.

## Python compatibility

Current PyPNM version, created for PyPI distribution, is a maximal backward compatibility build. While most of the development was performed using Python 3.12, extensive testing with other versions was carried out, and PyPNM proven to work with antique **Python 3.4** ([reached end of life 18 Mar 2019](https://devguide.python.org/versions/)) under **Windows XP 32-bit** ([reached end of support 8 Apr 2014](https://learn.microsoft.com/en-us/lifecycle/products/windows-xp)).

> [!NOTE]
> Tkinter, bundled with standard CPython distributions 3.10 and below have problems with 16 bpc images. Although it's not PyPNM but Tkinter problem, it's still ungood and severely discombobulating. As a workaround, `list2bin` function in PyPNM extended compatibility version (.34) includes a routine for color depth reduction from 16 bpc to 8 bpc when generating a preview. Surely `list2bin` tries to avoid such a remapping unless it is absolutely necessary since remapping requires extra calculation and therefore slows the function down; decision on remapping, however, is based on correlation between CPython version and bundled Tkinter version, and therefore may fail if you have custom builds of Tkinter, or Python, or both. Failure is most likely to manifest as unnecessary slowdowns, and least likely as Tkinter exception. Remember that this module is provided under Unlicense, I don't care much of my copyright, so you may edit the source at will, including Python version detection criteria.
>
> If you have only new versions of Python (3.11 and above) and Tkinter, you may consider downloading [Main version of PyPNM](https://github.com/Dnyarri/PyPNM), which doesn't have any backward compatibility fixes, and therefore doesn't waste CPU time on it.

## Format compatibility

Current PyPNM module read and write capabilities are briefly summarized below.

| Image format | File format | Read | Write |
| ------ | ------ | ------ | ------ |
| 16 bits per channel RGB | P6 Binary PPM | Yes | Yes |
| 16 bits per channel RGB | P3 ASCII PPM | Yes | Yes |
| 8 bits per channel RGB | P6 Binary PPM | Yes | Yes |
| 8 bits per channel RGB | P3 ASCII PPM | Yes | Yes |
| 16 bits per channel L | P5 Binary PGM | Yes | Yes |
| 16 bits per channel L | P2 ASCII PGM | Yes | Yes |
| 8 bits per channel L | P5 Binary PGM | Yes | Yes |
| 8 bits per channel L | P2 ASCII PGM | Yes | Yes |
| 1 bit ink on/off | P4 Binary PBM | Yes | No |
| 1 bit ink on/off | P1 ASCII PBM | Yes | No |

## Target image representation

**Main goal** of module under discussion **is** not just bytes reading and writing but representing image as some logically organized structure for further **image editing**.

Is seems logical to represent an RGB image as nested 3D structure - (X, Y)-sized matrix of three-component (R, G, B) vectors. Since in Python list seem to be about the only variant for mutable structures like that, it is suitable to represent image as `list(list(list(int)))` structure. Therefore, it would be convenient to have module read/write image data from/to such a structure.

Note that for L images memory structure is still `list(list(list(int)))`, with innermost list having only one component, which enables further image editing with the same nested (x, y, z) loop regardless of color mode.

Note that for the same reason when reading 1-bit PBM files into image this module promotes data to 8-bit L, inverting values and multiplying by 255, so that source 1 (ink on) is changed to 0 (black), and source 0 (ink off) is changed to 255 (white) - since any palette-based images, 1-bit included, are next to useless for general image processing (try to imagine 1-bit Gaussian blur, for example), and have to be converted to smooth color for that, conversion is performed by PyPNM automatically.

## Installation

In case of installing from PyPI via pip:

`python -m pip install --upgrade PyPNM`

then in your program import section:

`from pypnm import pnmlpnm`

then use functions as described in section *"Functions description"* below.

In case you downloaded file **pnmlpnm.py** from Github or somewhere else as plain .py file and not a module, simply put this file into your program folder, then use `import pnmlpnm`.

## Usage

Below is a minimal Python program, illustrating all PyPNM functions at once: reading PPM file (image files are not included into PyPI PyPNM distribution. You may use any of [compatibility testing samples](https://github.com/Dnyarri/PyPNM/tree/main/compatibility) from Git repository) to image nested list, writing image list to disk as binary PPM, writing image list as ASCII PPM, and displaying image list using Tkinter:

```python

#!/usr/bin/env python3

from tkinter import Button, PhotoImage, Tk

from pypnm import pnmlpnm

X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list('example.ppm')  # Open
pnmlpnm.list2pnmbin('binary.ppm', image3D, maxcolors)  # Save as binary
pnmlpnm.list2pnmascii('ascii.ppm', image3D, maxcolors)  # Save as ascii

main_window = Tk()
main_window.title('PyPNM demo')
preview_data = pnmlpnm.list2bin(image3D, maxcolors)  # Generating preview bytes from list
preview = PhotoImage(data=preview_data)  # Generating preview object from bytes
preview_button = Button(main_window, text='Example\n(click to exit)', 
                image=preview, compound='top', command=lambda: main_window.destroy())
preview_button.pack()
main_window.mainloop()

```

With a fistful of code for widgets and events this simplistic program may be easily turned into to a rather functional application.

| Fig. 2. *Example of ASCII PPM displayed in Tkinter-based GUI* |
| :---: |
| [![Example of ASCII PPM opened in Viewer.py and converted to binary ppm on the fly to be rendered with Tkinter](https://dnyarri.github.io/pypnm/viewer.png "Example of ASCII PPM opened in Viewer.py")](https://dnyarri.github.io/pypnm.html) |
| *Example of Tkinter-based viewer displaying ASCII PPM. Note that ASCII PNM files per se are not supported by Tkinter; in this example ASCII PPM is opened as 3D list using PyPNM, then, using PyPNM again, converted on the fly to PNM-like binary data in memory, which Tkinter can handle successfully.* |

## Functions description

Main module file **pnmlpnm.py** contains 100% pure Python implementation of everything one may need to read and write a variety of PGM and PPM files, as well as to display corresponding image data. No non-standard dependencies, no extra downloads, no dependency version conflicts expected. I/O functions are written as functions/procedures, as simple as possible, and listed below:

- **pnm2list**  - reading binary or ASCII RGB PPM or L PGM file and returning image data as nested list of int.
- **list2bin**  - getting image data as nested list of int and creating binary PPM (P6) or PGM (P5) data structure in memory. Suitable for generating data to display with Tkinter.
- **list2pnmbin** - getting image data as nested list of int and writing binary PPM (P6) or PGM (P5) file.
- **list2pnmascii** - alternative function to write ASCII PPM (P3) or PGM (P2) files.
- **list2pnm** - getting image data as nested list of int and writing either binary or ASCII file depending on `bin` argument.
- **create_image** - creating empty nested 3D list for image representation. Not used within this particular module but often needed by programs this module is supposed to be used with.

Detailed functions arguments description is provided below as well as in module docstrings and [PyPNM documentation for offline reading (PDF)](https://dnyarri.github.io/pypnm/pypnm.pdf).

### pnm2list

`X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(in_filename)`

Read data from PPM/PGM file to nested image data list, where:

- `X, Y, Z`   - image sizes (int);
- `maxcolors` - number of colors per channel for current image (int);
- `image3D`   - image pixel data as list(list(list(int)));
- `in_filename` - PPM/PGM file name (str).

### list2bin

`image_bytes = pnmlpnm.list2bin(image3D, maxcolors, show_chessboard)`

Convert nested image data list to PGM P5 or PPM P6 (binary) data structure in memory, where:

- `image3D`   - `Y * X * Z` list (image) of lists (rows) of lists (pixels) of ints (channels);
- `maxcolors` - number of colors per channel for current image (int);
- `show_chessboard` - optional bool, set `True` to show LA and RGBA images against chessboard pattern; `False` or missing show existing L or RGB data for transparent areas as opaque. Default is `False` for backward compatibility;
- `image_bytes` - PNM-structured binary data.

`image_bytes` object thus obtained is well compatible with Tkinter `PhotoImage(data=...)` method and therefore may be used to (and actually was developed for) visualize any data represented as image-like 3D list.
When encountering image list with 2 or 4 channels, current version of `list2bin` may treat it as LA or RGBA image correspondingly, and generate image preview for Tkinter as transparent over chessboard background (like Photoshop or GIMP). Since PNM images do not have transparency, this preview is actually either L or RGB, with image mixed with chessboard background, generated by `list2bin` on the fly (pattern settings match Photoshop "Light Medium" defaults). This behaviour is controlled by `show_chessboard` option. Default setting is `False` (meaning simply skipping alpha channel) for backward compatibility.

### list2pnmbin

`pnmlpnm.list2pnmbin(out_filename, image3D, maxcolors)`

Write PGM P5 or PPM P6 (binary) file from nested image data list, where:

- `image3D`   - `Y * X * Z` list (image) of lists (rows) of lists (pixels) of ints (channels);
- `maxcolors` - number of colors per channel for current image (int);
- `out_filename` - Name of PNM file to be written.

Note that unlike `lis2bit`, making big gulp to process whole image, `list2pnm` is developed for per row image writing to reduce memory requirements for large files.

### list2pnmascii

`pnmlpnm.list2pnmascii(out_filename, image3D, maxcolors)` where:

Write PGM P2 or PPM P3 (ASCII text) file from nested image data list, where:

- `image3D`   - `Y * X * Z` list (image) of lists (rows) of lists (pixels) of ints (channels);
- `maxcolors` - number of colors per channel for current image (int);
- `out_filename` - PNM file name.

Similar to `list2pnm` above but creates ASCII pnm file instead of binary one. Note that `list2pnmascii` performs per sample image writing, providing minimal memory footprint for a price of potential extra file fragmentation (which may, or may not appear in reality, depending on system and hardware caching).

### list2pnm

`pnmlpnm.list2pnm(out_filename, image3D, maxcolors, bin)`

Write either binary or ASCII file from nested image data list, where:

- `image3D`   - `Y * X * Z` list (image) of lists (rows) of lists (pixels) of ints (channels);
- `maxcolors` - number of colors per channel for current image (int);
- `bin` - switch defining whether to write binary file or ASCII (bool). Default is True, meaning binary output, to provide backward compatibility.
- `out_filename` - Name of PNM file to be written.

Note that `list2pnm` is merely a switch between `list2pnmbin` and `list2pnmascii`, introduced for simplifying writing "Save as..." dialog functions - now you can use one function for all PNM flavours, passing `bin` via lambda, if necessary. Default is `bin = True` since binary PNM seem to be more convenient for big programs like Photoshop or GIMP.

### create_image

`image3D = create_image(X, Y, Z)`

Create empty 3D nested list of `X * Y * Z` sizes. Not used within this particular module internally, but often needed by programs this module is supposed to be used with.

## References

1. [Netpbm file formats specifications](https://netpbm.sourceforge.net/doc/) followed in the course of PyPNM development.

2. [PyPNM at Github](https://github.com/Dnyarri/PyPNM) contains both PyPNM module and viewer application example, illustrating using `list2bin` to produce data for Tkinter `PhotoImage(data=...)` to display, and other PyPNM functions for opening/saving various portable map formats (so viewer may be used as converter between binary and ASCII variants of PPM and PGM files). Issues and discussions are open for possible bug reports.

3. [PyPNM for Python 3.4 at Github](https://github.com/Dnyarri/PyPNM/tree/py34/) - same as above, but compatible with Python down to 3.4. Besides PPM and PGM support, image viewer in this branch also have PNG support, based on [PyPNG](https://gitlab.com/drj11/pypng), and may be used as pure Python PNM <=> PNG converter.

4. [PyPNM docs (PDF)](https://dnyarri.github.io/pypnm/pypnm.pdf). While current documentation was written for 9 May 2025 "Victory" version, it remains valid for 2 Sep 2025 "Victory II" release since the latter involves total inner optimization without changing input and output data types and structure.

5. [PyPNM home page](https://dnyarri.github.io/pypnm.html).
