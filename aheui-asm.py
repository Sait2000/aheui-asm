from collections import defaultdict

COMMENT = u'#'
LINEEND = u'\r\n'
LABEL_OPEN = u'['
LABEL_CLOSE = u']'
GOTO_START = u'('
GOTO_END = u')'
GOTO_SEP = u';'
GOTO_RELATIVE = u'^'


def is_command_char(c):
    cc = ord(c)
    return 0xAC00 <= cc <= 0xD7A3


def parse(s):
    pos = 0
    commands = []
    labels = {}
    while pos < len(s):
        if s.startswith(COMMENT, pos):
            while pos < len(s) and s[pos] not in LINEEND:
                pos += 1
        elif s[pos] == LABEL_OPEN:
            old_pos = pos
            while pos < len(s) and s[pos] != LABEL_CLOSE:
                pos += 1
            label = u''.join(s[old_pos + 1 : pos].split())
            pos += 1
            labels[label] = len(commands)
        elif is_command_char(s[pos]):
            comm = s[pos]
            pos += 1
            goto = None
            if pos < len(s) and s[pos] == GOTO_START:
                old_pos = pos
                while pos < len(s) and s[pos] != GOTO_END:
                    pos += 1
                goto_s = u''.join(s[old_pos + 1 : pos].split())
                pos += 1
                goto = tuple(goto_s.split(GOTO_SEP) + [u'', u''])[:2]
            commands.append((comm, goto))
        else:
            pos += 1

    def resolve_goto(s):
        s = u''.join(s.split())
        if not s:
            return i + 1
        if s.startswith(GOTO_RELATIVE):
            s = s[len(GOTO_RELATIVE):]
            if not s:
                return i - 1
            else:
                return i + int(s)
        return labels[s]

    for i, (comm, goto) in enumerate(commands):
        if goto is not None:
            goto = tuple(resolve_goto(s) for s in goto)
            commands[i] = comm, goto

    return commands


def rotate_to_down(c):
    cc = ord(c) - 0xAC00
    cc = (cc // 588) * 588 + 13 * 28 + (cc % 28)
    return u'%c' % (cc + 0xAC00)


EMPTY = u'\u3147'
COMM_A = u'\uc544'
COMM_YA = u'\uc57c'
COMM_EO = u'\uc5b4'
COMM_YEO = u'\uc5ec'
COMM_O = u'\uc624'
COMM_YO = u'\uc694'
COMM_U = u'\uc6b0'
COMM_YU = u'\uc720'


def place(commands):
    comm_row = []
    board = []
    for comm, goto in commands:
        comm_row.append(len(board))
        comm = rotate_to_down(comm)
        if goto is not None:
            board.append([COMM_YU])
            board.append([COMM_A])
        board.append([comm])
        if goto is not None:
            board.append([COMM_A])

    lines = defaultdict(list)
    for i, (_comm, goto) in enumerate(commands):
        if goto is None: continue
        lines[comm_row[goto[0]]].append(comm_row[i] + 3)
        lines[comm_row[goto[1]]].append(comm_row[i] + 1)

    line_height = 1
    for stop in sorted(lines, key=lambda k: (-len(lines[k]), k)):
        starts = lines[stop]
        starts.sort()
        for i in range(min(starts[0], stop), max(starts[-1], stop) + 1):
            while len(board[i]) <= line_height:
                board[i].append(EMPTY)

        for i in starts:
            j = 0
            while j < line_height:
                board[i][j] = COMM_YA
                j += 2
            board[i][line_height - 1] = COMM_A
            board[i][line_height] = COMM_U if i < stop else COMM_O

        j = 2
        while j < line_height:
            board[stop][j] = COMM_YEO
            j += 2
        board[stop][line_height] = COMM_EO

        line_height += 2

    for row in board: row.append(u'\n')
    return u''.join(map(u''.join, board))


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as fr:
        src = fr.read().decode('u8')

    commands = parse(src)
    res = place(commands)

    with open(sys.argv[2], 'wb') as fw:
        fw.write(res.encode('u8'))
