
import os
from common import global_vars
from fuzzier.parser import Fson


def ratio(target:str, pattern:str):
    """ a modified Levenshtein Distance (LD) algorithm
    """
    target = target.lower()
    patter = pattern.lower()
    width = len(target)
    height = len(pattern)
    if width == 0:
        return height
    if height == 0:
        return width

    # initialize the matrix
    d_matrix = [[0 for n in range(width + 1)] for m in range(height + 1)]
    d_matrix_mod = [[0 for n in range(width + 1)] for m in range(height + 1)]
    for i in range(width + 1):
        d_matrix[0][i] = i
    for j in range(height + 1):
        d_matrix[j][0] = j
        d_matrix_mod[j][0] = j

    for i in range(1, width + 1):
        t_char = target[i - 1]
        for j in range(1, height + 1):
            p_char = pattern[j - 1]
            cost = 0 if (p_char == t_char) else 1
            d_matrix[j][i] = min(d_matrix[j - 1][i] + 1,
                                 d_matrix[j][i - 1] + 1,
                                 d_matrix[j - 1][i - 1] + cost)
            d_matrix_mod[j][i] = min(d_matrix_mod[j - 1][i] + 1,
                                     d_matrix_mod[j][i - 1] + 1,
                                     d_matrix_mod[j - 1][i - 1] + cost)

    distance = d_matrix[height][width]
    if distance >= width:
        return 0
    weight = 1 - distance / width
    if 0 in d_matrix_mod[height] and distance != 0:
        # there is a full match to the substring, increase weight based on distance
        weight += distance / width / 3 * 2
    ratio = (1 - distance / width) * weight
    return ratio


def run_fuzzier(pattern):
    global_vars.pattern = pattern
    this_path = os.path.dirname(os.path.realpath(__file__))
    print(os.path.join(this_path, 'json', global_vars.company + '.json'))
    result = []

    with open(os.path.join(this_path, 'json', global_vars.company + '.json')) as F:
        for line in F:
            result = Fson(line, pattern=pattern, ratio_method=ratio, result_length=5).parse()

    print(result)
