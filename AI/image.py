from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
from .object_detection_api import get_objects
import json


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
    font_size = int(new_im.size[1]/12)
    font = ImageFont.truetype(BASE + "/font.ttf", font_size)
    draw.text((0, 0), breed_image.replace('_', ' ') + "\n" + str(match_percent*100)[:4] + "% match", (255, 255, 0), font=font)

    new_path = breed_image + "mergedwithinputfrom" + str(user_id)
    final_path = BASE + '/static/media/' + new_path + '.jpg'
    new_im.save(final_path)
    # face_count, new_im = face_detect.face_detect(final_path)
    # if face_count:
    #    new_im.save(final_path)
    return new_path


def crop(image_file):
    img = Image.open(image_file)
    get_objects_result = json.loads(get_objects(img))
    object_type = 'none'
    crop_x, crop_y, crop_width, crop_height = (0, 0, 0, 0)
    for i in get_objects_result:
        if "class_name" in i:
            if i["class_name"] == 'dog':
                object_type = 'dog'
                crop_x, crop_y, crop_width, crop_height = (i["x"], i["y"], i["width"], i["height"])
                break
            elif i["class_name"] == 'person':
                object_type = 'human'
                crop_x, crop_y, crop_width, crop_height = (i["x"], i["y"], i["width"], i["height"])
    if object_type != 'none':
        orig_width, orig_height = img.size
        left_corner = (crop_x * orig_width, crop_y * orig_height)
        right_corner = (crop_width * orig_width, crop_height * orig_height)
        box = (left_corner[0], left_corner[1], right_corner[0], right_corner[1])
        img = img.crop(box=box)
        print(box)
        img.save(image_file)
        return True
    return False
