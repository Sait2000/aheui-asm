constatns = {
    0: '바',
    2: '박',
    3: '받',
    4: '밤',
    5: '발',
    6: '밦',
    7: '밝',
    8: '밣',
    9: '밞',
}


nullary_commands = {
    'halt': '하',
    'add': '다',
    'mul': '따',
    'sub': '타',
    'div': '나',
    'mod': '라',
    'pop': '마',
    'popnum': '망',
    'popchar': '맣',
    'pushnum': '방',
    'pushchar': '밯',
    'dup': '빠',
    'swap': '파',
    'cmp': '자',
}


def handle_push(v):
    v = int(v)
    if v in constatns:
        return [constatns[int(v)]]
    # stack을 가정
    # TODO: optimization
    res = []
    while v:
        if v > 9:
            if v % 9:
                res.append('다')
                res.append(constatns.get(v % 9, '바바자'))
            res.append('밞따')
        else:
            res.append(constatns.get(v % 9, '바바자'))
        v //= 9
    return list(''.join(reversed(res)))


def handle_sel(v):
    return [chr(ord('사') + int(v))]


def handle_mov(v):
    return [chr(ord('싸') + int(v))]


def handle_brz(v):
    return [
        '차(;{})'.format(v),
    ]


def handle_brpop2(v):
    return [
        '파(;{})'.format(v),
        '파',
    ]


def handle_brpop1(v):
    return [
        '빠(;{})'.format(v),
        '마',
    ]


def handle_jmp(v):
    return [
        '아({})'.format(v),
    ]


unary_commands = {
    'push': handle_push,
    'sel': handle_sel,
    'mov': handle_mov,
    'brz': handle_brz,
    'brpop2': handle_brpop2,
    'brpop1': handle_brpop1,
    'jmp': handle_jmp,
}


def format_label(s):
    return '[{}]'.format(s)


def aheuis_to_aheuiasm(s):
    pos = 0
    lines = []

    def read_ws(pos):
        while pos < len(s) and s[pos].isspace():
            pos += 1
        return pos

    def read_token(pos):
        oldpos = pos
        while pos < len(s) and not s[pos].isspace() and not s[pos] == ';':
            pos += 1
        return pos, s[oldpos:pos]

    while pos < len(s):
        if s[pos] == ';':
            while pos < len(s) and s[pos] != '\n':
                pos += 1
        elif s[pos].isspace():
            pos = read_ws(pos)
        else:
            pos, token = read_token(pos)
            if token.endswith(':'):
                lines.append(format_label(token[:-1]))
            elif token in nullary_commands:
                    lines.append(nullary_commands[token])
            else:
                pos = read_ws(pos)
                pos, arg = read_token(pos)
                lines.extend(unary_commands[token](arg))

    return ''.join(line + '\n' for line in lines)


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fr:
        src = fr.read().decode('u8')

    res = aheuis_to_aheuiasm(src)

    with open(sys.argv[2], 'wb') as fw:
        fw.write(res.encode('u8'))
