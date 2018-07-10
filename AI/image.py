from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
from . import face_detect


def merge(inc_image, breed_image, user_id, match_percent):
    BASE = os.path.dirname(os.path.abspath(__file__))
    images = [Image.open(inc_image), Image.open(BASE + '/static/media/' + breed_image + '.jpg')]
    images[0] = ImageOps.expand(images[0], border=16, fill=(255, 255, 255))
    coef = 3  # The lower the bigger the thumbnail will be
    thumb_size = (int((images[0].size[0]) * ((images[1].size[1]/coef)/(images[0].size[1]))),
                  int(images[1].size[1]/coef))
    images[0] = images[0].resize(size=thumb_size, resample=Image.ANTIALIAS)

    widths, heights = zip(*(i.size for i in images))

    total_width = max(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))
    new_im.paste(images[1])
    new_im.paste(images[0], (0, int(max_height/2)))

    draw = ImageDraw.Draw(new_im)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font_size = int(new_im.size[1]/12)
    font = ImageFont.truetype(BASE + "/font.ttf", font_size)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text((0, 0), breed_image.replace('_', ' ') + "\n" + str(match_percent*100)[:4] + "% match", (255, 255, 0), font=font)

    new_path = breed_image + "mergedwithinputfrom" + str(user_id)
    final_path = BASE + '/static/media/' + new_path + '.jpg'
    new_im.save(final_path)
    face_count, new_im = face_detect.face_detect(final_path)
    if face_count:
        new_im.save(final_path)
    return new_path

"""
def merge_sidebyside(inc_image, breed_image, user_id):
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

    new_path = breed_image + "mergedwithinputfrom" + str(user_id)
    final_path = BASE + '/static/media/' + new_path + '.jpg'
    new_im.save(final_path)

    img = Image.open(final_path)
    draw = ImageDraw.Draw(img)
    # font = ImageFont.truetype(<font-file>, <font-size>)
    font = ImageFont.truetype("font.ttf", 16)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text((0, 0), "Sample Text", (255, 255, 255), font=font)
    img.save(final_path)
    face_count, img = face_detect.face_detect(final_path)
    img.save(final_path)

    return new_path
"""