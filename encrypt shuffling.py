import os.path
from PIL import Image   # Uses Pillow, a fork of PIL for Python 3
from random import randrange, seed


def scramble(input_image_filename, key_image_filename=None,
             number_of_regions=16777216):
    input_image_path = os.path.abspath(input_image_filename)
    input_image = Image.open(input_image_path)
    if input_image.size == (1, 1):
        raise ValueError("input image must contain more than 1 pixel")
    number_of_regions = min(int(number_of_regions),
                            number_of_colours(input_image))
    if key_image_filename:
        key_image_path = os.path.abspath(key_image_filename)
        key_image = Image.open(key_image_path)
    else:
        key_image = None
        number_of_regions = 1
    region_lists = create_region_lists(input_image, key_image,
                                       number_of_regions)
    seed(0)
    shuffle(region_lists)
    output_image = swap_pixels(input_image, region_lists)
    save_output_image(output_image, input_image_path)


def number_of_colours(image):
    return len(set(list(image.getdata())))


def create_region_lists(input_image, key_image, number_of_regions):
    template = create_template(input_image, key_image, number_of_regions)
    number_of_regions_created = len(set(template))
    region_lists = [[] for i in range(number_of_regions_created)]
    for i in range(len(template)):
        region = template[i]
        region_lists[region].append(i)
    odd_region_lists = [region_list for region_list in region_lists
                        if len(region_list) % 2]
    for i in range(len(odd_region_lists) - 1):
        odd_region_lists[i].append(odd_region_lists[i + 1].pop())
    return region_lists


def create_template(input_image, key_image, number_of_regions):
    if number_of_regions == 1:
        width, height = input_image.size
        return [0] * (width * height)
    else:
        resized_key_image = key_image.resize(input_image.size, Image.NEAREST)
        pixels = list(resized_key_image.getdata())
        pixel_measures = [measure(pixel) for pixel in pixels]
        distinct_values = list(set(pixel_measures))
        number_of_distinct_values = len(distinct_values)
        number_of_regions_created = min(number_of_regions,
                                        number_of_distinct_values)
        sorted_distinct_values = sorted(distinct_values)
        while True:
            values_per_region = (number_of_distinct_values /
                                 number_of_regions_created)
            value_to_region = {sorted_distinct_values[i]:
                               int(i // values_per_region)
                               for i in range(len(sorted_distinct_values))}
            pixel_regions = [value_to_region[pixel_measure]
                             for pixel_measure in pixel_measures]
            if no_small_pixel_regions(pixel_regions,
                                      number_of_regions_created):
                break
            else:
                number_of_regions_created //= 2
        return pixel_regions


def no_small_pixel_regions(pixel_regions, number_of_regions_created):
    counts = [0 for i in range(number_of_regions_created)]
    for value in pixel_regions:
        counts[value] += 1
    if all(counts[i] >= 256 for i in range(number_of_regions_created)):
        return True


def shuffle(region_lists):
    for region_list in region_lists:
        length = len(region_list)
        for i in range(length):
            j = randrange(length)
            region_list[i], region_list[j] = region_list[j], region_list[i]


def measure(pixel):
    '''Return a single value roughly measuring the brightness.

    Not intended as an accurate measure, simply uses primes to prevent two
    different colours from having the same measure, so that an image with
    different colours of similar brightness will still be divided into
    regions.
    '''
    if type(pixel) is int:
        return pixel
    else:
        r, g, b = pixel[:3]
        return r * 2999 + g * 5869 + b * 1151


def swap_pixels(input_image, region_lists):
    pixels = list(input_image.getdata())
    for region in region_lists:
        for i in range(0, len(region) - 1, 2):
            pixels[region[i]], pixels[region[i+1]] = (pixels[region[i+1]],
                                                      pixels[region[i]])
    scrambled_image = Image.new(input_image.mode, input_image.size)
    scrambled_image.putdata(pixels)
    return scrambled_image


def save_output_image(output_image, full_path):
    head, tail = os.path.split(full_path)
    if tail[:10] == 'scrambled_':
        augmented_tail = 'rescued_' + tail[10:]
    else:
        augmented_tail = 'scrambled_' + tail
    save_filename = os.path.join(head, augmented_tail)
    output_image.save(save_filename)


if __name__ == '__main__':
    import sys
    arguments = sys.argv[1:]
    if arguments:
        scramble(*arguments[:3])
    else:
        print('\n'
              'Arguments:\n'
              '    input image          (required)\n'
              '    key image            (optional, default None)\n'
              '    number of regions    '
              '(optional maximum - will be as high as practical otherwise)\n')