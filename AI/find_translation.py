import os


def find_translation(breed_name):
    base = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base, "russian_breeds.txt")
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            if line[:len(breed_name)] == breed_name:
                return line[len(breed_name)+1:-1] 

    return breed_name