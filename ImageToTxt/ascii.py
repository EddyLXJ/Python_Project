from PIL import Image
import argparse

# get cmd
parser = argparse.ArgumentParser()

parser.add_argument('file')
parser.add_argument('--output')
parser.add_argument('--width', type = int, default = 80)
parser.add_argument('--height', type = int, default = 80)

# argument
args = parser.parse_args()

IMG = args.file

WIDTH = args.width

HEIGHT = args.height

OUTPUT = args.output

ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

def get_char(r,g,b, alpha = 256):
	if alpha == 0:
		return ' '

	length = len(ascii_char)

	gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

	unit = (256.0 + 1)/ length

	return ascii_char[int(gray/unit)]

if __name__ == '__main__':
	# open image and adjust width and height
	im = Image.open(IMG)
	im = im.resize((WIDTH, HEIGHT), Image.NEAREST)

	# init the output
	txt = ""

	# for every row in image
	for i in range(HEIGHT):
		# every colum in image
		for j in range(WIDTH):

			txt += get_char(*im.getpixel((j,i)))

		txt += '\n'
	
	print(txt)

	# Write the txt to file
	if OUTPUT:
		with open(OUTPUT, 'w') as f:
			f.write(txt)

	else:
		with open("output.txt", 'w') as f:
			f.write(txt)

