from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from .object_detection_api import get_objects
import json
import textwrap
import math
from django.utils import timezone
from AI.find_translation import find_translation


def draw_arc(draw, center, radius, start, end, fill, width):
    arc_start = start
    arc_end = end
    sides = 360
    step = 360 / sides
    previous_point = (center[0], center[1] - radius)
    points = [previous_point]
    while arc_start < arc_end:
        heading = arc_start * 3.1415926535897932384626433832795 / 180
        next_point = (
            (previous_point[0] + math.cos(heading) * radius),
            (previous_point[1] + math.sin(heading) * radius)
        )
        previous_point = next_point
        arc_start += step
        points.append(previous_point)
    draw.line(points, fill=fill, width=width)


def merge(inc_image, breed_image, user_id, match_percent, localize=False):
    # base path for all static files
    base = os.path.dirname(os.path.abspath(__file__))

    # opening incoming image and breed representing image
    images = [Image.open(inc_image), Image.open(base + '/static/media/' + breed_image + '.jpg')]
    template = Image.open(base + "/template.png")

    # sizes of images and their location
    template_size = (654, 1105)
    breed_image_size = (575, 580)
    breed_image_paste_position = (40, 100)
    inc_image_size = (180, 170)
    inc_image_paste_position = (40, 873)

    template = template.resize(size=template_size, resample=Image.ANTIALIAS)

    # fitting images into their places in the template
    images[1] = ImageOps.fit(images[1], breed_image_size, Image.ANTIALIAS)
    images[0] = ImageOps.fit(images[0], inc_image_size, Image.ANTIALIAS)

    # forming a new image and pasting everything into the picture
    new_im = Image.new('RGBA', template_size)
    new_im.paste(images[1], breed_image_paste_position)
    new_im.paste(images[0], inc_image_paste_position)
    new_im = Image.alpha_composite(new_im, template)

    # hardcoded design for fonts and other graphics
    draw = ImageDraw.Draw(new_im)

    font_file_bold = base + "/font_bold.ttf"
    font_file_regular = base + "/font_regular.ttf"

    match_font_size = int(new_im.size[0] / 20)
    match_font = ImageFont.truetype(font_file_bold, match_font_size)

    breed_name_font_size = int(new_im.size[0] / 12)
    breed_name_font = ImageFont.truetype(font_file_bold, breed_name_font_size)

    description_font_size = int(new_im.size[0] / 25)
    description_font = ImageFont.truetype(font_file_regular, description_font_size)

    if localize:
        breed_name = find_translation((breed_image.replace('_', ' '))).capitalize()
    else:
        breed_name = (breed_image.replace('_', ' ')).capitalize()

    breed_name_location = (40, 720)
    breed_name_color = (0, 0, 0)

    match_percent_display = str(match_percent * 100)[:2 + int((match_percent * 100) // 100)] + "%"
    match_percent_display_location = (512 - int((match_percent * 100) // 100) * match_font_size / 4, 953)
    match_percent_display_color = (0, 0, 0)
    match_percent_arc_color = (226, 106, 88)
    match_percent_arc_radius = 0.8
    match_percent_arc_width = 4
    match_percent_arc_end = int(360 * match_percent)
    match_percent_arc_center = (
        match_percent_display_location[0] + 32 + int((match_percent * 100) // 100) * match_font_size / 3,
        match_percent_display_location[1] - 25
    )

    description_line_length = 20
    description = textwrap.fill("Lovable, affectionate, gets along easily.", width=description_line_length)
    description_location = (235, 915)
    description_color = (178, 178, 178)

    draw.text(match_percent_display_location, match_percent_display, match_percent_display_color,
              font=match_font)
    draw.text(breed_name_location, breed_name, breed_name_color,
              font=breed_name_font)
    draw.text(description_location, description, description_color,
              font=description_font)
    draw_arc(
        draw=draw,
        center=match_percent_arc_center, radius=match_percent_arc_radius,
        start=0, end=match_percent_arc_end,
        fill=match_percent_arc_color, width=match_percent_arc_width
    )

    # converting to jpg
    new_im = new_im.convert("RGB")

    # saving everything and returning a file name
    timecode = str(timezone.now()).replace(':', '-').replace('+', '-').replace('.', '-').replace(' ', '_')
    new_path = breed_image + timecode + str(user_id)
    final_path = base + '/static/media/' + new_path + '.jpg'
    new_im.save(final_path)
    from . import memory
    memory.print_memory_usage()
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
