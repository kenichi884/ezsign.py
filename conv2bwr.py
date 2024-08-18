import math
from PIL import Image
import argparse 
parser = argparse.ArgumentParser(description='Image color reduction to Black White Red', usage='infile outfile')
parser.add_argument('infilename', help='Image file to convert to Black White Red image.')
parser.add_argument('outfilename', help='output filename')
parser.add_argument('-b', '--blackonly', action='store_true')
parser.add_argument('--avoidresize', action='store_true')
parser.add_argument('--huerange', type=int, default=20)
parser.add_argument('--redvalue', type=int, default= 170)
args = parser.parse_args()

WIDTH = 400
HEIGHT = 300

loadedimage = Image.open(args.infilename)
cx, cy = loadedimage.size
if args.avoidresize == False:
    if cx != WIDTH or cy != HEIGHT :
        loadedimage = loadedimage.resize((WIDTH, HEIGHT))
        cx = WIDTH
        cy = HEIGHT
bwimage = loadedimage.convert('1')


red  = Image.new('L', (cx, cy));
if args.blackonly == False:
    hue, saturation, value = loadedimage.convert('HSV').split()
    h = hue.load()
    s = saturation.load()
    v = value.load()
    dst = red.load()
    for y in range(cy):
        for x in range(cx):
            if h[x, y] > (255 - args.huerange) or h[x, y] < args.huerange:
                p = int((v[x, y] + s[x, y]) / 2)
                if p > args.redvalue :
                    dst[x, y] = p
red_mask = red.convert('1')

red = Image.new('RGB', loadedimage.size, (255, 0, 0))
img = bwimage.convert('RGB')
img.paste(red, (0,0), red_mask)
#img.show()
img.save(args.outfilename)
