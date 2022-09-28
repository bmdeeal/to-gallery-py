#!/usr/bin/env python3

"""
to-gallery.py -- generate a basic html thumbnail gallery for a folder of images
#usage: to-gallery.py [-mode color|gray|hq] [-xsize size] [-ysize size] [-squaresize size] [-regenerate] [-regenerate-thumbs] [-regenerate-rotated] [-nothumbnails] [-norotate] [-nolucky] galleryname

---

(C) 2021, 2022 B.M.Deeal
#Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

---

Requires imagemagick to be available in $PATH. Tested on Ubuntu 20.04 on WSL with Python 3.8.5.

This is a Python re-implementation of a shell script I'd written to do this exact task. Python is dramatically nicer to use for something like this, even if it took quite a bit longer to write (even if that just means it took most of an evening into the morning, rather than just the evening and then I went to bed at a reasonable hour, lol).

This program will blindly accept any image formats as valid gallery targets to display, but the target device this I wrote this utility to generate galleries for doesn't support .png since it's an old CE2.0 palmtop. This script could handle that conversion if needed, which may be added at some point.
The defaults are the way they are due to this being made for use with a CE2 palmtop -- grayscale .gif thumbnails on extremely plain Web 1.0 style pages. The device supports .jpg, but decoding JPEG files on a late 90s handheld device is VERY slow.
Same thing with the standard color mode setting: I have another, quite a bit faster CE2.11 device with color that is more okay with JPEG, but it's still way faster working with .gif files vs .jpg on it, and high-quality (like 85 quality) files are still somewhat slow to decode.

This is not a production grade piece of software. This is a somewhat quick-and-dirty utility that lets me use particularly obsolete handheld devices as a convenient photo gallery, even if this script is likely useful for other purposes.
This bears repeating: this NOT ROBUST SOFTWARE, do not use it in a situation where robustness is needed (eg, on a website where users can upload files and this script gets called).
That license bit about how the "software is provided AS-IS" isn't kidding.

For example, this script isn't designed to handle arbitrary folder locations currently, it expects you to be in the parent directory of the folder with all the pictures.
Don't call it like 'to-gallery.py folder/otherfolder'. It might even work, but it is entirely untested and I know the old BASH script that I wrote (and referenced heavily for this, possibly unintentionally leading to the same behavior) broke badly when you did that.

TODO list:
* imagemap mode for thumbnail grid view, which would also save a LOT of overhead on a CE device with a large memory card -- would still need to generate the thumbnail files, but they could be deleted after? Something like that.
* modern mode that uses a nice HTML5 layout so you can have nice CSS theming, and it'd even include a default stylesheet if one doesn't already exist
* there are certainly a few spots with insufficient error handling
* test under Windows proper and not just under WSL -- this tries to do the Right Thing and use proper path constructing functions but I might just end up removing all of that because it seems like a bunch of fragile magic that overcomplicates things since Windows cheerfully accepts '/' anyway as the separator; this isn't a high priority since WSL exists, but it probably shouldn't be mandatory

"""

import sys
import os
import subprocess
import datetime
import random

#important globals
version_major="1" #will probably bump this to 2.0 once I add CSS theming.
version_minor="9"
version_suffix="release" #could be alpha, beta, or release
version_string=f"{version_major}.{version_minor}-{version_suffix}"
default_size=80
x_size=default_size
y_size=default_size
gallery_name=""
gallery_name_clean="" #no trailing slash or whatever
gallery_name_clean_list=""
thumb_dir="g-thumbs"
page_dir="g-pages"
rotate_dir="r-pics"
thumb_active=True #generate thumbnails?
rotate_active=True #generate rotated images?
lucky_active=True #enable the lucky image link?
regenerate=False #whether to re-create the thumbnails (pages are always re-created, since the order may have changed)
regenerate_thumbs=False
regenerate_rotate=False
mode="gray" #could be gray, color, or hq - gray and color are .gif format, hq generates modern .jpg thumbnails in color
result_ext="gif" #gif under gray/color, jpg under hq
footer_text=f"<hr>Generated on {datetime.date.today().strftime('%B %d, %Y')} with to-gallery.py, version {version_string}<br> Script (C) 2021, 2022 B.M.Deeal.</body></html>"


def helpScreen():
	"""
	Show the help.
	TODO: make nicer, it's a bit lacking
	"""
	print(f"to-gallery.py v{version_string}\nUtility to generate a basic HTML thumbnail gallery for a folder of images.")
	print("(C) 2021, 2022 B.M.Deeal. Distributed under the ISC license.\n")
	print("usage: to-gallery.py [-mode color|gray|hq] [-xsize size] [-ysize size] [-squaresize size] [-regenerate] [-regenerate-thumbs] [-regenerate-rotated] [-nothumbnails] [-norotate] [-nolucky] galleryname")
	print("For example, to generate a my-pics.html file for a folder named my-pics in the current directory, with 160x120 JPG thumbnails, you might do:")
	print("    to-gallery.py -mode hq -xsize 160 -ysize 120 -regenerate my-pics")

def generatePage(image, image_prev, image_next, number, end, lucky="#"):
	"""
	Generate per-image pages so you can navigate in-order through the gallery.
	This function needs to be refactored, or at least its signature does.
	"""
	#build filenames
	path=os.path.join(gallery_name, page_dir, f"{image}.html")
	prev=f"{image_prev}.html"
	next=f"{image_next}.html"
	lucky=f"{lucky}.html"
	thumb_prev=os.path.join("..", thumb_dir, f"{image_prev}.{result_ext}")
	thumb_next=os.path.join("..", thumb_dir, f"{image_next}.{result_ext}")
	rotate_img=os.path.join("..", rotate_dir, f"{image}.{result_ext}")
	top=os.path.join("..","..",f"{gallery_name_clean}.html")
	top_list=os.path.join("..","..",f"{gallery_name_clean_list}.html")
	pic=os.path.join("..", image)
	title=image #TODO: might remove the extension?
	#build page data:
	#final page data
	result=[f"<html><head><title>{title}</title></head> <body>image {number} of {end}<br>[{title}]<hr>"]
	#text navigation strip
	navparts=[]
	navparts.append(f"<a href='{prev}'>prev</a> | <a href='{next}'>next</a>")
	if thumb_active:
		navparts.append(f" | <a href='{top}'>index (grid)</a>")
	navparts.append(f" | <a href='{top_list}'>index (list)</a>")
	navparts.append(f" | <a href='{pic}'>image</a>")
	if lucky_active:
		navparts.append(f" | <a href='{lucky}'>lucky</a>")
	if rotate_active:
		navparts.append(f" | <a href='{rotate_img}'>rotate</a>")
	navparts.append("<br>")
	#navtext=f"<a href='{prev}'>prev</a> | <a href='{next}'>next</a> | <a href='{top}'>index (grid)</a> | <a href='{top_list}'>index (list)</a> | <a href='{pic}'>image</a> | <a href='{lucky}'>lucky</a> | <a href='{rotate_img}'>rotate</a><br>"
	navtext="".join(navparts)
	#image navigation
	if thumb_active:
		imgtext=f"<a href='{prev}'><img src='{thumb_prev}' width={x_size} height={y_size}></a><a href='{next}'><img src='{thumb_next}' width={x_size} height={y_size}></a><br>"
	else:
		imgtext=f"<a href='{prev}'>[{image_prev}]</a> | <a href='{next}'>[{image_next}]</a><br>"
	#emit page data
	result.append(navtext)
	result.append(imgtext)
	result.append(f"<a href='{next}'><img src='{pic}'></a><br>")
	result.append(imgtext)
	result.append(navtext)
	result.append(footer_text)
	#write to disk
	try:
		with open(path, "w") as ff:
			ff.writelines(result)
	except OSError as e:
		print(f"error: could not write {path}! ({ee})")
		return False
	return True

def generateRotation(path, target):
	"""
	Generate a rotated version of the image.
	TODO: add resize settings (currently, we clamp to 600 width so the rotated image fits on the 640px wide display on a typical Windows CE H/PC device)
	"""
	if mode!="hq":
		command=["convert", path, "-rotate", "90", "-resize", "600>", "-interlace", "GIF", "-colors", "32", target]
	else:
		command=["convert", path, "-rotate", "90", target]
	if subprocess.run(command).returncode != 0:
		return False
	return True

def generateThumbnail(path, target):
	"""
	Generate the thumbnail for an image.
	"""
	#select which command to run
	if mode=="gray":
		command=["convert", path, "-resize", f"{x_size}x{y_size}", "-background", "white", "-gravity", "center", "-extent", f"{x_size}x{y_size}", "-unsharp", "1x0.7+2.5", "-quantize", "Gray", "-colors", "8", "+dither", "-interlace", "GIF", target]
	elif mode=="color":
		command=["convert", path, "-resize", f"{x_size}x{y_size}", "-background", "white", "-gravity", "center", "-extent", f"{x_size}x{y_size}", "-quantize", "sRGB", "-colors", "24", "+dither", "-interlace", "GIF", target]
	elif mode=="hq":
		command=["convert", path, "-resize", f"{x_size}x{y_size}", "-background", "white", "-gravity", "center", "-extent", f"{x_size}x{y_size}", target]
	else:
		print(f"error: invalid mode '{mode}'!")
		return False
	#run the command
	if subprocess.run(command).returncode != 0:
		return False
	return True

def generateFolders():
	"""
	Generate the target folders.
	Returns False if they couldn't be created (and not just because they already exist), True otherwise.
	"""
	try:
		os.makedirs(os.path.join(gallery_name,thumb_dir),exist_ok=True)
		os.makedirs(os.path.join(gallery_name,page_dir),exist_ok=True)
		os.makedirs(os.path.join(gallery_name,rotate_dir),exist_ok=True)
	except OSError:
		return False
	return True

def createGallery():
	"""
	Loop through the file list and generate the main gallery pages.
	Returns False if something went wrong, and True on success.
	"""
	images=getFileList(gallery_name)
	images_lucky=images.copy()
	random.shuffle(images_lucky)
	length=len(images)
	#the main grid-view gallery page
	page_grid_data=[f"<html><head><title>{gallery_name_clean} gallery</title></head> <body>[{gallery_name_clean}]<br>images: {length}<br>grid view"]
	page_grid_data.append(f" | <a href='{gallery_name_clean_list}.html'>[list view]</a><hr>")
	#the list-view gallery page
	page_list_data=[f"<html><head><title>{gallery_name_clean} gallery</title></head> <body>[{gallery_name_clean}]<br>images: {length}<br>list view"]
	if thumb_active:
		page_list_data.append(f" | <a href='{gallery_name_clean}.html'>[grid view]</a>")
	page_list_data.append("<hr>")
	#emit info
	print(f"to-gallery.py v{version_string}.")
	print(f"Generating gallery '{gallery_name_clean}' with {length} images:")
	#deeply unpythonic loop
	for ii in range(0,length):
		#current filename
		image=images[ii]
		image_lucky=images_lucky[ii]
		#stuff for the per-image page, this probably needs to get moved (TODO)
		image_prev=images[(ii-1)%length]
		image_next=images[(ii+1)%length]
		image_target=os.path.join(gallery_name, image)
		page_target=os.path.join(gallery_name, page_dir, f"{image}.html")
		#where to put the thumbnail
		thumb_target=os.path.join(gallery_name, thumb_dir, f"{image}.{result_ext}")
		#where to put rotated images
		rotate_target=os.path.join(gallery_name, rotate_dir, f"{image}.{result_ext}")
		#generate everything, complain on error
		print(f"\nNow processing '{image}' (image {ii+1} of {length}):")
		#generate thumbnails
		if thumb_active and (regenerate or regenerate_thumbs or not os.path.isfile(thumb_target)):
			print(f"Generating thumbnail in '{thumb_target}'...")
			if not generateThumbnail(image_target, thumb_target):
				print(f"warning: could not generate '{thumb_target}'.")
		else:
			print(f"notice: skipping thumbnail generation for '{image}'.")
		#generate rotated images
		#if rotate_active: #TODO
		if rotate_active and (regenerate or regenerate_rotate or not os.path.isfile(rotate_target)):
			print(f"Generating rotated image in '{rotate_target}'...")
			if not generateRotation(image_target, rotate_target):
				print(f"warning: could not generate '{rotate_target}'.")
		else:
			print(f"notice: skipping rotated image generation for '{image}'.")
		#create pages
		print(f"Generating page in '{page_target}'...")
		if not generatePage(image, image_prev, image_next, ii+1, length, image_lucky):
			print(f"error: could not generate page '{page_target}'! Gallery navigation will be somewhat broken.")
		#add each generated thumbnail
		if thumb_active:
			if os.path.exists(thumb_target):
				page_grid_data.append(f"<a href='{page_target}'><img src='{thumb_target}' width={x_size} height={y_size}></a>")
				page_list_data.append(f"<a href='{page_target}'><img src='{thumb_target}' width={x_size} height={y_size}>{image}</a><br>")
		else:
			page_list_data.append(f"<a href='{page_target}'>{image}</a><br>")
	#insert the footer and write out
	page_grid_data.append(footer_text)
	page_list_data.append(footer_text)
	#generate the thumbnail page
	if thumb_active:
		try:
			with open(f"{gallery_name_clean}.html", "w") as ff:
				ff.writelines(page_grid_data)
		except OSError as ee:
			print(f"error: could not write '{gallery_name_clean}.html'! ({ee})")
			return False
	#generate the file list page
	try:
		with open(f"{gallery_name_clean_list}.html", "w") as ff:
			ff.writelines(page_list_data)
	except OSError as ee:
		print(f"error: could not write '{gallery_name_clean_list}.html'! ({ee})")
		return False
	print(f"\nGenerated html gallery pages '{gallery_name_clean}.html' and '{gallery_name_clean_list}.html'.")
	return True

def getFileList(path):
	"""
	Generate a list of images in the given directory, looking for png, gif, and jpeg files.
	Returns the list, sorted.
	"""
	result=[ff.name for ff in os.scandir(path) if not ff.is_dir() and ff.name.lower().endswith((".png", ".gif", ".jpg", ".jpeg"))]
	result.sort()
	return result

def getStr(target, pos):
	"""
	Get a string from a list/whatever.
	Returns the string if in-range, False if out of range.
	"""
	try:
		result=str(target[pos])
		return result
	except IndexError:
		return False

def getInt(target, pos):
	"""
	Get an integer from a list/whatever.
	Returns the integer if in-range, False if out of range.
	"""
	try:
		result=int(target[pos])
		return result
	except IndexError:
		return False
	except ValueError:
		return False

def parseArgs():
	"""
	Parse each of the arguments from the command line.
	Returns True if everything went okay, False otherwise.
	"""
	#TODO: maybe we could have some system to register arguments with a short description, I dunno, would help with help a lot.
	#disgusting pile of globals
	global x_size, y_size, thumbformat, gallery_name, regenerate, gallery_name_clean, gallery_name_clean_list, mode, result_ext, rotate_active, thumb_active, lucky_active, regenerate_thumbs, regenerate_rotate
	length=len(sys.argv)
	#this bit is deeply unpythonic but I dunno how to write it in a nice python way, this really would just be 'for(ii=1, ii<argc; ii++)' in C++ or whatever
	#we edit the value of ii in a lasting way so we can't even do 'for ii in range(1,len(sys.argv))'
	ii=1
	while ii<length:
		current=getStr(sys.argv, ii)
		current_orig=current #we munge the argument so that doing -- instead of just - works
		#couldn't parse somehow
		if current==False:
			return False
		#accept double-dash arguments
		if current.startswith("--"):
			current=current[1:]
		#all the arguments have a leading dash
		#TODO: should handle "--" on its own to indicate end of argument list
		if current.startswith("-"):
			#output format mode
			if current in ("-mode", "-m"):
				ii+=1
				mode=getStr(sys.argv, ii)
				#handle a blank mode
				if mode==False:
					mode=""
				mode=mode.lower()
				#accept any spelling differences
				if mode=="grey":
					mode="gray"
				if mode=="colour":
					mode="color"
				#we don't generate gif files if we're doing high-quality thumbnails
				if mode=="hq":
					result_ext="jpg"
				if not mode in ("color", "gray", "hq"):
					print(f"error: invalid mode '{mode}'!")
					print("Valid modes are 'color', 'gray', 'hq'.")
					return False
			#get help
			elif current in ("-help", "-?", "-h"):
				helpScreen()
				sys.exit(0)
			#square sized thumbnail size
			elif current in ("-squaresize", "-sS"):
				ii+=1
				x_size=getInt(sys.argv, ii)
				y_size=x_size
				if x_size==False:
					print(f"error: could not parse size! Using default of {default_size}...")
					x_size=default_size
					y_size=x_size
			#x-size of thumbnail
			elif current in ("-xsize", "-sX"):
				ii+=1
				x_size=getInt(sys.argv, ii)
				if x_size==False:
					print(f"error: could not parse xsize! Using default of {default_size}...")
					x_size=default_size
			#y-size of thumbnail
			elif current in ("-ysize", "-sY"):
				ii+=1
				y_size=getInt(sys.argv, ii)
				if y_size==False:
					print(f"error: could not parse ysize! Using default of {default_size}...")
					y_size=default_size
			#regenerate all thumbnails+rotated images
			elif current in ("-regenerate", "-r"):
				regenerate=True
			#regenerate all thumbnails
			elif current in ("-regenerate-thumbs", "-rT"):
				regenerate_thumbs=True
			#regenerate all rotated images
			elif current in ("-regenerate-rotated", "-rR"):
				regenerate_thumbs=True
			#disable thumbnail images
			elif current in ("-nothumbnails", "-nT"):
				thumb_active=False
			#disable rotated images
			elif current in ("-norotate", "-nR"):
				rotate_active=False
			elif current in ("-nolucky", "-nL"):
				lucky_active=False
			#nothing
			else:
				print(f"error: invalid argument '{current_orig}'!")
				#TODO: show help
				return False
		#get the path to generate
		#TODO: if we give multiple paths, we should generate multiple galleries
		#mightn't be too hard, we would just probably loop over createGallery or whatever
		else:
			gallery_name=current
			if not os.path.isdir(current):
				print(f"error: '{current}' is not a directory!")
				return False
			gallery_name_clean=gallery_name.strip()
			if gallery_name[-1]=="\\" or gallery_name[-1]=="/":
				gallery_name_clean=gallery_name_clean[:-1]
			gallery_name_clean_list=f"{gallery_name_clean}-list"
		#again, deeeeeeply unpythonic
		ii+=1
	return True

def main():
	"""
	Main program entry point.
	Get the gallery folder and parameters, create the thumbnails, and create HTML pages for the gallery and each image.
	Return code of 1 on error, 0 if everything was okay.
	"""
	#read command line arguments
	if not parseArgs():
		print("fatal error: could not parse arguments!")
		sys.exit(1)
	#check if a target directory was passed
	#this should be a stricter check to be honest, but eh
	if gallery_name.strip()=="":
		helpScreen()
		print("fatal error: no image folder name given!")
		sys.exit(1)
	#setup the two folders
	if not generateFolders():
		print("fatal error: could not create the output folders!")
		sys.exit(1)
	#create the gallery
	if not createGallery():
		print ("fatal error: could not create gallery!")
		sys.exit(1)
	#done
	print("\nAll done.")
	sys.exit(0)

#the usual start
if __name__=="__main__":
	main()
