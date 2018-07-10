from PIL import Image, ImageDraw
import face_recognition


# draws a rectangle of a specified width and color
def draw_rectangle(draw, right, left, top, bottom, line_width, line_color):
    draw.line(((left, top), (right, top)), fill=line_color, width=line_width)
    draw.line(((right, top), (right, bottom)), fill=line_color, width=line_width)
    draw.line(((right, bottom), (left, bottom)), fill=line_color, width=line_width)
    draw.line(((left, bottom), (left, top)), fill=line_color, width=line_width)


# returns how many faces the algorithm found and the image with drawn rectangles
def face_detect(image_file, line_width=15, line_color="black", line_color_secondary="white", line_width_secondary=2):
    image = face_recognition.load_image_file(image_file)
    pil_image = Image.open(image_file)
    face_locations = face_recognition.face_locations(image)

    draw = ImageDraw.Draw(pil_image)

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    for face_location in face_locations:

        top, right, bottom, left = face_location

        draw_rectangle(draw, right, left, top, bottom, line_width, line_color)
        draw_rectangle(draw, right, left, top, bottom, line_width_secondary, line_color_secondary)

    return len(face_locations), pil_image
