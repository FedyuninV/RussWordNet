import sys


POS = ['noun', 'verb', 'adv', 'adj']


def data_file_name(pos):
    return 'data.' + pos


def index_file_name(pos):
    return 'index.' + pos


def build_offset_map(pos):
    print('getting data from ' + data_file_name(pos) + '...')
    offset_map = {}
    lines = open(data_file_name(pos), 'r').readlines()
    tot_len = 0
    for line in lines:
        tokens = line.split()
        if len(tokens[0]) == 8:
            offset_map[int(tokens[0])] = tot_len
        tot_len += len(line.encode('utf-8'))
    return offset_map


class LineTokenizer:
    def __init__(self, text):
        self.tokens = text.split()
        self.text = text
        self.coord = 0
        self.token_index = -1

    def next_token(self):
        self.token_index += 1
        self.coord = self.text.find(self.tokens[self.token_index], self.coord)
        return self.tokens[self.token_index]

    def replace_curr_token(self, new_text):
        self.text = self.text[:self.coord] + new_text + self.text[self.coord + len(self.tokens[self.token_index]):]
        return None

    def get_text(self):
        return self.text


def get_int(text):
    return int('0x'+text, 16)

def fix_data_offsets(pos, offset_map):
    print('fixing offsets in ' + data_file_name(pos) + '...')
    lines = open(data_file_name(pos), 'r').readlines()
    for i in range(len(lines)):
        t = LineTokenizer(lines[i])
        def get_pos(x):
            if x == 'n':
                return 'noun'
            if x == 'v':
                return 'verb'
            if x == 'r':
                return 'adv'
            if x == 'a':
                return 'adj'
        
        old_offset = int(t.next_token())
        t.replace_curr_token(str(offset_map[pos][old_offset]).zfill(8))
        # some number
        _ = t.next_token()
        # pos tag
        _ = t.next_token()
        # count and [word, num] * count
        word_count = get_int(t.next_token())
        for j in range(word_count):
            _ = t.next_token()
            _ = t.next_token()
        word_count = int(t.next_token())
        for j in range(word_count):
            _ = t.next_token()
            old_offset = int(t.next_token())
            word_pos = get_pos(lines[i][t.coord + 9])
            t.replace_curr_token(str(offset_map[word_pos][old_offset]).zfill(8))
            _ = t.next_token()
            _ = t.next_token()
        lines[i] = t.get_text()
    open(data_file_name(pos), 'w').write(''.join(lines))


def fix_index_offsets(pos, offset_map):
    print('fixing offsets in ' + index_file_name(pos) + '...')
    lines = open(index_file_name(pos), 'r').readlines()
    for i in range(len(lines)):
        tokens = lines[i].split()
        for j in reversed(range(len(tokens))):
            if not len(tokens[j]) == 8:
                break
            offset = int(tokens[j])
            tokens[j] = str(offset_map[offset]).zfill(8)
        lines[i] = ' '.join(tokens) + '\n'
    open(index_file_name(pos), 'w').write(''.join(lines))


def main():
    print('getting data...')
    offset_map = {}
    for pos in POS:
        offset_map[pos] = build_offset_map(pos)
    print('getting data finished!')
    print('')

    print('fixing offsets in index files...')
    for pos in POS:
        fix_index_offsets(pos, offset_map[pos])
    print('fixing offsets in index files finished!')
    print('')

    print('fixing offsets in data files...')
    for pos in POS:
        fix_data_offsets(pos, offset_map)
    print('fixing offsets in data files finished!')

if __name__ == '__main__':
    main()
