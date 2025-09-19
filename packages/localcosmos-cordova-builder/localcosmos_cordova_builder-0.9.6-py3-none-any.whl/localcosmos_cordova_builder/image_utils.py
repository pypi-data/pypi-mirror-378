# requires inkscape to be installed

import subprocess, sys, os
from subprocess import CalledProcessError, PIPE, check_output

from PIL import Image, ImageOps

class SVGToBitmapError(Exception):
    pass

class ImageMagickError(Exception):
    pass


def query_svg(svg_filepath):

    if not os.path.isfile(svg_filepath):
        raise FileNotFoundError(svg_filepath)

    # return a tuple (x,y,width,height)
    x_output = check_output(["inkscape", "--query-x", svg_filepath])
    svg_x = float(x_output)

    y_output = check_output(["inkscape", "--query-y", svg_filepath])
    svg_y = float(y_output)

    width_output = check_output(["inkscape", "--query-width", svg_filepath])
    svg_width = float(width_output)

    height_output = check_output(["inkscape", "--query-height", svg_filepath])
    svg_height = float(height_output)
    
    svg_info = (svg_x, svg_y, svg_width, svg_height)

    return svg_info

# bug in inkscape 1.2 returns returncode -11 and an error, although png gets created
# https://gitlab.com/inkscape/inbox/-/issues/7106
def create_png_from_svg(svg_filepath, width, height, destination_filepath):

    version_command = ["inkscape", "-V"]

    version_process = subprocess.run(version_command, stdout=PIPE, stderr=PIPE)
  
    installed_inkscape_version = 0
    try:
        installed_inkscape_version_str = str(version_process.stdout).split(' ')[1]
        version_parts = installed_inkscape_version_str.split('.')
        major_version = version_parts[0]
        subversion = version_parts[1]
        installed_inkscape_version = float('{0}.{1}'.format(major_version, subversion))
    except:
        pass

    if installed_inkscape_version >= 1.2:

        command = ["inkscape", "--export-filename={0}".format(destination_filepath),
                    "--export-width={0}".format(width),
                    "--export-height={0}".format(height), svg_filepath]

        process_completed = subprocess.run(command, stdout=PIPE, stderr=PIPE)

        if process_completed.returncode not in [0, -11]:
            raise SVGToBitmapError(process_completed.stderr)

    
    else:
    
        if sys.platform == 'darwin':
            command = ["inkscape", "--export-file={0}".format(destination_filepath),
                    "--export-type=png", "--export-width={0}".format(width),
                    "--export-height={0}".format(height), svg_filepath]

        else:
            command = ["inkscape", "--export-png={0}".format(destination_filepath),
                    "--export-width={0}".format(width),
                    "--export-height={0}".format(height), svg_filepath]
        

        process_completed = subprocess.run(command, stdout=PIPE, stderr=PIPE)

        if process_completed.returncode != 0:
            raise SVGToBitmapError(process_completed.stderr)



# image with border
def create_png_border(png_filepath, border_width, border_color):
    image = Image.open(png_filepath)
    image_with_border = ImageOps.expand(image, border=border_width, fill=border_color)
    image_with_border.save(png_filepath)
    

# first, export a png from svg that maintains proportions
# cut the png to correct size
def create_resized_png_from_svg(svg_filepath, width, height, destination_filepath):

    svg_x, svg_y, svg_width, svg_height = query_svg(svg_filepath)

    # determine x-difference and y-difference
    x_diff = svg_width - width
    y_diff = svg_height - height

    # x-difference is smaller than (or equal to) y-difference
    if x_diff <= y_diff:
        # scale_axis = 'x'
        scale_factor = width/svg_width

    else:
        # scale_axis = 'y'
        scale_factor = height/svg_height

    # this creates a png which is larger than the target size
    export_width = int(svg_width * scale_factor)
    export_height = int(svg_height * scale_factor)

    create_png_from_svg(svg_filepath, export_width, export_height, destination_filepath)

    # cut the png
    size = (width, height)
    image_file = Image.open(destination_filepath)
    image_file_cropped = ImageOps.fit(image_file, size, Image.LANCZOS, bleed=0, centering=(0.5, 0.5))
    image_file_cropped.save(destination_filepath, 'PNG')
    
    
def remove_alpha_channel_from_png(png_filepath):
    """
    Removes the alpha channel from a PNG file by replacing it with a white background.
    Supports both 'convert' (older ImageMagick) and 'magick' (newer ImageMagick versions).
    """
    # Determine which command to use: 'convert' or 'magick'
    command_base = None
    try:
        # Check if 'magick' is available
        subprocess.run(['magick', '-version'], stdout=PIPE, stderr=PIPE, check=True)
        command_base = ['magick', 'convert']
    except FileNotFoundError:
        try:
            # Check if 'convert' is available
            subprocess.run(['convert', '-version'], stdout=PIPE, stderr=PIPE, check=True)
            command_base = ['convert']
        except FileNotFoundError:
            raise ImageMagickError("Neither 'magick' nor 'convert' command is available. Please install ImageMagick.")

    # Build the command
    command = command_base + [png_filepath, '-background', 'white', '-alpha', 'remove', '-alpha', 'off', png_filepath]

    # Run the command
    process_completed = subprocess.run(command, stdout=PIPE, stderr=PIPE)

    if process_completed.returncode != 0:
        raise ImageMagickError(process_completed.stderr.decode('utf-8'))

