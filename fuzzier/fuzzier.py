

"""
Levenshtein distance (LD) algorithm is used for calculating similarity between
searched pattern and target string
"""

from common import global_vars

class LDRatio:
    def ratio(self, target:str, pattern:str):
        width = len(target)
        height = len(pattern)
        if width == 0:
            return height
        if height == 0:
            return width

        # initialize the matrix
        d_matrix = [[0 for n in range(width + 1)] for m in range(height + 1)]
        # first row set to all `0` for fuzzy substring match
        # for i in range(width + 1):
        #     d_matrix[0][i] = i
        for j in range(height + 1):
            d_matrix[j][0] = j

        for i in range(1, width + 1):
            t_char = target[i - 1]
            for j in range(1, height + 1):
                p_char = pattern[j - 1]
                cost = 0 if (p_char == t_char) else 1
                d_matrix[j][i] = min(d_matrix[j - 1][i] + 1, d_matrix[j][i - 1] + 1, d_matrix[j - 1][i - 1] + cost)
        distance = d_matrix[height][width]
        if distance >= width:
            return 0

        weight = 1 - distance / width
        if 0 in d_matrix[height]:
            # there is a full match to the substring, increase weight based on substring length
            weight = max(height, distance) / width

        ratio = (1 - distance / width) * weight
        return ratio