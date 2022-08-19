to-gallery.py -- generate a basic HTML thumbnail gallery for a folder of images.
By B.M.Deeal.

This version is distributed under the ISC license, see the LICENSE section of this file for details.

---
ABOUT:
to-gallery.py allows you to create a simple HTML gallery with thumbnails and navigation between pictures. 

For example, running:

	to-gallery.py -mode color -regenerate pictures-ce
	
will create a pictures-ce.html page in the current directory, while placing the thumbnails and per-image pages in ./pictures-ce/g-thumbs/ and ./pictures-ce/g-pages/ respectively. 

This utility was primarily created to view a collection of images on some old Windows CE devices I had, as the machines do not have a dedicated image browser program available. However, the systems do have a reasonably full-featured (for the time) web browser.

All of the defaults, along with the design of the web pages, are based around this fact. Future versions of to-gallery.py are expected to add support for generating more modern HTML5+CSS galleries (likely with a -modern switch).

This utility is an updated version of a quick-and-dirty Bash script I wrote, and is significantly enhanced from it, with features like per-image pages so you can navigate from image to image without having to return to the gallery thumbnail page, which is quite slow on the CE devices) and configurable options for thumbnail generation.

---
PARAMETERS:
There are several parameters:

* -xsize/-sX (width), -ysize/-sY (height)
Set the size of the thumbnails in pixels.


* -mode/-m color/gray/hq
Set the thumbnail output mode.
	color: color dithered .gif format thumbnail
	gray: .grayscale dithered gif format grayscale thumbnail (default)
	hq: color .jpg format thumbnail (currently unimplemented, use '-mode color' for now)

* -regenerate/-r
Re-create all of the thumbnails instead of skipping pictures that already have them.

* -help/-h/-?
Display a brief help on how to use the program.

* -nothumbnails/-nT
Disable thumbnail generation, modifies pages to not use them.

* -norotate/-nR
Disable rotated image generation, and disables the rotate link on pages.

* -nolucky/-nL
Disables the 'lucky' image link button, which would link to a randomly selected (at gallery creation time) image.

All arguments will accept one or two dashes before them (eg, --regenerate is a valid command).
Arguments are case-sensitive.
Currently, there is no command to stop argument processing, so it will not work on folders starting with a dash..

---
INSTALLATION:
to-gallery.py simply can be plopped anywhere in your PATH (commonly, /usr/local/bin/) and made executable.

to-gallery.py requires ImageMagick (tested with 6.9.10-23) to be available in the PATH and Python 3.8.5 or later. to-gallery.py uses the 'convert' command.
This script was tested under Ubuntu 20.04.2 LTS under WSL1.

to-gallery.py has currently not been tested under a Windows version of Python (or any non-Linux system), but may still work.


---
LICENSE:

(C) 2021, 2022 B.M.Deeal.

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
