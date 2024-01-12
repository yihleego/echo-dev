import os.path

from PIL import Image


def rename(src, append):
    directory, filename = os.path.split(src)
    basename, extension = os.path.splitext(filename)
    return f"{basename}_{append}{extension}"


def resize(src, dst, ratio):
    if not os.path.exists(src):
        return
    if os.path.exists(dst):
        return
    image = Image.open(src)
    new_size = (int(image.width * ratio), int(image.height * ratio))
    resized_image = image.resize(new_size)
    resized_image.save(dst)


def larger(src):
    dst = rename(src, "large")
    resize(src, dst, 2)


def smaller(src):
    dst = rename(src, "small")
    resize(src, dst, 0.5)


if __name__ == "__main__":
    images = [
        "sample_pypi_part_copy.png",
        "sample_pypi_part_logo.png",
        "sample_pypi_part_title.png",
        "sample_pypi_part_version.png",
    ]
    for i in images:
        larger(i)
        smaller(i)
