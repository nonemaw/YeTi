import re
from pprint import pprint


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


def format(code: list, message: str = None, entity: str = None) -> list:
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
                line = re.sub(r'^ +', '', line)
                if line.startswith('<:'):
                    if re.search(r'^<: *for', line) or re.search(r'^<: *if',
                                                                   line):
                        if re.search(r'<: *end *:>', line):
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
                    elif re.search(r'^<: *else', line):
                        code[index] = indent(line, level - 1)
                    elif re.search(r'^<: *end', line):
                        level -= 1
                        code[index] = indent(line, level)
                    else:
                        code[index] = indent(line, level)
                else:
                    pass
        else:
            return []

    return code


def format_segment(segment: list) -> list:
    for index, chunk in enumerate(segment):
        indent = ''
        if re.search(r'^ +', chunk):
            indent = re.findall(r'^ +', chunk)[0]

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
                re.search(
                    '(entity|client|partner|trust|superfund|company|partnership)',
                    chunk).span()[0] - 1
            if span >= 0:
                if chunk[span] != '$':
                    chunk = f'{chunk[:span + 1]}${chunk[span + 1:]}'
            else:
                chunk = f'${chunk}'

        if re.search(r'^(let|if|for|end|else)', chunk) or re.search(r'^=',
                                                                      chunk):
            if chunk[-1] == ':':
                segment[index] = f'{indent}{text}<:{chunk}>'
            else:
                segment[index] = f'{indent}{text}<:{chunk}:>'

        elif not re.search(r'(<: *let|^let)', chunk) and re.search(
                '[^\!=]+=[^=]+', chunk):
            segment[index] = f'{indent}{text}<:let {chunk}:>'

        elif not re.search(r'^(let|if|for|end|else)', chunk) and \
                not re.search(r'^=', chunk):
            if len(chunk) > 0 and (chunk[0] == '$' or ' ' not in chunk):
                segment[index] = f'{indent}{text}<:={chunk}:>'

    return [s for s in segment if s]


def cleanup_for_single_entity(code: list) -> list:
    stack = 0
    pop_list = []
    end_list = []
    # text_reserve = {}

    for index, line in enumerate(code):
        # remove comment
        line = re.sub(r' *(#.*):>', ':>', code[index])

        segment = line.split(':>')
        for chunk in segment:
            if stack > 0:
                if 'let' not in chunk:
                    stack += len(
                        re.findall(r' *for.+in *([^\$]+) *| *if +(.+?) *',
                                   chunk))

            entity_loop = len(re.findall(r' *for.+in *(\$\w+) *', chunk))
            if entity_loop:
                if stack <= 0:
                    stack = 0
                    stack += entity_loop
                pop_list.append(index)

            entity_end = len(re.findall(r' *end *', chunk))
            if entity_end:
                stack -= entity_end
                if stack == 0:
                    end_list.append(index)

    for index in reversed(pop_list):
        # remove comment
        line = re.sub(r' *(#.*):>', ':>', code[index])

        if not re.search(r'<: *:>', line):
            entry_log = re.findall(r'<: *for.+in *\$\w+ *:>', line)[0]
            code[index] = re.sub(r'<: *for.+in *\$\w+ *:>',
                                 f'<:#{entry_log[2:-2]}:>',
                                 line)
            if index in end_list:
                code[index] = re.sub(r'<: *end *:>', '<:#end:>', line)
                end_list.remove(index)

    if len(end_list):
        for index in reversed(end_list):
            # remove comment
            line = re.sub(r' *(#.*):>', ':>', code[index])

            if not re.search(r'<: *:>', line):
                code[index] = re.sub(r'<: *end *:>', '<:#end:>', line)

    return [c for c in code if c]


def change_entity(code: list, entity: str) -> list:
    if entity in ['client', 'partner', 'joint']:
        code = cleanup_for_single_entity(code)

        for index, line in enumerate(code):
            # remove comment
            line = re.sub(r' *(#.*):>', ':>', line)

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
                # if entity keyword is in line
                if re.search(r'(trust|superfund|company|partnership)', line):
                    if var_name:
                        line = re.sub(var_name, entity, line)

                    if not var_name:
                        if re.findall(r'<: *for +([\w]+) +in +\$[\w]+', line):
                            var_name = re.findall(r'<: *for +([\w]+) +in +\$[\w]+', line)[0]

                    line = re.sub(r'<: *for +[\w]+ +in +\$[\w]+',
                                  f'<:for {entity} in ${entity}', line)

                    code[index] = re.sub(r'=[\w]+', f'={entity}', line)

                # if $client or $partner is in line
                if re.search(r'(\$client|\$partner\b)', line):
                    if stack < 0:
                        stack = 0
                    if not in_chunk:
                        chunk.append([index])
                        in_chunk = True
                    # if nested loop/condition
                    if re.search(r'<: *(if|for)', line):
                        stack += 1
                        in_chunk = False
                else:
                    if re.search(r'<: *(if|for)', line) and stack >= 0:
                        stack += 1
                    if in_chunk or stack == 0:
                        chunk[-1].append(index)
                        in_chunk = False
                    if re.search(r'<: *end *:>', line) and stack > 0:
                        stack -= 1

        try:
            if len(chunk[-1]) == 1:
                chunk[-1].append(len(code) - 1)

            if len(chunk):
                for c in reversed(chunk):
                    gap_index = c[0]
                    if c[-1] == c[0]:
                        while gap_index <= c[-1]:
                            code[gap_index] = re.sub(r'\$[\w]+', f'{entity}',
                                                     code[gap_index])
                            gap_index += 1
                        code.append('<:end #INSERTION:>')
                        code.insert(c[0],
                                    f'<:for {entity} in ${entity} #INSERTION:>')
                    else:
                        while gap_index < c[-1]:
                            code[gap_index] = re.sub(r'\$[\w]+', f'{entity}',
                                                     code[gap_index])
                            gap_index += 1
                        if c[-1] == len(code) - 1:
                            code.append('<:end #INSERTION:>')
                        else:
                            code.insert(c[-1], '<:end #INSERTION:>')
                        code.insert(c[0],
                                    f'<:for {entity} in ${entity} #INSERTION:>')
        except:
            pass

    else:
        return []

    return code


if __name__ == '__main__':
    code = \
['<:for company in $company #INSERTION:>',
'<:if company.name:>',
'<:if mami:>',
'<:end:>',
'<:end:>',
'<:end #INSERTION:>']

    pprint(change_entity(code, 'partnership'))
