"""
Name:           retropil.py    
Author:         Mark Bradley (github.com/mtbradley)
Description:    Generate various images with effects using Python's PIL module and numpy
Requirements:   Python 3 with Pillow (PIL) and numpy modules installed
License:        MIT (https://opensource.org/licenses/MIT)

                -- Refer to README.md for source code credit and references
"""

from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageOps
import numpy as np
from pathlib import Path
from glob import glob


def show_banner():
    print(f'''
 ___   ____ _____  ___   ___   ___   _   _    
| |_) | |_   | |  | |_) / / \ | |_) | | | |   
|_| \ |_|__  |_|  |_| \ \_\_/ |_|   |_| |_|__                                                             
''')
    print(__doc__)


class RetroImage:
    # Default class values
    dst_path = 'output/'
    fg_colour = '#000000'
    bg_colour_list = ['#FF82E2', '#FED715', '#0037B3', '#70BAFF', '#FFFFFF']
    include_transparent = False
    fixed_size = None
    fixed_width = None
    fixed_height = None
    popart_dots_max = 160
    pixelate_size = 12
    pixelate_colour_count_list = [8, 16, 32, 64, 128]
    pixelate_adjustment = 160
    asciiart_font = 'fonts/firacode.ttf'
    asciiart_chars = ' .,:irs?@9B&#'

    def __init__(self, src_file, image_inverted=False):
        self.src_file = src_file
        self.image_inverted = image_inverted
        self.original_image = Image.open(self.src_file)
        self.original_filename = (Path(self.src_file).stem).lower()
        self.working_image = self.resizer(
            self.original_image, set_antialias=True)
        if self.image_inverted:
            self.working_image = ImageOps.invert(self.working_image)
            self.original_filename += '_inverted'
        self.working_image_width, self.working_image_height = self.working_image.size

    def save_image(self, input_image, add_text):
        filename = (
            f'{self.dst_path}{self.original_filename}_{input_image.size[0]}x{input_image.size[1]}_{add_text}.png').lower()
        input_image.save(filename)
        print(f'Saved file: {filename}', end="\n", flush=True)

    def resizer(self, ascii_working_image, set_antialias=False):
        if set_antialias:
            scale_method = 'Image.ANTIALIAS'
        else:
            scale_method = 'Image.NEAREST'
        # Resize image depending on fixed value and maintain aspect ratio
        ascii_working_image_width, ascii_working_image_height = ascii_working_image.size
        if self.fixed_width:
            # If a fixed width has been set, image width will be set to self.fixed_width.
            wpercent = (self.fixed_width/float(ascii_working_image_width))
            hsize = int((float(ascii_working_image_height)*float(wpercent)))
            output_image = ascii_working_image.resize(
                (self.fixed_width, hsize), eval(scale_method))
        elif self.fixed_height:
            # If a fixed height has been set, image height will be set to: self.fixed_height.
            hpercent = (self.fixed_height/float(ascii_working_image_height))
            wsize = int((float(ascii_working_image_width)*float(hpercent)))
            output_image = ascii_working_image.resize(
                (wsize, self.fixed_height), eval(scale_method))
        elif self.fixed_size:
            # If self.fixed_size is set the largest side of the image will be set to self.fixed_size
            if ascii_working_image_height == max(ascii_working_image_height, ascii_working_image_width):
                # if input image is landscape, width will be set to: self.fixed_size.
                hpercent = (self.fixed_size/float(ascii_working_image_height))
                wsize = int((float(ascii_working_image_width)*float(hpercent)))
                output_image = ascii_working_image.resize(
                    (wsize, self.fixed_size), eval(scale_method))
            else:
                # If input image is portrait, height will be set to: self.fixed_size.
                wpercent = (self.fixed_size/float(ascii_working_image_width))
                hsize = int(
                    (float(ascii_working_image_height)*float(wpercent)))
                output_image = ascii_working_image.resize(
                    (self.fixed_size, hsize), eval(scale_method))
        return output_image

    def popart(self):
        print('\n### Generating pop art images...')
        for colour_count, hex_colour in enumerate(self.bg_colour_list):
            rgb_bg = ImageColor.getrgb(hex_colour)
            rgb_fg = ImageColor.getrgb(self.fg_colour)
            grayscale_image = self.working_image.convert(
                "L")  # Convert to grayscale
            # down size to number of dots
            if self.working_image_height == max(self.working_image_height, self.working_image_width):
                downsized_image = grayscale_image.resize(
                    (int(self.working_image_width * (self.popart_dots_max / self.working_image_height)), self.popart_dots_max))
            else:
                downsized_image = grayscale_image.resize((self.popart_dots_max, int(
                    self.working_image_height * (self.popart_dots_max / self.working_image_width))))
            # image size
            downsized_image_width, downsized_image_height = downsized_image.size
            # increase target image size
            multiplier = 48
            # set size for target image
            blank_img_height = downsized_image_height * multiplier
            blank_img_width = downsized_image_width * multiplier
            # set the padding value so the dots start in frame (rather than being off the edge
            padding = int(multiplier / 3)
            # create canvas containing just the background colour
            blank_image = np.full(
                ((blank_img_height), (blank_img_width), 3), rgb_bg, dtype=np.uint8
            )
            # prepare for drawing circles on our target image
            popart_bg_image = Image.fromarray(blank_image)
            draw = ImageDraw.Draw(popart_bg_image)
            downsized_image = np.array(downsized_image)

            # run through each pixel and draw the circle on our blank canvas
            for y in range(0, downsized_image_height):
                for x in range(0, downsized_image_width):
                    k = (x * multiplier) + padding
                    m = (y * multiplier) + padding
                    r = int((0.6 * multiplier) *
                            ((255 - downsized_image[y][x]) / 255))
                    leftUpPoint = (k - r, m - r)
                    rightDownPoint = (k + r, m + r)
                    twoPointList = [leftUpPoint, rightDownPoint]
                    draw.ellipse(twoPointList, fill=rgb_fg)

            popart_bg_image = self.resizer(popart_bg_image)
            self.save_image(
                popart_bg_image, f'popart_fg_{self.fg_colour.strip("#")}_bg_{hex_colour.strip("#")}')
            # Make a transparent background version once coloured versions are finished.
            if colour_count == len(self.bg_colour_list)-1:
                if self.include_transparent:
                    popart_trans_image = popart_bg_image.convert("RGBA")
                    datas = popart_trans_image.getdata()
                    new_data = []
                    for item in datas:
                        if item[0] == rgb_bg[0] and item[1] == rgb_bg[1] and item[2] == rgb_bg[2]:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)

                    popart_trans_image.putdata(new_data)
                    self.save_image(
                        popart_trans_image, f'popart_fg_{self.fg_colour.strip("#")}_bg_transparent')

    def pixelart(self):
        # Scale pixelate size to produce consistent results regardless of resolution
        set_pixelate_size = int(
            max(self.working_image_width, self.working_image_height)/self.pixelate_adjustment)
        if set_pixelate_size < 2:
            set_pixelate_size = 2
        print(
            f'\n### Generating pixel art images with pixelate size {set_pixelate_size}...')
        for colours in self.pixelate_colour_count_list:
            pixel_image = self.working_image.convert(
                'P', palette=Image.ADAPTIVE, colors=colours)
            pixel_image = pixel_image.resize(
                (pixel_image.size[0] // set_pixelate_size,
                 pixel_image.size[1] // set_pixelate_size),
                Image.NEAREST
            )
            pixel_image = pixel_image.resize(
                (pixel_image.size[0] * set_pixelate_size,
                 pixel_image.size[1] * set_pixelate_size),
                Image.NEAREST
            )
            # Fix image size when not exact by running through resizer function again prior to saving
            pixel_image = self.resizer(pixel_image)
            self.save_image(pixel_image, f'pixelart_{colours}_colour')

    def asciiart(self):

        # (Modified from original source: https://wshanshan.github.io/python/asciiart/)
        # Copyright 2017, Shanshan Wang, MIT license

        print(f'\n### Generating ascii art images...')
        ascii_working_image = self.working_image
        baseline_width = 1000
        baseline_pixel_width = 0.09
        baseline_percentage = round(
            float(baseline_width / ascii_working_image.size[0]), 2)
        # pixel sampling rate in width
        pixel_sample_width = round(
            float(baseline_pixel_width * baseline_percentage), 2)
        font_size = 32
        contrast = 2      # contrast adjustment
        chars = np.asarray(list(self.asciiart_chars))
        # chars = np.asarray(list(' .:-=+*#%@'))
        font = ImageFont.truetype(self.asciiart_font, font_size)
        letter_width = font.getsize("x")[0]
        letter_height = font.getsize("x")[1]
        letter_h_div_w = (letter_height/letter_width)

        # open the input file

        # Based on the desired output image size, calculate how many ascii letters are needed on the width and height
        width_by_letter = round(
            ascii_working_image.size[0]*pixel_sample_width*letter_h_div_w)
        height_by_letter = round(
            ascii_working_image.size[1]*pixel_sample_width)
        S = (width_by_letter, height_by_letter)

        # Resize the image based on the symbol width and height
        ascii_working_image = ascii_working_image.resize(S)

        # Get the RGB color values of each sampled pixel point and convert them to graycolor using the average method.
        # Refer to https://www.johndcook.com/blog/2009/08/24/algorithms-convert-color-grayscale/ to know about the algorithm
        ascii_working_image = np.sum(np.asarray(ascii_working_image), axis=2)

        # Normalize the results, enhance and reduce the brightness contrast.
        # Map grayscale values to bins of symbols
        ascii_working_image -= ascii_working_image.min()
        ascii_working_image = (1.0 - ascii_working_image /
                               ascii_working_image.max())**contrast*(chars.size-1)

        # Generate the ascii art symbols
        lines = ("\n".join(("".join(r)
                            for r in chars[ascii_working_image.astype(int)]))).split("\n")

        # Create an image object, set its width and height
        set_letter_width = letter_width * width_by_letter
        set_letter_height = letter_height * height_by_letter

        for colour_count, hex_colour in enumerate(self.bg_colour_list):
            #rgb_bg = ImageColor.getrgb(hex_colour)
            asciiart_bg_image = Image.new(
                "RGBA", (set_letter_width, set_letter_height), hex_colour)
            if self.include_transparent:
                if colour_count == len(self.bg_colour_list)-1:
                    asciiart_trans_image = Image.new(
                        "RGBA", (set_letter_width, set_letter_height), (255, 255, 255, 0))
                    draw_trans = ImageDraw.Draw(asciiart_trans_image)
            draw = ImageDraw.Draw(asciiart_bg_image)

            # Print symbols to image
            left_padding = 0
            top_padding = 0
            lineIdx = 0
            for line in lines:
                lineIdx += 1

                draw.text((left_padding, top_padding),
                          line, self.fg_colour, font=font)
                if colour_count == len(self.bg_colour_list)-1:
                    if self.include_transparent:
                        draw_trans.text((left_padding, top_padding),
                                        line, self.fg_colour, font=font)
                top_padding += letter_height

            asciiart_bg_image = self.resizer(asciiart_bg_image)
            self.save_image(
                asciiart_bg_image, f'asciiart_fg_{self.fg_colour.strip("#")}_bg_{hex_colour.strip("#")}')
            if colour_count == len(self.bg_colour_list)-1:
                if self.include_transparent:
                    asciiart_trans_image = self.resizer(asciiart_trans_image)
                    self.save_image(
                        asciiart_trans_image, f'asciiart_fg_{self.fg_colour.strip("#")}_bg_transparent')


def main():
    show_banner()
    # Change/overwrite default Class variables as follows:

    # Set image sizes by setting one of the following three lines only.
    # Note: fixed_side will set largest one of the image sides can be could be
    # height or width based on if the image is landscape or portrait
    # RetroImage.fixed_size = 3000
    RetroImage.fixed_width = 1920
    # RetroImage.fixed_height = 3000

    # Set output destination for saved images default = 'output/'
    RetroImage.dst_path = 'output/'

    # Include a transparent background version of the image generated.
    # Applies to popart and ascii art - default = False
    RetroImage.include_transparent = True

    # Change default characters used in ascii art
    #RetroImage.asciiart_chars = ' 1010000'

    # Change the default max dots used in pop art - default 160
    RetroImage.popart_dots_max = 130

    # Uncomment and customise one of the following examples.

    # Example 1. - use for a single image using default Class variables
    # Sets bg and fg colours and inverts image for terminal effect
    # new_image = RetroImage('input/eagle.jpg')
    # new_image.popart()
    # new_image.pixelart()
    # new_image.asciiart()

    # Example 2. - use for batch processing a folder/directory of image files
    batch_images = glob(f'input/*.jpg') + glob(f'input/*.png')
    for image in batch_images:
        new_image = RetroImage(image)
        new_image.popart()
        new_image.pixelart()
        new_image.asciiart()

    # Example 3. Shows use for a single image setting instance variables
    # Example sets bg and fg colours and runs all three generators
    # new_image = RetroImage('input/woman.jpg')
    # new_image.bg_colour_list = ['#87b805']
    # new_image.fg_colour = "#794597"
    # new_image.popart()
    # new_image.pixelart()
    # new_image.asciiart()

    # Example 4. - Shows use for a single inverted image and setting custom instance variables
    # Example sets custom bg and fg colours to appear like a green terminal image
    # Only runs ascii art generator
    # new_image = RetroImage('input/dog.jpg', image_inverted=True)
    # new_image.asciiart_chars = ' 1010000'
    # new_image.bg_colour_list = ['#000000']
    # new_image.fg_colour = "#41FF00"
    # new_image.asciiart()


if __name__ == "__main__":
    main()
