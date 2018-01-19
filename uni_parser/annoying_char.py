annoying_guys = (
    (b'\xe2\x80\x99', "'"),
    (b'\xe2\x80\x90', '-'),
    (b'\xe2\x80\x91', '-'),
    (b'\xe2\x80\x92', '-'),
    (b'\xe2\x80\x93', '-'),
    (b'\xe2\x80\x94', '-'),
    (b'\xe2\x80\x94', '-'),
    (b'\xe2\x80\x98', "'"),
    (b'\xe2\x80\x9b', "'"),
    (b'\xe2\x80\x9c', '"'),
    (b'\xe2\x80\x9c', '"'),
    (b'\xe2\x80\x9d', '"'),
    (b'\xe2\x80\x9e', '"'),
    (b'\xe2\x80\x9f', '"'),
    (b'\xe2\x80\xa4', '.'),
    (b'\xe2\x80\xa5', '..'),
    (b'\xe2\x80\xa6', '...'),
    (b'\xe2\x80\xa7', '-'),
    (b'\xe2\x80\xb2', "'"),
    (b'\xe2\x80\xb3', "'"),
    (b'\xe2\x80\xb4', "'"),
    (b'\xe2\x80\xb5', "'"),
    (b'\xe2\x80\xb6', "'"),
    (b'\xe2\x80\xb7', "'"),
    (b'\xe2\x81\xba', '+'),
    (b'\xe2\x81\xbb', '-'),
    (b'\xe2\x81\xbc', '='),
    (b'\xe2\x81\xbd', '('),
    (b'\xe2\x81\xbe', ')'),
    (b'\xe2\x80\xa2', '-'),
    (b'\xe2\x80\xa3', '-')
)


def annoying_guys_cleaner(char: bytes) -> str:
    for _hex, _char in annoying_guys:
        if char == _hex:
            return _char
