#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import datetime
from io import open
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageTk
from tqdm import tqdm
import colorama
from colorama import Fore, Back, Style
import requests
from packaging import version

__author__ = "Edoardo Tosin"
__copyright__ = "Copyright (C) 2022-24 Edoardo Tosin"
__credits__ = "Edoardo Tosin"
__license__ = "GPL-3.0"
__version__ = "1.3.2"

Image.MAX_IMAGE_PIXELS = 9e9

filetype = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp')
exception_files = []
converted_count = 0


def str_filetypes(list_types):
    text = ''
    spacing = ', '
    for single_type in list_types:
        text = text + single_type.strip('.') + spacing
    return text[0:len(text) - len(spacing)]


def get_update():
    try:
        release_path = "/EdoardoTosin/Batch-Image-Converter/releases/latest"
        api_url = "https://api.github.com/repos" + release_path
        response = requests.get(api_url)
        latest_release = response.json()["tag_name"].strip("v")
        if version.parse(__version__) < version.parse(latest_release):
            latest_page_url = "https://github.com" + release_path
            messagebox.showinfo(
                "Update Available",
                f"New Version {latest_release} is available.\nPlease visit {latest_page_url} to download.",
            )
        else:
            messagebox.showinfo(
                "Version Check",
                f"Batch-Image-Converter is up to date ({__version__})",
            )
    except:
        messagebox.showwarning("Version Check", "Unable to check latest version")


def open_folder():
    folder_path = filedialog.askdirectory()
    path_var.set(folder_path)


def start_conversion():
    args = parse_arguments()
    main(args)


def parse_arguments():
    args = argparse.Namespace()
    args.path = path_var.get()
    args.dpi = dpi_var.get()
    args.size = size_var.get()
    args.filter = filter_var.get()
    args.colorspace = colorspace_var.get()
    args.quality = quality_var.get()
    args.max_image_mpixels = max_image_var.get()
    args.optimize = optimize_var.get()
    args.alert = alert_var.get()
    args.wait = wait_var.get()
    return args


def print_init(args):
    output_text = (
        f"\nRoot folder: {args.path}\n"
        f"Dpi value: {args.dpi}\n"
        f"Max pixel long side: {args.size}\n"
        f"Downscaling filter: {args.filter}\n"
        f"Output image quality: {args.quality}"
    )
    if args.quality > 95:
        output_text += (
            " -> WARNING: values above 95 might not decrease file size with hardly any gain in image quality!"
        )
    output_text += (
        f"\nColor space conversion: {args.colorspace}\n"
        f"Mute alert when finished: {args.alert}\n"
        f"Wait after end of conversion: {args.wait}"
    )
    if args.wait:
        output_text += " -> Press enter to confirm exit when finished."
    output_label.config(text=output_text)


def process_image(args, root_path, filename):
    global converted_count
    if args.max_image_mpixels > 0:
        Image.MAX_IMAGE_PIXELS = args.max_image_mpixels
    MAX_SIZE = (args.size, args.size)
    filters = [
        Image.Resampling.NEAREST,
        Image.Resampling.BILINEAR,
        Image.Resampling.BICUBIC,
        Image.Resampling.LANCZOS,
    ]
    DPI = (args.dpi, args.dpi)

    image_path = os.path.join(root_path, filename)

    try:
        img = Image.open(image_path)
    except:
        if [root_path, filename] not in exception_files:
            exception_files.append([root_path, filename])
    else:
        if filename.lower().endswith(".png"):
            colour_space = "RGBA"
        else:
            colour_space = "RGB"

        img.thumbnail(MAX_SIZE, Image.Resampling(args.filter))
        if args.colorspace:
            if not (
                filename.lower().endswith(".png")
                or filename.lower().endswith(".jpg")
                or filename.lower().endswith(".jpeg")
            ):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.convert(colour_space).save(
                    new_image_path,
                    dpi=DPI,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.convert(colour_space).save(
                    image_path, dpi=DPI, quality=args.quality, optimize=args.optimize
                )
                img.close()
        else:
            if not (
                filename.lower().endswith(".png")
                or filename.lower().endswith(".jpg")
                or filename.lower().endswith(".jpeg")
            ):
                new_image_path = os.path.splitext(image_path)[0] + ".jpg"
                img.save(
                    new_image_path,
                    dpi=DPI,
                    quality=args.quality,
                    optimize=args.optimize,
                )
                img.close()
                os.remove(image_path)
            else:
                img.save(
                    image_path, dpi=DPI, quality=args.quality, optimize=args.optimize
                )
                img.close()
        converted_count += 1


def wait_keypress(val):
    
    try:
        print(f"\n{Fore.YELLOW}Press {Back.BLACK}{Style.BRIGHT}Enter{Style.NORMAL}{Back.RESET} to {val}{Style.RESET_ALL}", end='')
        press = input()
    except SyntaxError:
        pass


def main(args):
    #print_init(args)

    other_files = []

    for root_path, dirnames, filenames in os.walk(args.path):
        for filename in filenames:
            if not filename.lower().endswith(filetype):
                other_files.append([root_path, filename])

    print("\nProcessing images")

    startTime = datetime.now()

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_image, args, root_path, filename)
            for root_path, _, filenames in os.walk(args.path)
            for filename in filenames
            if filename.lower().endswith(filetype)
        ]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            unit_divisor=100,
            colour="green",
            bar_format="{desc}: {percentage:3.0f}% | {bar} | {n_fmt}/{total_fmt} Files | Elapsed: {elapsed} | Remaining: {remaining}",
        ):
            try:
                data = future.result()
            except Exception as exc:
                if [root_path, filename] not in exception_files:
                    exception_files.append([root_path, filename])

    time_exec = datetime.now() - startTime

    str_time = str(time_exec).split(".")[0].replace(":", "h ", 1).replace(
        ":", "m ", 1
    ) + "s"
    output_label.config(
        text=(
            f"Time to complete: {str_time}\n"
            f"Total number of converted images: {converted_count}\n"
        )
    )

    if len(exception_files) > 0:
        plural_s = ""
        if len(exception_files) > 1:
            plural_s = "s"
        output_label.config(
            text=(
                output_label.cget("text")
                + f"\n{len(exception_files)} Corrupted image{plural_s}:\n"
            )
        )
        for excpt in exception_files:
            output_label.config(
                text=(
                    output_label.cget("text")
                    + f"-> {excpt[1]} found in {excpt[0]}\n"
                )
            )
    else:
        output_label.config(
            text=(output_label.cget("text") + "No corrupted images found.\n")
        )
    '''
    if len(other_files) == 1:
        output_label.config(
            text=(output_label.cget("text") + "No other files found.\n")
        )
    else:
        output_label.config(
            text=(output_label.cget("text") + "\nOther files (not converted):\n")
        )
        for other in other_files:
            if other[1] != os.path.basename(__file__):
                output_label.config(
                    text=(
                        output_label.cget("text")
                        + f"-> {other[1]} found in {other[0]}\n"
                    )
                )
    '''
    messagebox.showinfo("Conversion Complete", "Image conversion is complete.")
    
    if alert_var.get():
        root.bell()
    if wait_var.get():
        wait_keypress("exit")


root = Tk()
root.title("Batch Image Converter")

# Set the icon logo
root.iconbitmap('../assets/logo.ico')

# Variables
path_var = StringVar()
dpi_var = IntVar(value=72)
size_var = IntVar(value=1000)
filter_var = StringVar(value="Nearest")  # Default value is "Nearest"
colorspace_var = BooleanVar()
quality_var = IntVar(value=80)
max_image_var = IntVar(value=0)
optimize_var = BooleanVar(value=True)
alert_var = BooleanVar(value=True)
wait_var = BooleanVar(value=True)

# Filter options mapping
filter_options = {
    "Nearest": 0,
    "Box": 4,
    "Bilinear": 2,
    "Hamming": 5,
    "Bicubic": 3,
    "Lanczos": 1
}

# GUI Elements
Label(root, text="Root Folder:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
Entry(root, textvariable=path_var, width=50).grid(
    row=0, column=1, columnspan=3, sticky=W, padx=5, pady=5
)
Button(root, text="Browse", command=open_folder).grid(
    row=0, column=4, sticky=W, padx=5, pady=5
)

Label(root, text="DPI:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
Entry(root, textvariable=dpi_var, width=10).grid(
    row=1, column=1, sticky=W, padx=5, pady=5
)

Label(root, text="Max Pixel Long Side:").grid(
    row=1, column=2, sticky=W, padx=5, pady=5
)
Entry(root, textvariable=size_var, width=10).grid(
    row=1, column=3, sticky=W, padx=5, pady=5
)

Label(root, text="Filter:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
OptionMenu(
    root,
    filter_var,
    *filter_options.keys(),  # Use keys of the filter_options dictionary
).grid(row=2, column=1, sticky=W, padx=5, pady=5)

Checkbutton(root, text="Convert to RGB", variable=colorspace_var).grid(
    row=2, column=2, sticky=W, padx=5, pady=5
)

Label(root, text="Quality:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
Entry(root, textvariable=quality_var, width=10).grid(
    row=3, column=1, sticky=W, padx=5, pady=5
)

Label(root, text="Max Image Megapixels:").grid(
    row=3, column=2, sticky=W, padx=5, pady=5
)
Entry(root, textvariable=max_image_var, width=10).grid(
    row=3, column=3, sticky=W, padx=5, pady=5
)

Checkbutton(root, text="Optimize", variable=optimize_var).grid(
    row=4, column=0, sticky=W, padx=5, pady=5
)

Checkbutton(root, text="Mute Alert", variable=alert_var).grid(
    row=4, column=1, sticky=W, padx=5, pady=5
)

Checkbutton(root, text="Wait after Conversion", variable=wait_var).grid(
    row=4, column=2, sticky=W, padx=5, pady=5
)

Button(root, text="Start Conversion", command=start_conversion).grid(
    row=5, column=0, columnspan=5, pady=10
)

output_label = Label(root, text="", justify=LEFT)
output_label.grid(row=6, column=0, columnspan=5, padx=10, pady=10)

completion_label = Label(root, text="", justify=LEFT)
completion_label.grid(row=7, column=0, columnspan=5, padx=10, pady=10)

root.mainloop()
