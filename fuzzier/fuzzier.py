import re
from fuzzier.jison import Jison


def ratio(target: str, pattern: str):
    """ a modified Levenshtein Distance (LD) algorithm
    """
    target_l = re.sub(r'\s|_', '', target.lower())
    pattern_l = re.sub(r'\s|_', '', pattern.lower())
    width = len(target_l)
    height = len(pattern_l)
    if width == 0:
        return height
    if height == 0:
        return width

    # initialize the matrix
    # d_matrix for calculating Levenshtein Distance
    # d_matrix_mod for detecting a full substring match, increase ratio when a full substring match
    d_matrix = [[0 for n in range(width + 1)] for m in range(height + 1)]
    d_matrix_mod = [[0 for n in range(width + 1)] for m in range(height + 1)]

    for i in range(width + 1):
        d_matrix[0][i] = i

    for j in range(height + 1):
        d_matrix[j][0] = j
        d_matrix_mod[j][0] = j

    for i in range(1, width + 1):
        t_char = target_l[i - 1]

        for j in range(1, height + 1):
            p_char = pattern_l[j - 1]
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
        # there is a full match to the substring, increase weight largely based on distance
        weight += distance / width / 3 * 2

    if 1 in d_matrix_mod[height] and distance != 1:
        # there is nearly a full match to the substring, increase weight moderately based on distance
        weight += distance / width / 3

    return (1 - distance / width) * weight


def search(jison: Jison, pattern: str, count: int = 8) -> list:
    if hasattr(jison, 'json') and jison.json:
        return jison.search(pattern=pattern, ratio_method=ratio, count=count)
    else:
        return []

