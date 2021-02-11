from PIL import Image, ImageFont, ImageDraw
import glob
import os


def write_text(n):
    return "Vote: " + str(n+1)


def main():
    # im = Image.open("img/img_2.png")
    # im2 = Image.open("img/img_0.png")
    #
    # print(im.format, im.size, im.mode)
    # print(im2.format, im2.size, im2.mode)
    #
    # im3 = Image.new("RGB", (1000, 500), 0)
    # im3.show()

    infiles = glob.glob(os.path.join('img/*.png'))

    PADDING = 5
    TILE_SIZE = 500, 750
    GAP = 2
    COLS = len(infiles)
    BGCOLOR = '#fff'
    WRITE = True
    FONT_PADDING = 10
    FONT_COLOR = '#fff'

    RESIZE = True

    # Create canvas.
    tile_count = len(infiles)

    ROWS = tile_count // COLS + (1 if tile_count % COLS else 0)
    imgsize = (2 * PADDING + TILE_SIZE[0] * COLS +
               GAP * (COLS - 1),
               2 * PADDING + TILE_SIZE[1] * ROWS +
               GAP * (ROWS - 1))
    img = Image.new('RGB', imgsize, BGCOLOR)

    # Initialize writing.
    if WRITE:
        font = ImageFont.truetype("HappyMonkey-Regular.ttf", 50)

    imgno = 0

    for tile_file in infiles:

        # Tile position.
        pos = imgno
        x = pos % COLS
        y = pos // COLS
        # Offsets.
        xoff = PADDING + x * (TILE_SIZE[0] + GAP)
        yoff = PADDING + y * (TILE_SIZE[1] + GAP)

        tile = Image.open(tile_file)

        # Resize image if necessary!
        if RESIZE and tile.size != TILE_SIZE:
            w_from, h_from = tile.size
            if (w_from / float(h_from) >
                    TILE_SIZE[0] / float(TILE_SIZE[1])):
                w_to = TILE_SIZE[0]
                h_to = int(w_to / float(w_from) * h_from)
            else:
                h_to = TILE_SIZE[1]
                w_to = int(h_to / float(h_from) * w_from)
            tile = tile.resize((w_to, h_to), Image.ANTIALIAS)

        # Place tile on canvas.
        img.paste(tile, (xoff, yoff))

        # Write a number on the image, if desired.
        if WRITE:
            draw = ImageDraw.Draw(img)
            txt = write_text(imgno)

            # Calculate offsets.
            txtsize = draw.textsize(txt, font=font)
            font_xoff = (xoff + TILE_SIZE[0] - txtsize[0] -
                         FONT_PADDING)
            font_yoff = (yoff + TILE_SIZE[1] - txtsize[1] -
                         FONT_PADDING)

            # Finally, draw the number.
            draw.text((font_xoff-150, font_yoff), txt, font=font,
                      fill=FONT_COLOR, stroke_fill="#000000", stroke_width=2)
            del draw

        imgno += 1

    img.save("collage.png")


if __name__ == "__main__":
    main()
