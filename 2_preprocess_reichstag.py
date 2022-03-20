import collections
import glob
import os
import re
from natsort import natsorted
import tqdm as tqdm

pattern = re.compile(r"""   
                                ^M{0,3}
                                (CM|CD|D?C{0,3})?
                                (XC|XL|L?X{0,3})?
                                (IX|IV|V?(I|i|H){0,3})?$
            """, re.VERBOSE)


def line_start_with_number(line):
    if line[0].isdigit() or (len(line) > 1 and line[0] in ['L', 'Z'] and line[1] == '.'):
        return True
    if (line[0].islower() and len(line) > 2 and line[1] == '.' and line[0] != 'v'):
        return True
    #if (line.startswith("Art.")):
    #    return True
    if re.match(pattern, line.split(' ')[0].replace(".", "")):
        return True
    if len(line) > 2 and line[0] == '.' and line[1].isdigit():
        return True
    return False

abbreviations_start = ['.', '-', ' ']
words1 = ["a", "b", "d", "i", "K", "m", "s", "S", "u", "v", "z", "Z", 'D']

def new_line(sentance, dot_at):
    if (line[c] not in ".?!;"):
        return False
    # abbreviations of words with one letter
    if dot_at > 1 and (sentance[dot_at - 2] in abbreviations_start) or dot_at == 1:
        word1 = sentance[dot_at - 1:dot_at]
        if word1 in word1:
            return False
    # abbreviations of words with two letter
    if (dot_at > 2 and sentance[dot_at - 3] in abbreviations_start) or dot_at == 2:
        word2 = sentance[dot_at - 2:dot_at]
        if word2 in ["ca", "rc", "re", "Fl", "Dr", "St", "Fr", "Kr", "Pr", "Sr"]:
            return False
    # abbreviations of words with three letter
    if (dot_at > 3 and sentance[dot_at - 4] in abbreviations_start) or dot_at == 3:
        word3 = sentance[dot_at - 3:dot_at]
        if word3 in ["Bew", "Grf", "Str", "Inf", "Reg", "Grs", "Kgr", "Bzg", "dir"]:
            return False
    # abbreviations of words with four letter
    if (dot_at > 4 and sentance[dot_at - 5] in abbreviations_start) or dot_at == 4:
        word4 = sentance[dot_at - 4:dot_at]
        if word4 in ["Prov", "Thlr"]:
            return False
    # abbreviations of words with five letter
    if (dot_at > 5 and sentance[dot_at - 6] in abbreviations_start) or dot_at == 5:
        word5 = sentance[dot_at - 5:dot_at]
        if word5 in ["Preuß", "indir"]:
            return False
    # no linebreak before - and :
    if (len(sentance) - dot_at) > 1 and sentance[dot_at + 1] == '-' and sentance[dot_at + 1] == ':':
        return False
    # no linebreak before digit like 1.2
    if re.search('[0-9]', sentance[dot_at - 1]) or re.search('[0-9]', sentance[dot_at - 2]):
        return False
    # linebreak by '.Word' oder ..
    if (len(sentance) - dot_at) > 1 and (sentance[dot_at + 1].isupper() or sentance[dot_at + 1] == '.'):
        return True
    # linebreak by '. Word'
    if (len(sentance) - dot_at) > 2 and sentance[dot_at + 2].isupper():
        return True
    # linebreak at end of line
    if (len(sentance) - 1 == dot_at):
        return True
    # else  no linebreak
    return False


def remove_one(sentance, oneAt):
    if (oneAt < len(sentance) - 1 and sentance[oneAt + 1].isalpha()):
        return True
    else:
        return False


if __name__ == "__main__":

    bucket_folders = list(natsorted(glob.glob("data/1_collected/Reichstag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        # Reichstag -> bucket name is year
        bucket_name = int(bucket_folder[-5:-1])

        if not os.path.isdir(f"data/2_preprocessed/Reichstag/{bucket_name}/"):
            os.makedirs(f"data/2_preprocessed/Reichstag/{bucket_name}/")

        file_paths = list(natsorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                lines = file.readlines()

                # delete strange lines from the beginning
                startline = 0
                if bucket_name == 1867:
                    for line in lines:
                        if "Kirth's" not in line or "Kirth's" not in line:
                            startline += 1
                        else:
                            break
                    if startline != len(lines):
                        lines = lines[startline:]
                else:
                    break

                # fix splitted words at the end of a line
                # ... Bundes-
                # tag ...
                # -> ... Bundestag ...
                lines_fix, buffer = [], []
                for line in lines:
                    if line[-2:] == '¬\n' or line[-2:] == '-\n' or line[-2:] == '—\n' or line[-2:] == '–\n':
                        buffer.append(line[:-2])
                    elif len(buffer) != 0 and line[:1].islower():
                        buffer.append(line[:-1])
                        lines_fix.append("".join(buffer))
                        buffer = []
                    elif len(buffer) != 0:
                        buffer.append(line[:-1])
                        lines_fix.append("-".join(buffer))
                        buffer = []
                    else:
                        lines_fix.append(line)
                lines = lines_fix

                # remove double spaces
                lines = [re.sub('\s\s+', ' ', line).strip() for line in lines]

                # remove noisy digits TODO first letter of a line like $ in "$ Test geht weiter"
                # 'Remove digits that are appending, prepending or in the middle of some words, e.g. because of faulty OCR'
                lines = [re.sub(r'\b\d(?P<quote>[A-Za-zßäöüÄÖÜ]+)\b',
                                '\g<quote>', line) for line in lines]
                lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d\b',
                                '\g<quote>', line) for line in lines]
                lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d(?P<name>[A-Za-zßäöüÄÖÜ]*)\b',
                                '\g<quote> \g<name>', line) for line in lines]

                # remove dash and minus signs
                # 'Remove lone standing dashes/hyphens at beginning, middle and end of lines.'
                lines = [re.sub(r'\s(-|—|–|\s)+\s', ' ', line)
                         for line in lines]
                lines = [re.sub(r'^(-|—|–|\s)+\s', '', line) for line in lines]
                lines = [re.sub(r'\b\s(-|—|–|\s)+$', '', line)
                         for line in lines]
                # remove some random chars
                lines = [re.sub(r'(<|>|\^|«|»|\*)', ' ', line)
                         for line in lines]

                # remove linebreaks
                lines = [re.sub(r'[\n\t]', '', line).strip() for line in lines]

                # replace digits
                #lines = [re.sub(r'\d+', ' 0 ', line).strip() for line in lines]

                # removes ... #TODO replace with other place holder
                lines = [re.sub(r'\.\.\.', ' ', line).strip() for line in lines]

                # reduce 
                #lines = [ re.sub(r'(\.| ){3}', ' \n', line).strip() for line in lines]
                lines_fix, buffer = [], []
                for line in lines:
                    line = re.sub(r'(\.| ){3}', ' $', line).strip()
                    for a in line.split("$"):
                        lines_fix.append("".join(a))
                
                lines = lines_fix

                # reduce numerical sequences
                #lines = [ re.sub(r'((0)\s?){2,}', '\\2 ', line).strip() for line in lines]

                # filter doc
                lines = [line for line in lines if len(line) > 1]
                lines = [line for line in lines if line.count('/') < 4]
                lines = [line for line in lines if line.count('_') < 2]

                # lowercase
                lines_tokens = [[tok.lower() for tok in line.split()]
                                for line in lines]

                
                # split text in sentances
                a = 0
                lines_fix, buffer = [], []
                for line in lines:

                    for c in range(len(line)):

                        if line[c] == '1' and remove_one(line, c):
                            string_list = list(line)
                            string_list[c] = " "
                            line = "".join(string_list)

                        # for listings c == 0 and
                        if c == len(line) - 1 and line_start_with_number(line):
                            lines_fix.append("".join(buffer))
                            buffer = []
                            buffer.append(line)
                            # break

                        elif line_start_with_number(line):
                            continue

                        # line is part of a santence that alrady started
                        elif c == len(line) - 1 and not new_line(line, c):
                            buffer.append(line[a - len(line) - 1:] + " ")

                        # found a dot and checks if it needs to be splitted
                        elif new_line(line, c):
                            buffer.append(line[a - len(line) - 1: c + 1])
                            lines_fix.append("".join(buffer))
                            buffer = []
                            a = c + 2
                    a = 0

                lines = lines_fix
                # """
                
                # puts smal lines together
                minLineLen = 10
                lines_fix, buffer = [], []
                for line in lines:
                    if buffer == []:
                        buffer.append(line)
                    elif len(line) < minLineLen:
                        buffer.append(line)
                    else:
                        lines_fix.append("".join(buffer))
                        buffer = []
                        buffer.append(line)

                lines = lines_fix

                # deletes useless liens
                lines = [line for line in lines if re.search('[a-zA-Z]', line)]

                # remove not needed white spaces
                lines = [re.sub('\s\s+', ' ', line).strip() for line in lines]

                count_per_bucket[bucket_name] += 1
                with open(f"data/2_preprocessed/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "w", encoding="utf-8") as file:
                    for line in lines:
                        file.write(line + "\n")
