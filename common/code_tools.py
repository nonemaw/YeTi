import re


def indent(line: str, level: int) -> str:
    for i in range(level):
        line = '    ' + line
    return line


def cleanup_mess(code: list) -> list:
    clean_code = []
    for line in code:
        # if a line is not started with 'for/if/else/end' but contains 'for/if/else/end'
        if not re.search(r'(^\s*<:for|^\s*<:if|^\s*<:else|^\s*<:end)', line):
            if '<:for' in line or '<:if' in line or '<:else' in line or \
                            '<:end' in line:
                for segment in line.split('<:'):
                    if ':>' in segment:
                        clean_code.append(f'<:{segment}')
                    elif segment:
                        clean_code.append(segment)
            else:
                clean_code.append(line)
        else:
            clean_code.append(line)

    return clean_code


def format(code: list, message: str=None, entity: str=None) -> list:
    if entity:
        code = change_entity(code, entity)
    else:

        if message == 'format':
            for index, line in enumerate(code):
                segment = line.split(':>')
                code[index] = '\n'.join(format_segment(segment))

        elif message == 'indent':
            level = 0
            for index, line in enumerate(code):
                line = re.sub('^ +', '', line)
                if line.startswith('<:'):
                    if re.findall('^<: *for', line) or re.findall('^<: *if', line):
                        if re.findall('<: *end *:>', line):
                            if len(re.findall(r'<:if', line) + re.findall(
                                    r'<: *for', line)) == len(
                                re.findall(r'<: *end *:>', line)):
                                code[index] = indent(line, level)
                            else:
                                code[index] = indent(line, level)
                                level += 1
                        else:
                            code[index] = indent(line, level)
                            level += 1
                    elif re.findall('^<: *else', line):
                        code[index] = indent(line, level - 1)
                    elif re.findall('^<: *end', line):
                        level -= 1
                        code[index] = indent(line, level)
                    else:
                        code[index] = indent(line, level)
                else:
                    pass
    return code


def format_segment(segment: list) -> list:
    for index, chunk in enumerate(segment):
        indent = ''
        if re.findall('^ +', chunk):
            indent = re.findall('^ +', chunk)[0]

        chunk = chunk.strip().split('<:')
        if len(chunk) > 1:
            text = chunk[0]
            chunk = chunk[1]
        else:
            text = ''
            chunk = chunk[0]

        if 'client.' in chunk or 'partner.' in chunk or \
                        'trust' in chunk or 'superfund' in chunk or \
                        'company' in chunk or 'partnership' in chunk:
            span = \
            re.search('(client|partner|trust|superfund|company|partnership)',
                      chunk).span()[0] - 1
            if span >= 0:
                if chunk[span] != '$':
                    chunk =  f'{chunk[:span + 1]}${chunk[span + 1:]}'
            else:
                chunk = f'${chunk}'

        if not re.findall('(<: *let|^let)', chunk) and re.findall('[^!=]+=[^=]+', chunk):
            segment[index] = f'{indent}{text}<:let {chunk}:>'

        elif re.findall('^(let|if|for|end|else)', chunk) or re.findall('^=',
                                                                       chunk):
            if chunk.endswith(':'):
                segment[index] = f'{indent}{text}<:{chunk}>'
            else:
                segment[index] = f'{indent}{text}<:{chunk}:>'

        elif not re.findall('^(let|if|for|end|else)', chunk) and \
                not re.findall('^=', chunk):
            if len(chunk) > 0 and (chunk[0]  =='$' or ' ' not in chunk):
                segment[index] = f'{indent}{text}<:={chunk}:>'

    return [s for s in segment if s]


def cleanup_for_single_entity(code: list) -> list:
    stack = 0
    pop_list = []
    end_list = []
    #text_reserve = {}

    for index, line in enumerate(code):
        segment = line.split(':>')
        for chunk in segment:
            if stack > 0:
                if 'let' not in chunk:
                    stack += len(re.findall(' *for.+in *([^\$]+) *| *if +(.+?) *', chunk))

            entity_loop = len(re.findall(' *for.+in *(\$\w+) *', chunk))
            if entity_loop:
                if stack <= 0:
                    stack = 0
                    stack += entity_loop
                pop_list.append(index)

            entity_end = len(re.findall(' *end *', chunk))
            if entity_end:
                stack -= entity_end
                if stack == 0:
                    end_list.append(index)

    for index in reversed(pop_list):
        code[index] = re.sub('<: *for.+in *\$\w+ *:>', '', code[index])
        if index in end_list:
            code[index] = re.sub('<: *end *:>', '', code[index])
            end_list.remove(index)

    if len(end_list):
        for index in reversed(end_list):
            code[index] = re.sub('<: *end *:>', '', code[index])

    return [c for c in code if c]


def change_entity(code: list, entity: str) -> list:
    if entity in ['client', 'partner']:
        code = cleanup_for_single_entity(code)

        for index, line in enumerate(code):
            line = re.sub('\$[\w]+', f'${entity}', line)
            code[index] = re.sub('(CX|PX)', f'{entity[0].upper()}X', line)

    elif entity == 'joint':
        code = cleanup_for_single_entity(code)

        for index, line in enumerate(code):
            line = re.sub('\$[\w]+', '$client', line)
            code[index] = re.sub('(CX|PX)', f'JX', line)

    elif entity in ['trust', 'superfund', 'company', 'partnership']:
        pass



    return code
