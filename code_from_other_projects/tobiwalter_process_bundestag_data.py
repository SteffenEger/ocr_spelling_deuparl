import glob
import os
import re
from collections import defaultdict
from typing import List

from tqdm import tqdm


def remove_umlauts(sentence: List) -> str:
    text_out = []
    for tok in sentence:
        res = tok.replace('ä', 'ae')
        res = res.replace('ö', 'oe')
        res = res.replace('ü', 'ue')
        res = res.replace('Ä', 'Ae')
        res = res.replace('Ö', 'Oe')
        res = res.replace('Ü', 'Ue')
        text_out.append(res)
    return text_out


def remove_hyphens(sentence: str, split_chars="-|—|–") -> str:
    """Remove hyphens that are still prepending or appending words, After splitting up chain words -> They are either noise or a chain word was not successfully split"""

    new_text = sentence
    for t in sentence.split():
        parts = []
        for p in re.split(split_chars, t):  # for each part p in compound token t
            if not p:
                continue  # skip empty part
            else:  # add p as separate token
                parts.append(p)
        if len(parts) > 0:
            new_text = new_text.replace(t, "-".join(parts))
    return new_text


if __name__ == "__main__":
    YEARS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    with open("../harmonize_dict.txt", encoding="utf-8") as file:
        spelling_dict = {line.split()[0]: line.split()[1] for line in file}

    ####################################################################################################################
    # 1. Extract from original files
    ####################################################################################################################
    print("\n\n\n1. Extract from original files")

    documents = defaultdict(list)

    for year in YEARS:
        print("Processing year: ", year)

        start_pattern_matched = 0
        end_pattern_matched = 0

        # read input files
        file_paths = glob.glob("data/source/BRD Protocols - Sentence Split/" + str(year) + "/*.txt")
        for file_path in tqdm(file_paths):
            with open(file_path, encoding="utf-8") as file:
                lines = file.readlines()

            ############################################################################################################
            # minor text cleaning before protocols are extracted
            ############################################################################################################
            start_patterns_bundestag = '|'.join(
                ['Ich eröffne die \d+ (\n )?Sitzung',
                 'Die \d+ (\n )?Sitzung des (Deutschen)? (Bundestages|Bundestags) ist eröffnet',
                 'Ich erkläre die \d+ (\n )?Sitzung des (Deutschen )?(Bundestages|Bundestags) für eröffnet',
                 'Die (\n )?Sitzung (\n )?ist (\n )?eröffnet',
                 'Ich (\n )?eröffne (\n )?die (\n )?Sitzung',
                 'Beginn:? \d+ Uhr']
            )
            end_patterns_bundestag = '|'.join(
                ['(Schluß|Schluss) der Sitzung \d+',
                 'Die Sitzung ist geschlossen',
                 'Ich schließe die (\n )?Sitzung'
                 ])
            bundestag_start = re.compile(f"({start_patterns_bundestag})", re.IGNORECASE)
            bundestag_end = re.compile(f"({end_patterns_bundestag})", re.IGNORECASE)

            # remove punctuation
            pattern = re.compile('[%s]' % re.escape('!"#$&\'()*+,./:;<=>?@®©[\\]^_`{|}~„“«»'))
            lines = [re.sub(pattern, '', line).strip() for line in lines]

            # remove double spaces
            lines = [re.sub('\s\s+', ' ', line).strip() for line in lines]

            # extract protocol bundestag
            temp = "\n".join(lines)

            # Search for start and end pattern
            sitzung_start = bundestag_start.search(temp)
            sitzung_end = bundestag_end.search(temp)

            if sitzung_start:
                start_pattern_matched += 1
                # If both patterns found, return only text between start and end indices of the matching objects
                if sitzung_end:
                    end_pattern_matched += 1
                    temp = temp[sitzung_start.start():sitzung_end.end()]
                # If only one of start/end patterns is found, discard all text before/after the found pattern.
                else:
                    temp = temp[sitzung_start.start():]
            elif sitzung_end:
                end_pattern_matched += 1
                temp = temp[:sitzung_end.end()]

            # Split string by new-line character to transform protocol back to line format
            lines = temp.split(' \n ')

            # remove linebreaks
            lines = [re.sub(r'[\n\t]', '', line).strip() for line in lines]

            # remove noisy digits
            # 'Remove digits that are appending, prepending or in the middle of some words, e.g. because of faulty OCR'
            lines = [re.sub(r'\b\d(?P<quote>[A-Za-zßäöüÄÖÜ]+)\b', '\g<quote>', line) for line in lines]
            lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d\b', '\g<quote>', line) for line in lines]
            lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d(?P<name>[A-Za-zßäöüÄÖÜ]*)\b', '\g<quote> \g<name>', line)
                     for line in lines]

            # remove dash and minus signs
            # 'Remove lone standing dashes/hyphens at beginning, middle and end of lines.'
            lines = [re.sub(r'\s(-|—|–|\s)+\s', ' ', line) for line in lines]
            lines = [re.sub(r'^(-|—|–|\s)+\s', '', line) for line in lines]
            lines = [re.sub(r'\b\s(-|—|–|\s)+$', '', line) for line in lines]

            documents[year].append("\n".join(lines) + "\n")

        print("start_pattern_matched:", start_pattern_matched / len(documents[year]))
        print("end_pattern_matched:", end_pattern_matched / len(documents[year]))

    # store documents
    print("store documents")
    for year, docs in documents.items():
        if not os.path.isdir("data/tobiwalter_data_processed/documents/" + str(year) + "/"):
            os.makedirs("data/tobiwalter_data_processed/documents/" + str(year) + "/")
        for index, document in enumerate(docs):
            with open("data/tobiwalter_data_processed/documents/" + str(year) + "/" + str(index) + ".txt", "w",
                      encoding="utf-8") as file:
                file.write(document)

    ####################################################################################################################
    # 2. Create slices
    ####################################################################################################################
    print("\n\n\n2. Create slices")

    # load documents
    print("load documents")
    documents = defaultdict(list)
    for year in YEARS:
        file_paths = glob.glob("data/tobiwalter_data_processed/documents/" + str(year) + "/*.txt")
        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                documents[year].append(file.read())

    periods = {  # FIXME are these the correct matchings?
        "CDU1": [1, 2, 3, 4, 5],
        "SPD1": [6, 7, 8, 9],
        "CDU2": [10, 11, 12, 13],
        "SPD2": [14, 15],
        "CDU3": [16, 17, 18, 19]
    }

    slices = defaultdict(list)
    for name, indices in periods.items():
        for index in indices:
            slices[name] += documents[index]

    # store slices
    print("store slices")
    for slice_index, (name, docs) in enumerate(slices.items()):
        if not os.path.isdir("data/tobiwalter_data_processed/slices/" + name + "/"):
            os.makedirs("data/tobiwalter_data_processed/slices/" + name + "/")
        for index, document in enumerate(docs):
            with open("data/tobiwalter_data_processed/slices/" + str(slice_index) + "-" + name + "/" + str(index) + ".txt", "w", encoding="utf-8") as file:
                file.write(document)

    ####################################################################################################################
    # 3. Process resulting slices
    ####################################################################################################################
    print("\n\n\n3. Process resulting slices")

    # load slices
    print("load slices")
    slices = defaultdict(list)
    names = ["4-CDU1", "5-SPD1", "6-CDU2", "7-SPD2", "8-CDU3"]
    for name in names:
        file_paths = glob.glob("data/tobiwalter_data_processed/slices/" + name + "/*.txt")
        for file_path in file_paths:
            with open(file_path, encoding="utf-8") as file:
                slices[name].append(file.read())

    processed_slices = defaultdict(list)

    for name, documents in slices.items():
        print("\n\nProcessing slice:", name)

        for document in tqdm(documents):
            lines = document.split("\n")

            # replace digits
            lines = [re.sub(r'\d+', ' 0 ', line).strip() for line in lines]

            # remove double spaces
            lines = [re.sub('\s\s+', ' ', line).strip() for line in lines]

            # reduce numerical sequences
            lines = [re.sub(r'((0)\s?){2,}', '\\2 ', line).strip() for line in lines]

            # filter doc
            lines = [line for line in lines if len(line) > 1]

            # remove german chain words
            # lines = [remove_german_chainwords(line) for line in lines]  # FIXME: cannot do this because of missing package char_split

            # remove hyphens
            lines = [remove_hyphens(line) for line in lines]

            # lemmatize
            # lines = [lemmatizer.lemmatize(line) for line in lines]  # FINDME: not doing lemmatization

            # lowercase
            lines_tokens = [[tok.lower() for tok in line.split()] for line in lines]  # FINDME: do split() instead of lemmatization

            # remove umlauts
            lines_tokens = [remove_umlauts(line) for line in lines_tokens]

            # harmonize spelling
            lines_tokens = [[re.sub(tok, spelling_dict[tok], tok) if tok in spelling_dict else tok for tok in line] for line in lines_tokens]

            processed_slices[name].append("\n".join([" ".join(tokens) for tokens in lines_tokens]))

    # store slices
    print("store processed slices")
    for name, docs in processed_slices.items():
        if not os.path.isdir("data/tobiwalter_data_processed/processed_slices/" + name + "/"):
            os.makedirs("data/tobiwalter_data_processed/processed_slices/" + name + "/")
        for index, document in enumerate(docs):
            with open("data/tobiwalter_data_processed/processed_slices/" + str(name) + "/" + str(index) + ".txt", "w",
                      encoding="utf-8") as file:
                file.write(document)

    print("Done!")
