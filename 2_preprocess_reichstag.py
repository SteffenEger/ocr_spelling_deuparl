import collections
import glob
import os
import re

import tqdm as tqdm

if __name__ == "__main__":

    bucket_folders = list(sorted(glob.glob("data/1_collected/Reichstag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        # Reichstag -> bucket name is year
        bucket_name = int(bucket_folder[-5:-1])

        if not os.path.isdir(f"data/2_preprocessed/Reichstag/{bucket_name}/"):
            os.makedirs(f"data/2_preprocessed/Reichstag/{bucket_name}/")

        file_paths = list(sorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                lines = file.readlines()

                # delete strange lines from the beginning 
                startline = 0
                if bucket_name == 1867:
                    for line in lines:
                        if "Kirth's" or "Kirth's" not in line:
                            startline += 1
                        else:
                            break

                if startline != len(lines):
                    lines = lines[startline:]

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

                # remove noisy digits
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

                # remove linebreaks
                lines = [re.sub(r'[\n\t]', '', line).strip() for line in lines]

                # replace digits
                #lines = [re.sub(r'\d+', ' 0 ', line).strip() for line in lines]

                # reduce numerical sequences
                lines = [re.sub(r'((0)\s?){2,}', '\\2 ', line).strip() for line in lines]

                # filter doc
                lines = [line for line in lines if len(line) > 1]

                # lowercase
                lines_tokens = [[tok.lower() for tok in line.split()]
                            for line in lines]


                count_per_bucket[bucket_name] += 1
                with open(f"data/2_preprocessed/Reichstag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "w", encoding="utf-8") as file:
                    for line in lines:
                        file.write(line + "\n")
