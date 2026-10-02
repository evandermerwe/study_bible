# Copyright (c) 2026 Eric van der Merwe
# SPDX-License-Identifier: MIT

# Convert the Project Gutenberg King James Version into OpBible .txs files.
#
# The biblical text is the public-domain Authorized Version. Project Gutenberg
# ebooks 8001 through 8066 are books 1 through 66 (Genesis through Revelation),
# the same edition already used for KJV-Luke.txs and KJV-Rev.txs.
#
# One .txs file is written per book, named KJV-<mark>.txs, where <mark> is the
# book mark from books.tex. main.tex loads them as bible_text/\tmark-\amark.txs.
# Each line is one verse: #chapter:verse text
# Psalm superscriptions are prefixed to verse 1, and formats/fmt-KJV-Ps.tex
# sets those superscriptions in italic.
#
# Usage:
#   python3 convert_to_txs.py --pg-dir /path/to/pg-texts
#   python3 convert_to_txs.py luke_kjv.txt KJV-Luke.txs
#
# --pg-dir must contain 8001.txt ... 8066.txt (the UTF-8 PG ebook texts).

import re
import sys
from pathlib import Path

VERSE_RE = re.compile(r'^(\d+):(\d+):(\d+)\s+(.*)$')
END_MARK = '*** END OF THE PROJECT GUTENBERG EBOOK'
TEX_SPECIAL_RE = re.compile(r'[\\$&_^%{}~#<>]')

# mark, title, chapters, verses. Order is the Protestant canon.
BOOKS = [
    ('Gen', 'Genesis', 50, 1533),
    ('Exod', 'Exodus', 40, 1213),
    ('Lev', 'Leviticus', 27, 859),
    ('Num', 'Numbers', 36, 1288),
    ('Deut', 'Deuteronomy', 34, 959),
    ('Josh', 'Joshua', 24, 658),
    ('Judg', 'Judges', 21, 618),
    ('Ruth', 'Ruth', 4, 85),
    ('1Sam', 'I Samuel', 31, 810),
    ('2Sam', 'II Samuel', 24, 695),
    ('1Kgs', 'I Kings', 22, 816),
    ('2Kgs', 'II Kings', 25, 719),
    ('1Chr', 'I Chronicles', 29, 942),
    ('2Chr', 'II Chronicles', 36, 822),
    ('Ezra', 'Ezra', 10, 280),
    ('Neh', 'Nehemiah', 13, 406),
    ('Esth', 'Esther', 10, 167),
    ('Job', 'Job', 42, 1070),
    ('Ps', 'Psalms', 150, 2461),
    ('Prov', 'Proverbs', 31, 915),
    ('Eccl', 'Ecclesiastes', 12, 222),
    ('Song', 'Song of Solomon', 8, 117),
    ('Isa', 'Isaiah', 66, 1292),
    ('Jer', 'Jeremiah', 52, 1364),
    ('Lam', 'Lamentations', 5, 154),
    ('Ezek', 'Ezekiel', 48, 1273),
    ('Dan', 'Daniel', 12, 357),
    ('Hos', 'Hosea', 14, 197),
    ('Joel', 'Joel', 3, 73),
    ('Amos', 'Amos', 9, 146),
    ('Obad', 'Obadiah', 1, 21),
    ('Jonah', 'Jonah', 4, 48),
    ('Mic', 'Micah', 7, 105),
    ('Nah', 'Nahum', 3, 47),
    ('Hab', 'Habakkuk', 3, 56),
    ('Zeph', 'Zephaniah', 3, 53),
    ('Hag', 'Haggai', 2, 38),
    ('Zech', 'Zechariah', 14, 211),
    ('Mal', 'Malachi', 4, 55),
    ('Matt', 'Matthew', 28, 1071),
    ('Mark', 'Mark', 16, 678),
    ('Luke', 'Luke', 24, 1151),
    ('John', 'John', 21, 879),
    ('Acts', 'Acts', 28, 1007),
    ('Rom', 'Romans', 16, 433),
    ('1Cor', 'I Corinthians', 16, 437),
    ('2Cor', 'II Corinthians', 13, 257),
    ('Gal', 'Galatians', 6, 149),
    ('Eph', 'Ephesians', 6, 155),
    ('Phil', 'Philippians', 4, 104),
    ('Col', 'Colossians', 4, 95),
    ('1Thess', 'I Thessalonians', 5, 89),
    ('2Thess', 'II Thessalonians', 3, 47),
    ('1Tim', 'I Timothy', 6, 113),
    ('2Tim', 'II Timothy', 4, 83),
    ('Titus', 'Titus', 3, 46),
    ('Phlm', 'Philemon', 1, 25),
    ('Heb', 'Hebrews', 13, 303),
    ('Jas', 'James', 5, 108),
    ('1Pet', 'I Peter', 5, 105),
    ('2Pet', 'II Peter', 3, 61),
    ('1John', 'I John', 5, 105),
    ('2John', 'II John', 1, 13),
    ('3John', 'III John', 1, 14),
    ('Jude', 'Jude', 1, 25),
    ('Rev', 'Revelation', 22, 404),
]

# Gutenberg prints a handful of ordinary verses in capitals (a heading style,
# not the small-caps of the Authorized Version). These are restored to the
# sentence case used everywhere else. LORD stays in capitals: that is the
# KJV distinction for the divine name. Inscriptions that the KJV itself prints
# in capitals (HOLINESS TO THE LORD, MENE TEKEL, and so on) are left alone.
SHOUTING_VERSES = {
    (19, 70, 1),
    (19, 92, 1),
}

# Unnumbered King James superscriptions. Gutenberg's numbered text omits
# them; they are prefixed to verse 1 of the psalm. Italics are applied in
# formats/fmt-KJV-Ps.tex, which is how the Authorized Version prints them.
PSALM_SUPERSCRIPTION = {
    3: 'A Psalm of David, when he fled from Absalom his son.',
    4: 'To the chief Musician on Neginoth, A Psalm of David.',
    5: 'To the chief Musician upon Nehiloth, A Psalm of David.',
    6: 'To the chief Musician on Neginoth upon Sheminith, A Psalm of David.',
    7: 'Shiggaion of David, which he sang unto the LORD, concerning the words of Cush the Benjamite.',
    8: 'To the chief Musician upon Gittith, A Psalm of David.',
    9: 'To the chief Musician upon Muthlabben, A Psalm of David.',
    11: 'To the chief Musician, A Psalm of David.',
    12: 'To the chief Musician upon Sheminith, A Psalm of David.',
    13: 'To the chief Musician, A Psalm of David.',
    14: 'To the chief Musician, A Psalm of David.',
    15: 'A Psalm of David.',
    16: 'Michtam of David.',
    17: 'A Prayer of David.',
    18: 'To the chief Musician, A Psalm of David, the servant of the LORD, who spake unto the LORD the words of this song in the day that the LORD delivered him from the hand of all his enemies, and from the hand of Saul: And he said,',
    19: 'To the chief Musician, A Psalm of David.',
    20: 'To the chief Musician, A Psalm of David.',
    21: 'To the chief Musician, A Psalm of David.',
    22: 'To the chief Musician upon Aijeleth Shahar, A Psalm of David.',
    23: 'A Psalm of David.',
    24: 'A Psalm of David.',
    25: 'A Psalm of David.',
    26: 'A Psalm of David.',
    27: 'A Psalm of David.',
    28: 'A Psalm of David.',
    29: 'A Psalm of David.',
    30: 'A Psalm and Song at the dedication of the house of David.',
    31: 'To the chief Musician, A Psalm of David.',
    32: 'A Psalm of David, Maschil.',
    34: 'A Psalm of David, when he changed his behaviour before Abimelech; who drove him away, and he departed.',
    35: 'A Psalm of David.',
    36: 'To the chief Musician, A Psalm of David the servant of the LORD.',
    37: 'A Psalm of David.',
    38: 'A Psalm of David, to bring to remembrance.',
    39: 'To the chief Musician, even to Jeduthun, A Psalm of David.',
    40: 'To the chief Musician, A Psalm of David.',
    41: 'To the chief Musician, A Psalm of David.',
    42: 'To the chief Musician, Maschil, for the sons of Korah.',
    44: 'To the chief Musician for the sons of Korah, Maschil.',
    45: 'To the chief Musician upon Shoshannim, for the sons of Korah, Maschil, A Song of loves.',
    46: 'To the chief Musician for the sons of Korah, A Song upon Alamoth.',
    47: 'To the chief Musician, A Psalm for the sons of Korah.',
    48: 'A Song and Psalm for the sons of Korah.',
    49: 'To the chief Musician, A Psalm for the sons of Korah.',
    50: 'A Psalm of Asaph.',
    51: 'To the chief Musician, A Psalm of David, when Nathan the prophet came unto him, after he had gone in to Bathsheba.',
    52: 'To the chief Musician, Maschil, A Psalm of David, when Doeg the Edomite came and told Saul, and said unto him, David is come to the house of Ahimelech.',
    53: 'To the chief Musician upon Mahalath, Maschil, A Psalm of David.',
    54: 'To the chief Musician on Neginoth, Maschil, A Psalm of David, when the Ziphims came and said to Saul, Doth not David hide himself with us?',
    55: 'To the chief Musician on Neginoth, Maschil, A Psalm of David.',
    56: 'To the chief Musician upon Jonath-elem-rechokim, Michtam of David, when the Philistines took him in Gath.',
    57: 'To the chief Musician, Al-taschith, Michtam of David, when he fled from Saul in the cave.',
    58: 'To the chief Musician, Al-taschith, Michtam of David.',
    59: 'To the chief Musician, Al-taschith, Michtam of David; when Saul sent, and they watched the house to kill him.',
    60: 'To the chief Musician upon Shushan-eduth, Michtam of David, to teach; when he strove with Aram-naharaim and with Aram-zobah, when Joab returned, and smote of Edom in the valley of salt twelve thousand.',
    61: 'To the chief Musician upon Neginah, A Psalm of David.',
    62: 'To the chief Musician, to Jeduthun, A Psalm of David.',
    63: 'A Psalm of David, when he was in the wilderness of Judah.',
    64: 'To the chief Musician, A Psalm of David.',
    65: 'To the chief Musician, A Psalm and Song of David.',
    66: 'To the chief Musician, A Song or Psalm.',
    67: 'To the chief Musician on Neginoth, A Psalm or Song.',
    68: 'To the chief Musician, A Psalm or Song of David.',
    69: 'To the chief Musician upon Shoshannim, A Psalm of David.',
    70: 'To the chief Musician, A Psalm of David, to bring to remembrance.',
    72: 'A Psalm for Solomon.',
    73: 'A Psalm of Asaph.',
    74: 'Maschil of Asaph.',
    75: 'To the chief Musician, Al-taschith, A Psalm or Song of Asaph.',
    76: 'To the chief Musician on Neginoth, A Psalm or Song of Asaph.',
    77: 'To the chief Musician, to Jeduthun, A Psalm of Asaph.',
    78: 'Maschil of Asaph.',
    79: 'A Psalm of Asaph.',
    80: 'To the chief Musician upon Shoshannim-eduth, A Psalm of Asaph.',
    81: 'To the chief Musician upon Gittith, A Psalm of Asaph.',
    82: 'A Psalm of Asaph.',
    83: 'A Song or Psalm of Asaph.',
    84: 'To the chief Musician upon Gittith, A Psalm for the sons of Korah.',
    85: 'To the chief Musician, A Psalm for the sons of Korah.',
    86: 'A Prayer of David.',
    87: 'A Psalm or Song for the sons of Korah.',
    88: 'A Song or Psalm for the sons of Korah, to the chief Musician upon Mahalath Leannoth, Maschil of Heman the Ezrahite.',
    89: 'Maschil of Ethan the Ezrahite.',
    90: 'A Prayer of Moses the man of God.',
    92: 'A Psalm or Song for the sabbath day.',
    98: 'A Psalm.',
    100: 'A Psalm of praise.',
    101: 'A Psalm of David.',
    102: 'A Prayer of the afflicted, when he is overwhelmed, and poureth out his complaint before the LORD.',
    103: 'A Psalm of David.',
    108: 'A Song or Psalm of David.',
    109: 'To the chief Musician, A Psalm of David.',
    110: 'A Psalm of David.',
    120: 'A Song of degrees.',
    121: 'A Song of degrees.',
    122: 'A Song of degrees of David.',
    123: 'A Song of degrees.',
    124: 'A Song of degrees of David.',
    125: 'A Song of degrees.',
    126: 'A Song of degrees.',
    127: 'A Song of degrees for Solomon.',
    128: 'A Song of degrees.',
    129: 'A Song of degrees.',
    130: 'A Song of degrees.',
    131: 'A Song of degrees of David.',
    132: 'A Song of degrees.',
    133: 'A Song of degrees of David.',
    134: 'A Song of degrees.',
    138: 'A Psalm of David.',
    139: 'To the chief Musician, A Psalm of David.',
    140: 'To the chief Musician, A Psalm of David.',
    141: 'A Psalm of David.',
    142: 'Maschil of David; A Prayer when he was in the cave.',
    143: 'A Psalm of David.',
    144: 'A Psalm of David.',
    145: "David's Psalm of praise.",
}


def parse_pg(path):
    """Return [(book, chapter, verse, text), ...] from one PG ebook."""
    verses = []
    current = None
    parts = []
    in_content = False

    with open(path, 'r', encoding='utf-8-sig') as infile:
        for raw in infile:
            line = raw.strip()
            if END_MARK in line:
                break
            match = VERSE_RE.match(line)
            if match:
                if current is not None:
                    verses.append((*current, ' '.join(parts).strip()))
                current = (
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
                parts = [match.group(4).strip()]
                in_content = True
            elif in_content and line:
                parts.append(line)

    if current is not None:
        verses.append((*current, ' '.join(parts).strip()))
    return verses


def unshout(text):
    """Sentence-case a verse Gutenberg printed entirely in capitals."""

    def lower_word(match):
        word = match.group(0)
        if word == 'LORD':
            return word
        return word.lower()

    out = re.sub(r"\b[A-Z]+(?:'[A-Z]+)?\b", lower_word, text)
    out = out[0].upper() + out[1:]
    out = re.sub(r'\bo\b', 'O', out)
    out = re.sub(r'\bgod\b', 'God', out)
    out = out.replace('most high', 'most High')
    return out


def normalize(book, chapter, verse, text):
    text = text.replace('\u2019', "'")
    if (book, chapter, verse) in SHOUTING_VERSES:
        text = unshout(text)
    elif (book, chapter, verse) == (42, 1, 5):
        text = text.replace('THERE ', 'There ', 1)
    elif (book, chapter, verse) == (20, 22, 1):
        text = text.replace('A GOOD name', 'A good name', 1)
    elif (book, chapter, verse) == (25, 3, 1):
        text = text.replace('I AM the man', 'I am the man', 1)
    if book == 19 and verse == 1 and chapter in PSALM_SUPERSCRIPTION:
        text = PSALM_SUPERSCRIPTION[chapter] + ' ' + text
    return text


def check_structure(book_index, verses):
    mark, _title, chapters, expected = BOOKS[book_index - 1]
    errors = []
    if len(verses) != expected:
        errors.append(f'{mark}: {len(verses)} verses, expected {expected}')

    seen_chapters = []
    last_chapter = 0
    last_verse = 0
    for book, chapter, verse, text in verses:
        if book != book_index:
            errors.append(f'{mark}: verse {chapter}:{verse} is numbered as book {book}')
        if not text:
            errors.append(f'{mark} {chapter}:{verse} is empty')
        if TEX_SPECIAL_RE.search(text):
            errors.append(f'{mark} {chapter}:{verse} contains a TeX-special character')
        if chapter != last_chapter:
            if chapter != last_chapter + 1:
                errors.append(f'{mark}: chapter jumps from {last_chapter} to {chapter}')
            if verse != 1:
                errors.append(f'{mark} {chapter}:{verse} does not start the chapter at verse 1')
            seen_chapters.append(chapter)
            last_chapter = chapter
            last_verse = 1
        else:
            if verse != last_verse + 1:
                errors.append(
                    f'{mark}: verse jumps from {chapter}:{last_verse} to {chapter}:{verse}'
                )
            last_verse = verse

    if seen_chapters != list(range(1, chapters + 1)):
        errors.append(f'{mark}: chapters are {seen_chapters}, expected 1..{chapters}')
    return errors


def write_txs(path, verses):
    lines = [
        f'#{chapter}:{verse} {normalize(book, chapter, verse, text)}\n'
        for book, chapter, verse, text in verses
    ]
    path.write_text(''.join(lines), encoding='utf-8')


def write_psalm_format(path):
    """Italicize each superscription, which is the opening of verse 1."""
    lines = [
        '% King James psalm superscriptions.',
        '% The words stand at the start of verse 1 in KJV-Ps.txs.',
        '% Psalms with no superscription are not listed.',
        '',
    ]
    for chapter, title in PSALM_SUPERSCRIPTION.items():
        lines.append(f'\\fmtfont{{{chapter}:1}}{{{title}}}{{\\it}}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def convert_directory(pg_dir, out_dir):
    pg_dir = Path(pg_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    errors = []
    total = 0
    for index, (mark, _title, _chapters, _verses) in enumerate(BOOKS, start=1):
        source = pg_dir / f'{8000 + index}.txt'
        if not source.exists():
            errors.append(f'missing {source}')
            continue
        verses = parse_pg(source)
        errors.extend(check_structure(index, verses))
        write_txs(out_dir / f'KJV-{mark}.txs', verses)
        total += len(verses)
        print(f'KJV-{mark}.txs  {len(verses)} verses')
    write_psalm_format(out_dir.parent / 'formats' / 'fmt-KJV-Ps.tex')
    print('formats/fmt-KJV-Ps.tex  psalm superscriptions')
    if total != 31102:
        errors.append(f'total verses {total}, expected 31102')
    return errors


def convert_one(input_path, output_path):
    verses = parse_pg(input_path)
    if not verses:
        raise SystemExit(f'no verses found in {input_path}')
    book_index = verses[0][0]
    if not 1 <= book_index <= 66:
        raise SystemExit(f'unrecognized book number {book_index} in {input_path}')
    errors = check_structure(book_index, verses)
    write_txs(Path(output_path), verses)
    mark = BOOKS[book_index - 1][0]
    print(f'{output_path}: {len(verses)} verses ({mark})')
    return errors


def main(argv):
    if len(argv) == 3 and argv[1] == '--pg-dir':
        errors = convert_directory(argv[2], Path(__file__).resolve().parent)
    elif len(argv) == 3:
        errors = convert_one(argv[1], argv[2])
    else:
        print('Usage: python3 convert_to_txs.py --pg-dir DIR')
        print('       python3 convert_to_txs.py INPUT.txt OUTPUT.txs')
        return 1
    if errors:
        print('Problems:')
        for error in errors:
            print(f'  {error}')
        return 1
    print('All books match the King James verse counts.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
