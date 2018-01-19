import re


def indent(line: str, level: int) -> str:
    indent = ' ' * (level * 4)
    line = f'{indent}{line}'
    return line


def cleanup_mess(code: list) -> list:
    clean_code = []
    for line in code:
        # if a line is not started with 'for/if/else/end' but contains 'for/if/else/end'
        if not re.search(r'(^\s*<:for|^\s*<:if|^\s*<:else|^\s*<:end)', line.lower()):
            if '<:for' in line.lower() or '<:if' in line.lower() or '<:else' in line.lower() or \
                            '<:end' in line.lower():
                for segment in line.split('<:'):
                    if ':>' in segment:
                        clean_code.append(f'<:{segment}')
                    elif segment:
                        clean_code.append(segment)
            else:
                clean_code.append(line)
        else:
            clean_code.append(line)

    code.clear()
    return clean_code


def format(code: list, message: str = None, entity: str = None) -> list:
    if entity:
        code = change_entity(code, entity)
        return format(code, message='indent')

    else:
        if message == 'format':
            for index, line in enumerate(code):
                segment = line.split(':>')
                code[index] = '\n'.join(format_segment(segment))

            return format(code, message='indent')

        elif message == 'indent':
            level = 0
            for index, line in enumerate(code):
                line = re.sub(r'^ +', '', line)
                # check any line starts with template tag
                if line.startswith('<:'):
                    # this line starts with `for` or `if`
                    if re.search(r'^<: *for', line.lower()) or re.search(r'^<: *if',
                                                                 line.lower()):
                        # this line includes `end`
                        if re.search(r'<: *end *:>', line.lower()):
                            # this line's `for` or `if` is completed
                            if len(re.findall(r'<: *if', line.lower()) + re.findall(
                                    r'<: *for', line.lower())) == len(
                                re.findall(r'<: *end *:>', line.lower())):
                                code[index] = indent(line, level)
                            else:
                                code[index] = indent(line, level)
                                level += 1
                        else:
                            code[index] = indent(line, level)
                            level += 1
                    # this line starts with `else`
                    elif re.search(r'^<: *else', line.lower()):
                        code[index] = indent(line, level - 1)
                    # this line starts with `end`
                    elif re.search(r'^<: *end', line.lower()):
                        level -= 1
                        code[index] = indent(line, level)
                    else:
                        code[index] = indent(line, level)
                else:
                    pass

            return code

        else:
            return []


def format_segment(segment: list) -> list:
    for index, line in enumerate(segment):
        indent = ''
        if re.search(r'^ +', line):
            indent = re.findall(r'^ +', line)[0]

        line = line.strip().split('<:')
        if len(line) > 1:
            text = line[0]
            line = re.sub('^ *= *', '=', line[1])
        else:
            text = ''
            line = re.sub('^ *= *', '=', line[0])

        if 'client.' in line or 'partner.' in line:
            span = re.search('(entity|client|partner)', line).span()[0] - 1
            if span >= 0:
                if line[span] != '$':
                    line = f'{line[:span + 1]}${line[span + 1:]}'
            else:
                line = f'${line}'

        elif 'trust' in line or 'superfund' in line or 'company' in line or\
                        'partnership' in line:
            try:
                span = -1
                if 'for' in line:
                    split = re.search('for +[\w]+ +in', line).span()[1]
                    span = re.search('(trust|superfund|company|partnership)',
                                     line[split:]).span()[0] + split - 1
                elif 'if' in line:
                    if not ('trust.' in line or 'superfund.' in line or
                        'company.' in line or 'partnership.' in line):
                        split = re.search('if +', line).span()[1]
                        span = re.search('(trust|superfund|company|partnership)',
                                  line[split:]).span()[0] + split - 1
            except:
                span = -1

            if span != -1:
                if line[span] != '$' and line[span] != '=':
                    line = f'{line[:span + 1]}${line[span + 1:]}'

        # add template tag to each line
        if re.search(r'^(let|if|for|end|else)', line) or re.search(r'^=',
                                                                   line):
            if line[-1] == ':':
                segment[index] = f'{indent}{text}<:{line}>'
            else:
                segment[index] = f'{indent}{text}<:{line}:>'

        elif not re.search(r'(<: *let|^let)', line) and re.search(
                '[^\!=]+=[^=]+', line):
            segment[index] = f'{indent}{text}<:let {line}:>'

        elif not re.search(r'^(let|if|for|end|else)', line) and \
                not re.search(r'^=', line):
            if len(line) and line[0] != '#' and (line[0] == '$' or ' ' not in line):
                segment[index] = f'{indent}{text}<:={line}:>'
            else:
                if len(segment[index]):
                    segment[index] = f'{indent}{text}<:{line}:>'

    return [s for s in segment if s]


def cleanup_for_single_entity(code: list) -> list:

    for index, c in enumerate(code):
        c = re.sub(r' *(#.*):>', ':>', c)
        if c.strip() == '<::>':
            code[index] = [code[index]]
            continue
        code[index] = c.strip().split(':>')
        code[index] = [f'{_c}:>' for _c in code[index] if _c]

    new_code = []
    for c in code:
        new_code += c
    code.clear()

    stack = []
    pop_list = []
    end_list = []
    # text_reserve = {}

    for index, line in enumerate(new_code):
        # remove comment
        line = re.sub(r' *(#.*):>', ':>', line)
        len_left = len(re.findall('<:', line))
        len_right = len(re.findall(':>', line))

        if len_left != len_right or not len_left or not len_right:
            continue

        if not len(re.findall(r' *end *', line)):
            if 'let' not in line:
                if len(re.findall(r' *for +[\w]+ +in +(.+) *| *if +(.+?) *', line)):
                    stack.append(index)

            if len(re.findall(r' *for +[\w]+ +in +(\$\w+) *', line)):
                pop_list.append(index)

        else:
            # process `end` tag
            if stack and stack.pop() in pop_list:
                end_list.append(index)

    stack.clear()
    for index in reversed(pop_list):
        if not re.search(r'<: *:>', new_code[index]):
            entry_log = re.findall(r'<: *for.+in *\$\w+ *:>', new_code[index])[0]
            new_code[index] = re.sub(r'<: *for.+in *\$\w+ *:>',
                                 f'<:#{entry_log[2:-2]}:>',
                                     new_code[index])
            if index in end_list:
                new_code[index] = re.sub(r'<: *end *:>', '<:#end:>', new_code[index])
                end_list.remove(index)

    if end_list:
        for index in reversed(end_list):
            if not re.search(r'<: *:>', new_code[index]):
                new_code[index] = re.sub(r'<: *end *:>', '<:#end:>', new_code[index])

    return new_code


def change_entity(code: list, entity: str) -> list:
    if entity in ['client', 'partner', 'joint']:
        code = cleanup_for_single_entity(code)

        for index, line in enumerate(code):
            # remove comment
            line = re.sub(r' *(#.*):>', ':>', line)

            if re.search(r'\(\$(trust|superfund|company|partnership)\)', line):
                continue

            if not re.search(r'<: *:>', line):
                if entity in ['client', 'partner']:
                    line = re.sub(r'\$[\w]+', f'${entity}', line)
                    line = re.sub(r'=(trust|superfund|company|partnership)',
                                  f'=${entity}', line)
                    line = re.sub(r'(trust|superfund|company|partnership)\.',
                                  f'${entity}.', line)
                    code[index] = re.sub(r'(CX|PX|JX)',
                                         f'{entity[0].upper()}X', line)

                elif entity == 'joint':
                    line = re.sub(r'\$[\w]+', '$client', line)
                    line = re.sub(r'=(trust|superfund|company|partnership)',
                                  '=$client', line)
                    line = re.sub(r'(trust|superfund|company|partnership)\.',
                                  f'$client.', line)
                    code[index] = re.sub(r'(CX|PX)', 'JX', line)

    elif entity in ['trust', 'superfund', 'company', 'partnership']:
        in_chunk = False
        stack = -1
        chunk = []
        var_name = ''

        for index, line in enumerate(code):
            # remove comment
            line = re.sub(r' *(#.*):>', ':>', line)

            if not re.search(r'<: *:>', line):

                # if other entity keywords is in line
                if re.search(r'(trust|superfund|company|partnership)', line):
                    if var_name:
                        line = re.sub(var_name, entity, line)

                    if not var_name:
                        if re.findall(r'<: *for +([\w]+) +in +\$[\w]+', line):
                            var_name = \
                                re.findall(r'<: *for +([\w]+) +in +\$[\w]+',
                                           line)[0]

                    line = re.sub(r'(trust|superfund|company|partnership)', entity, line)
                    line = re.sub(r'<: *for +[\w]+ +in +\$[\w]+',
                                  f'<:for {entity} in ${entity}', line)

                    code[index] = re.sub(r'=[\w]+', f'={entity}', line)

                # if `$client` or `$partner` in line with `if` or `for`
                if re.search(r'(\$client|\$partner\b)', line) and re.search(
                        r'<: *(if|for)', line):
                    in_chunk = True
                    if stack < 0:
                        stack = 1
                        chunk.append([index])
                    else:
                        stack += 1

                # if `$client` or `$partner` in line
                elif re.search(r'(\$client|\$partner\b)', line):
                    if not in_chunk:
                        chunk.append([index])

                # a normal `if` or `for` without `$client` or `$partner`
                elif re.search(r'<: *(if|for)', line) and in_chunk:
                    stack += 1

                # `end` tag
                elif re.search(r'<: *end *:>', line):
                    stack -= 1
                    if stack == 0:
                        stack = -1
                        chunk[-1].append(index)

        # merge code chunk, e.g.
        # [[0], [1, 3], [4, 6], [9, 10]] => [[0, 6], [9, 10]]
        merged_chunk = []
        item = []
        for index, c in enumerate(chunk):
            if index < len(chunk) - 1 and c[-1] + 1 == chunk[index + 1][0]:
                if item:
                    item[-1] = chunk[index + 1][-1]
                else:
                    item = [c[0], chunk[index + 1][-1]]
            else:
                if item:
                    merged_chunk.append(item)
                    item = []
                else:
                    merged_chunk.append(c)
        chunk.clear()

        try:
            if len(merged_chunk[-1]) == 1:
                merged_chunk[-1].append(len(code) - 1)

            if len(merged_chunk):
                for c in reversed(merged_chunk):
                    gap_index = c[-1]
                    if c[0] == c[-1]:
                        while gap_index >= c[0]:
                            code[gap_index] = re.sub(r'\$[\w]+', f'{entity}',
                                                     code[gap_index])
                            gap_index -= 1
                        code.append('<:end #INSERTION:>')
                        code.insert(c[0],
                                    f'<:for {entity} in ${entity} #INSERTION:>')

                    else:
                        while gap_index >= c[0]:
                            if not re.findall('<: *for +[\w]+ +in +\$[\w]+', code[gap_index]):
                                code[gap_index] = re.sub(r'\$[\w]+', f'{entity}',
                                                         code[gap_index])

                            gap_index -= 1
                        if c[-1] == len(code) - 1:
                            code.append('<:end #INSERTION:>')
                        else:
                            code.insert(c[-1] + 1, '<:end #INSERTION:>')
                        code.insert(c[0],
                                    f'<:for {entity} in ${entity} #INSERTION:>')
        except:
            pass

    else:
        return []

    return code


if __name__ == '__main__':
    code = """<:IF SHOWC:>
AAA
<:END:>
<:IF $PARTNER:>
    <:IF SHOWP:>
BBB
    <:END:>
    <:IF SHOWJ:>
CCC
    <:END:>
<:END:>
<:IF COMPANY:>
DDD
    <:IF SUPERFUND:>
        <:FOR SUPERFUND IN $SUPERFUND:>
EEE
        <:END:>
    <:END:>
    <:IF TRUST:>
        <:FOR TRUST IN $TRUST:>
DDD
        <:END:>
    <:END:>
    <:IF COMPANY:>
        <:FOR COMPANY IN $COMPANY:>
EEE
        <:END:>
    <:END:>
<:END:>"""

    code = code.split('\n')

    from pprint import pprint
    pprint(format(code, 'indent'))
