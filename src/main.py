#!/usr/bin/env python3

import argparse
from io import open
import os
from tqdm import tqdm
from PIL import Image#, ImageCms
from datetime import datetime
import re
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

filters = [Image.NEAREST, Image.BILINEAR, Image.BICUBIC,  Image.ANTIALIAS]

filetype = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.psd', '.psb')

def str_filetypes(list_types):
	text = ''
	spacing = ', '
	for single_type in list_types:
		text = text + single_type.strip('.') + spacing
	return text[0:len(text)-len(spacing)]

parser = argparse.ArgumentParser(description=f'Batch image conversion. Filetype: {str_filetypes(filetype)}.')
group_img = parser.add_argument_group('commands', 'Image conversion properties')
group_opt = parser.add_argument_group('other options', 'Customize script behaviour (alert and wait)')

group_img.add_argument(
	"-d",
	"--dpi",
	type=int,
	choices=range(1, 1001),
	metavar="[1-1000]",
	default=72,
	nargs=1,
	help="pixel density in pixels per inch (dpi), must be in range 1-1000 (default: 72)",
)

group_img.add_argument(
	"-s",
	"--size",
	type=int,
	choices=range(1, 10001),
	metavar="[1-10000]",
	default=1000,
	nargs=1,
	help="max resolution of image (long side) in pixel (downscaling only), must be in range 1-10000 (default: 1000)",
)

group_img.add_argument(
	"-f",
	"--filter",
	type=int,
	choices=range(0, 4),
	metavar="[0 = NEAREST, 1 = BILINEAR, 2 = BICUBIC, 3 = ANTIALIAS]",
	default=0,
	nargs=1,
	help="type of filter used for downscaling, must be an integer in range 0-3 (default: 0 = NEAREST)",
)

group_img.add_argument(
	"--colorspace",
	"--cs",
	type=bool,
	default=False,
	action=argparse.BooleanOptionalAction,
	help="convert all images to RGB color space",
)

group_img.add_argument(
	"-q",
	"--quality",
	type=int,
	choices=range(1, 101),
	metavar="[1-100]",
	default=80,
	nargs=1,
	help="quality of output images, must be in range 1-100 (values above 95 should be avoided) (default: 80)",
)

group_img.add_argument(
	"--optimize",
	type=bool,
	default=True,
	action=argparse.BooleanOptionalAction,
	help="attempt to compress the palette by eliminating unused colors",
)

group_opt.add_argument(
	"--alert",
	type=bool,
	default=True,
	action=argparse.BooleanOptionalAction,
	help="play alert sound when finished the conversion",
)

group_opt.add_argument(
	"--wait",
	type=bool,
	default=True,
	action=argparse.BooleanOptionalAction,
	help="wait user keypress (Enter) when finished the conversion",
)


def print_init(args, folder):

	print(f"\nRoot folder: {Fore.BLUE}{str(folder)}\n")
	print(f"Dpi value: {Fore.BLUE}{args.dpi[0]}")
	print(f"Max pixel long side: {Fore.BLUE}{args.size[0]}{Style.RESET_ALL}")
	switcher = { 
        0: 'Nearest',
        1: 'Bilinear',
        2: 'Bicubic',
		3: 'Antialias',
    }
	filter_name = switcher.get(args.filter[0], lambda: 'Nearest')
	print(f"Downscaling filter: {Fore.BLUE}{filter_name}{Style.RESET_ALL}")
	print(f"Output image quality: {Fore.BLUE}{args.quality[0]}{Style.RESET_ALL}", end='')
	if args.quality[0]>95:
		print(f" -> {Fore.YELLOW}WARNING: values above 95 might not decrease file size with hardly any gain in image quality!")
	else:
		print('')
	print(f"Color space conversion: {Fore.BLUE}{args.colorspace}", end='')
	if args.colorspace is True:
		print(f" -> {Fore.YELLOW}WARNING: colorspace conversion from CMYK to RGB may not be accurate!")
	else:
		print('')
	print(f"Mute alert when finished: {Fore.BLUE}{args.alert}")
	print(f"Wait after end of conversion: {Fore.BLUE}{args.wait}", end='')
	if args.wait is True:
		print(f" -> {Fore.GREEN}Press enter to confirm exit when finished.")
	else:
		print('')


def wait_keypress(val):

	try:
		input(f"\n{Fore.YELLOW}Press {Back.BLACK}{Style.BRIGHT}Enter{Style.NORMAL}{Back.RESET} to {val}{Style.RESET_ALL}")
	except SyntaxError:
		pass


def main(args):
	
	folder = os.path.realpath(__file__).rsplit(os.sep, 1)[0]
	
	print_init(args, folder)
	
	exception_files = []
	other_files = []
	MAX_SIZE = (args.size[0], args.size[0])
	DPI = (args.dpi[0], args.dpi[0])
	count = 0
	
	wait_keypress(f"continue or {Back.BLACK}{Style.BRIGHT}CTRL+C{Style.NORMAL}{Back.RESET} to abort")
	
	print("\nProcessing images")
	
	startTime = datetime.now()
	
	for root, dirnames, filenames in tqdm(list(os.walk(folder)), unit_divisor=100, colour='green', bar_format='{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt} Folders | Elapsed: {elapsed} | Remaining: {remaining}'):
		for filename in filenames:
			if filename.endswith(filetype):
				image_path = root + os.sep + filename
				try:
					img = Image.open(image_path)
				except:
					exception_files.append([root, filename])
				else:
					if filename.lower().endswith('.png'):
						colour_space = 'RGBA'
					else:
						colour_space = 'RGB'
					
					img.thumbnail(MAX_SIZE, filters[args.filter[0]])
					if args.colorspace is True:
						if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
							new_image_path = image_path.rsplit('.', 1)[0] + '.jpg'
							img.convert(colour_space).save(new_image_path, dpi=DPI, quality=args.quality[0], optimize=args.optimize)
							os.remove(image_path)
						else:
							img.convert(colour_space).save(image_path, dpi=DPI, quality=args.quality[0], optimize=args.optimize)
					else:
						if not (filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')):
							new_image_path = image_path.rsplit('.', 1)[0] + '.jpg'
							img.save(new_image_path, dpi=DPI, quality=args.quality[0], optimize=args.optimize)
							os.remove(image_path)
						else:
							img.save(image_path, dpi=DPI, quality=args.quality[0], optimize=args.optimize)
					count+=1
				
			else:
				other_files.append([root, filename])
	
	time_exec = (datetime.now() - startTime)
	
	str_time = re.match(r'(.+)\.(.+)', str(time_exec), re.M|re.I).group(1).replace(":", "h ", 1).replace(":", "m ", 1)+'s'
	print(f"\nTime to complete: {Fore.GREEN}{str_time}")
	
	print(f"Total number of converted images: {Fore.GREEN}{count}")
	
	if len(exception_files)>0:
		plural_s = ''
		if len(exception_files)>1:
			plural_s = 's'
		print(f"\n{Fore.RED}{len(exception_files)}{Style.RESET_ALL} Corrupted image{plural_s}:")
		for excpt in exception_files:
			print(f"-> {Fore.RED}{excpt[1]}{Style.RESET_ALL} found in {Fore.RED}{excpt[0]}")
	else:
		print("No corrupted images found.")
	
	if len(other_files)==1:
		print("No other files found.")
	else:
		print("\nOther files (not converted):")
		for other in other_files:
			if other[1]!=os.path.basename(__file__):
				print(f"-> {Fore.CYAN}{other[1]}{Style.RESET_ALL} found in {Fore.CYAN}{other[0]}")
	if args.alert is True:
		print('\a', end='')
	if args.wait is True:
		wait_keypress(f"exit")


if __name__ == "__main__":

	main(parser.parse_args())
