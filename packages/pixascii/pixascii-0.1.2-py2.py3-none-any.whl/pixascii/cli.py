# -*- coding: utf-8 -*-

import sys
from PIL import Image

# ASCII characters from dark to light
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100, new_height=None):
    width, height = image.size

    if new_height is None:
        # Adjusted ratio for typical console font aspect ratio
        ratio = height / width * 0.55
        new_height = max(1, int(new_width * ratio))
    else:
        new_height = max(1, new_height)

    return image.resize((new_width, new_height))

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    n_chars = len(ASCII_CHARS)
    return "".join(ASCII_CHARS[min(pixel * n_chars // 256, n_chars - 1)] for pixel in pixels)

def pixels_to_ascii_with_color(image, resized_image):
    """
    Convert the resized image to ASCII, preserving original pixel colors
    using ANSI escape codes for terminal color.
    """
    gray_img = grayify(resized_image)
    ascii_chars = pixels_to_ascii(gray_img)

    rgb_img = resized_image.convert("RGB")
    pixels = list(rgb_img.getdata())

    ascii_img = ""
    width = resized_image.width

    for i, char in enumerate(ascii_chars):
        r, g, b = pixels[i]
        ascii_img += f"\x1b[38;2;{r};{g};{b}m{char}"
        if (i + 1) % width == 0:
            ascii_img += "\x1b[0m\n"  # reset color and newline

    return ascii_img

def main(image_path, output_file=None, width=100, height=None, color=False):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Unable to open image: {e}")
        return

    resized = resize_image(image, new_width=width, new_height=height)

    if color:
        ascii_img = pixels_to_ascii_with_color(image, resized)
    else:
        gray = grayify(resized)
        ascii_str = pixels_to_ascii(gray)
        img_width = resized.width
        ascii_img = "\n".join(ascii_str[i:i+img_width] for i in range(0, len(ascii_str), img_width))

    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ascii_img)
            print(f"ASCII art saved to {output_file}")
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print(ascii_img)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert images to ASCII art")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("-o", "--output", help="File to save ASCII art")
    parser.add_argument("-w", "--width", type=int, default=100, help="Width of ASCII output")
    parser.add_argument("-H", "--height", type=int, default=None, help="Height of ASCII output (overrides auto height)")
    parser.add_argument("-c", "--color", action="store_true", help="Output colored ASCII art")
    args = parser.parse_args()

    main(args.image, args.output, args.width, args.height, args.color)
