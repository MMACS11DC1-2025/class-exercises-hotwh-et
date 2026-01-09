from PIL import Image, ImageFile

def binarize(image: ImageFile.ImageFile, threshold: int = 128):
	greyscale_image = image.convert("L")
	binarized_image = greyscale_image.copy()

	for x in range(greyscale_image.width):
		for y in range(greyscale_image.height):
			if greyscale_image.getpixel((x, y)) > 128: # type: ignore
				binarized_image.putpixel((x, y), 255)
			else:
				binarized_image.putpixel((x, y), 0)

	return binarized_image

def greyscale(image: ImageFile.ImageFile, threshold: int = 128):
	greyscale_image = image.convert("L")

	return greyscale_image