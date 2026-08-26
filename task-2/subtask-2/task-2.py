from PIL import Image

def main():
    image = Image.open("img.jpeg")
    bw_image = image.convert("L")
    bw_image.show()
main()