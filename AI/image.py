from PIL import Image
import os


def merge(inc_image, breed_image, user_id):
    BASE = os.path.dirname(os.path.abspath(__file__))
    images = [Image.open(inc_image), Image.open(BASE + '/static/media/' + breed_image + '.jpg')]
    widths, heights = zip(*(i.size for i in images))
    min_height = min(heights)
    for i, s in enumerate(images):
        print("image size before")
        print(images[i].size)
        width, height = images[i].size
        images[i] = images[i].resize((int(width * (min_height/height)), min_height), Image.ANTIALIAS)
        print("image size after")
        print(images[i].size)

    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0

    for im in images:
        print("final image size")
        print(im.size)
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    new_path = breed_image+ "mergedwithinputfrom" + str(user_id)
    new_im.save(BASE + '/static/media/' + new_path + '.jpg')
    return new_path
