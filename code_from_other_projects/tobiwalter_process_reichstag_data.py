import glob
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import List

import dateparser as dateparser
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
    YEARS = [1895, 1918, 1933, 1942]

    with open("../harmonize_dict.txt", encoding="utf-8") as file:
        spelling_dict = {line.split()[0]: line.split()[1] for line in file}

    ####################################################################################################################
    # 1. Extract Reichstag proceedings from each of the original files
    ####################################################################################################################
    print("\n\n\n1. Extract Reichstag proceedings from each of the original files")

    documents = defaultdict(list)

    for year in YEARS:
        print("Processing year: ", year)

        # read input file
        with open("data/source/" + str(year) + ".corr.seg", encoding="utf-8") as file:
            lines = file.readlines()

        ################################################################################################################
        # minor text cleaning before protocols are extracted
        ################################################################################################################

        # remove punctuation FIXME: nicht mehr
        pattern = re.compile('[%s]' % re.escape('!"#$&\'()*+,./:;<=>?@®©[\\]^_`{|}~„“«»'))
        lines = [re.sub(pattern, '', line).strip() for line in tqdm(lines)]

        # remove double spaces
        lines = [re.sub('\s\s+', ' ', line).strip() for line in tqdm(lines)]

        # remove noisy digits
        # 'Remove digits that are appending, prepending or in the middle of some words, e.g. because of faulty OCR'
        lines = [re.sub(r'\b\d(?P<quote>[A-Za-zßäöüÄÖÜ]+)\b', '\g<quote>', line) for line in tqdm(lines)]
        lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d\b', '\g<quote>', line) for line in tqdm(lines)]
        lines = [re.sub(r'\b(?P<quote>[A-Za-zßäöüÄÖÜ]+)\d(?P<name>[A-Za-zßäöüÄÖÜ]*)\b', '\g<quote> \g<name>', line) for
                 line in tqdm(lines)]

        # remove dash and minus signs
        # 'Remove lone standing dashes/hyphens at beginning, middle and end of lines.'
        lines = [re.sub(r'\s(-|—|–|\s)+\s', ' ', line) for line in tqdm(lines)]
        lines = [re.sub(r'^(-|—|–|\s)+\s', '', line) for line in tqdm(lines)]
        lines = [re.sub(r'\b\s(-|—|–|\s)+$', '', line) for line in tqdm(lines)]

        ################################################################################################################
        # extract protocols
        ################################################################################################################
        print("extract protocols")
        start_patterns = '|'.join(
            ['(Z|I)ch eröffne die (\d+ |erste )?(\n )?Sitzung',
             'Di(e|s) (\d+ |erste )?(\n )?Sitzung (\n )?ist (\n )?erö(f|s)(f|s)net',
             'Die Sitzung-ist eröffnet',
             'eröffne ich (hiermit )?die Sitzung',
             'Ich eröffne die \d+$',
             '(Z|I)ch erkläre die (\d+ |erste )?Sitzung für eröffnet']
        )

        restart_patterns = '|'.join(
            ['Die (\n )?Sitzung (\n )?ist wieder (\n )?eröffnet',

             'Ich eröffne die Sitzung wieder',
             'Ich eröffne die Sitzung von neuem',
             'Ich eröffne die Sitzung noch einmal'
             ])

        end_patterns = '|'.join(
            ['(Schluß|Schluss|Sckluß) der Sitzung (um )?\d+ Uhr',
             'Die Sitzung ist geschlossen',
             'Die Sitzung ist geschloffen',
             'Ich schließe die (\n )?Sitzung'
             ])

        i = 0
        sitzung = False

        current_doc = None

        reichstag_restart = re.compile(f"({restart_patterns})", re.IGNORECASE)
        reichstag_end = re.compile(f"({end_patterns})", re.IGNORECASE)

        if year == 1942:
            reichstag_start = re.compile(
                r'Die Sitzung wird um \d+ Uhr(?:\s\d+ Minute)?n?(?:\sabends)? durch den Präsidenten eröffnet',
                re.IGNORECASE)
        else:
            reichstag_start = re.compile(f"({start_patterns})", re.IGNORECASE)

        # Check in each line if a session was started, ended, interrupted or restarted
        for line in tqdm(lines):
            sitzung_restart = reichstag_restart.search(line)
            sitzung_start = reichstag_start.search(line)
            sitzung_end = reichstag_end.search(line)
            sitzung_abgebrochen = re.search(r'Die Sitzung wird um \d+ Uhr (?:\d+ Minute)?n? abgebrochen', line,
                                            re.IGNORECASE)

            if sitzung_restart:
                sitzung = True
                current_doc.append(line)
                continue
            if sitzung_start:
                i += 1
                # Set the bool 'sitzung' to True, so that each line is written to the document as long as a session is not ended or interrupted
                sitzung = True
                # Creat a new document when new session was found
                if current_doc:
                    documents[year].append("\n".join(current_doc) + "\n")
                current_doc = [line]
                continue
            if sitzung_end or sitzung_abgebrochen:
                if current_doc is not None:
                    current_doc.append(line)
                    # Set the bool 'sitzung' to False, so that lines are not written to the document as long as another starting phrase was found
                    sitzung = False
                    continue

            if sitzung:
                if len(line) > 1:
                    current_doc.append(line)

        print('Screening done!')
        print(f'{i} documents extracted in total.')
        if current_doc:
            documents[year].append("\n".join(current_doc) + "\n")

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

    ####################################################################################################################
    # sort corpora
    ####################################################################################################################
    print("sort corpora")
    corpora = defaultdict(list)

    start_dates = {
        1895: '22 Oktober 1889',
        1918: '3 Dezember 1895',
        1933: '6 Februar 1919',
        1942: '21 März 1933'
    }

    periods = {
        1895: {'start': datetime(1867, 2, 24), 'end': datetime(1895, 5, 24)},
        1918: {'start': datetime(1895, 12, 3), 'end': datetime(1918, 10, 26)},
        1933: {'start': datetime(1919, 2, 6), 'end': datetime(1932, 12, 9)},
        1942: {'start': datetime(1933, 3, 21), 'end': datetime(1942, 4, 26)},
    }

    for year in YEARS:
        print("Processing year: ", year)
        # Initialize a list that stores each protocol with its corresponding date
        corpus_and_dates = []

        # The variable last_date keeps track of the last valid date encountered in order to keep a chronological ordering - it is initialized with the start date in each corpus
        last_date = dateparser.parse(start_dates.get(year))
        period_start = periods.get(year).get('start')
        period_end = periods.get(year).get('end')

        # Retrieve files in chronological order of creation
        date_matches = 0
        for document in tqdm(documents[year]):
            lines = [line.strip() for line in document.split("\n")]
            # For each protocol, check if a date can be extracted
            date_match = re.search(
                r'\d+ Sitzung (?:am )?(?:Montag |Dienstag |Mittwoch |Donnerstag |Freitag |Sonnabend |Sonntag )?(?:den )?(\d+ (?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember) \d{4})',
                " ".join(lines))

            # If match found, assign it to date variable
            if date_match:
                date_matches += 1
                date = date_match.groups()[0]
                date = dateparser.parse(date)

                if date is not None:
                    # if date out of period range due to OCR error, impute date with last valid date
                    if date < period_start or date > period_end:
                        date = last_date
                else:
                    # if date is None (e.g. due to an OCR error -> 38 Januar instead of 28 Januar), impute date with last valid date
                    date = last_date

                # Store the last valid date to impute instances for which no or a faulty date was found
                last_date = date

            # If no date match at all, impute with last valid date
            else:
                date = last_date

            # Store protocol in the list along with its associated date
            corpus_and_dates.append((date, document))

        print("date_matches:", date_matches)

        # At the end, sort the corpus by date
        corpora[year] = sorted(corpus_and_dates, key=lambda x: x[0])

    ####################################################################################################################
    # create slices
    ####################################################################################################################
    print("create slices")
    slices = {}

    # Split up corpus_1 as one part belongs to first historic slice, and the other to the second historic slice
    end_bismarck = 0
    for i in range(len(corpora[YEARS[0]])):
        # 25 January 1990 is the split date, so search for the first protocol having a higher date
        if corpora[YEARS[0]][i][0] > datetime(1890, 1, 25):
            end_bismarck = i
            break

    print("end_bismarck:", end_bismarck)

    # remove dates
    for year, documents in corpora.items():
        corpora[year] = [document[1] for document in documents]

    periods = {
        1895: {'start': datetime(1867, 2, 24), 'end': datetime(1895, 5, 24)},
        1918: {'start': datetime(1895, 12, 3), 'end': datetime(1918, 10, 26)},
        1933: {'start': datetime(1919, 2, 6), 'end': datetime(1932, 12, 9)},
        1942: {'start': datetime(1933, 3, 21), 'end': datetime(1942, 4, 26)},
    }

    slices["0-KR1"] = corpora[YEARS[0]][:end_bismarck]
    slices["1-KR2"] = corpora[YEARS[0]][end_bismarck:] + corpora[YEARS[1]]
    slices["2-WR"] = corpora[YEARS[2]]
    slices["3-NS"] = corpora[YEARS[3]]

    # elif HISTORIC_OR_BALANCED == "balanced":
    #     # remove dates
    #     for year, documents in corpora.items():
    #         corpora[year] = [document[1] for document in documents]
    #
    #     # slice into equal parts
    #     full_corpus = []
    #     for year in YEARS:
    #         full_corpus += corpora[year]
    #     slice_border = round(len(full_corpus) / 5)
    #
    #     index = 0
    #     while index * slice_border < len(full_corpus):
    #         slices[str(index)] = full_corpus[index * slice_border:(index + 1) * slice_border]
    #         index += 1

    # store slices
    print("store slices")
    for name, docs in slices.items():
        if not os.path.isdir("data/tobiwalter_data_processed/slices/" + name + "/"):
            os.makedirs("data/tobiwalter_data_processed/slices/" + name + "/")
        for index, document in enumerate(docs):
            with open("data/tobiwalter_data_processed/slices/" + str(name) + "/" + str(index) + ".txt", "w",
                      encoding="utf-8") as file:
                file.write(document)

    # ####################################################################################################################
    # # 3. Process resulting slices
    # ####################################################################################################################
    print("\n\n\n3. Process resulting slices")

    # load slices
    print("load slices")
    slices = defaultdict(list)
    names = ["0-KR1", "1-KR2", "2-WR", "3-NS"]
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

            # remove linebreaks
            lines = [re.sub(r'[\n\t]', '', line).strip() for line in lines]

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
            lines_tokens = [[tok.lower() for tok in line.split()] for line in lines]

            # remove umlauts
            lines_tokens = [remove_umlauts(line) for line in lines_tokens]

            # harmonize spelling
            lines_tokens = [[re.sub(tok, spelling_dict[tok], tok) if tok in spelling_dict else tok for tok in line] for
                            line in lines_tokens]

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
