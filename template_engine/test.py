import re

def handle_iter_to_list(stmt: str):
    """
    convert map, reduce, filter to list, for a compatibility with
    Python2.*'s operation, e.g. filter(func, iter)[0]

    e.g.

    map(func, filter(lambda x: str(x) in '0123456789', [1,2,3,4,5,99]))
    to
    list(map(func, list(filter(lambda x: str(x) in '0123456789', [1,2,3,4,5,99]))))
    """
    search = re.search(r"[^a-zA-Z]*(map|reduce|filter)[^a-zA-Z]", stmt)
    if search:
        start = search.start(1)
        end = search.end(1)
        func = search.group(1)

        # find the position of closed brackets
        temp = stmt[end:]
        stack = 0
        str_stack = []
        closed_position = 0
        for index, c in enumerate(temp):
            if (c == '(' or c == '{' or c == '[') and not str_stack:
                stack += 1

            if (c == ')' or c == '}' or c == ']') and not str_stack:
                stack -= 1

            if c == "'" or c == '"':
                if str_stack and str_stack[-1] == c:
                    str_stack.pop()
                else:
                    str_stack.append(c)

            if not stack:
                closed_position = index + 1 + end
                break

        return f'{stmt[:start]}list({func}{handle_iter_to_list(stmt[end:closed_position])}){handle_iter_to_list(stmt[closed_position:])}'
    else:
        return stmt

stmt = "float(map(lambda x: x.startswith('(') and ('-'+x[1:]) or x, filter(lambda x: x in '0123456789.(', $client.sample_method(['1', '2', '3', '4', '5'])))[0])"
#stmt = "map(func, filter(lambda x: str(x) in '0123456789(', [1,2,3,4,5,99]))"
#stmt = "map('012(', hhh)"
print(handle_iter_to_list(stmt))


