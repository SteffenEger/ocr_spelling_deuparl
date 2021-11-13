import collections
import glob
import os
from xml.etree import ElementTree

import tqdm

if __name__ == "__main__":

    #######################################
    # https://github.com/SteffenEger/Corpus
    #######################################

    # load the mapping
    mapping = {}

    with open("data/source/Reichstag/BSB_Reichstagsprotkolle_Konkordanz.csv", encoding="utf-8") as file:
        # skip header
        _ = file.readline()
        _ = file.readline()
        _ = file.readline()

        for line in file:
            if line != "":
                bsb_id = line[:line.index("\t")]
                year = line[line.rindex("\t") + 1:-1]
                mapping[bsb_id] = year

    bsb_folders = glob.glob("/storage/nllg/compute-share/eger/melvin/reichstagsprotokolle/bsb*/")

    # load the documents
    idx_per_year = collections.Counter()
    for bsb_folder in tqdm.tqdm(bsb_folders):
        year = mapping[bsb_folder[-12:-1]]

        file_paths = list(sorted(glob.glob(bsb_folder + "xml/*.xml")))

        ##########################################################################
        # source: https://github.com/SteffenEger/Corpus/blob/master/XML_Parsing.py
        ##########################################################################
        lines = []
        for file_path in file_paths:
            punctuation = ['.', ',', ':', ';', '!', '?', '(', ')']
            root = ElementTree.parse(file_path).getroot()

            # taking into account the XML files' particularities. The given corpus was got as the result of the work of Fine Reader programme.
            for line in root.iter('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}line'):
                s = []
                for char_param in line.iter('{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}charParams'):
                    # separating text into lines
                    if char_param.text == None:
                        char_param.text = " "
                    # if char_param.text in punctuation:
                    #     char_param.text = char_param.text + " "
                    s.append(char_param.text)
                lines.append("".join(s))

        text = "\n".join(lines)

        ######################################################################################
        # source: https://github.com/SteffenEger/Corpus/blob/master/Text_U%CC%88berarbeitet.py
        ######################################################################################
        #
        # # concatenates lines based on "-", better to do this in postprocessing after OCR post-correction
        #
        # new_lines = []
        # prevLine = ""
        # for line in lines:
        #     line = line.strip()
        #     if line[-1] == "¬" or line[-1] == "-":
        #         prevLine = prevLine + line[:-1]
        #     else:
        #         new_lines.append(prevLine + line)
        #         prevLine = ""
        # lines = new_lines
        # text = "\n".join(lines)

        #############################################################################
        # https://github.com/SteffenEger/Corpus/blob/master/Additional_Corrections.py
        #############################################################################
        #
        # # applies some text normalization (not necessary and not working)
        #
        # def text_normalization(raw_data):
        #     word_list = []
        #     numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        #     sent_text = nltk.sent_tokenize(raw_data)
        #     for sent in sent_text:
        #         for word in nltk.word_tokenize(sent):
        #             if len(word) > 2 and word[0] in numbers and word[1] not in numbers:
        #                 word_list.append(word[0])
        #                 word_list.append(" ")
        #                 word_list.append(word[1:])
        #             else:
        #                 word_list.append(word)
        #         print(" ".join(word_list))
        #         word_list = []
        #
        #     return word_list
        #
        #
        # def sents_creation(data):
        #     sent_text = nltk.sent_tokenize(data)
        #     return sent_text

        idx_per_year[year] += 1
        if not os.path.isdir(f"data/1_collected/Reichstag/{year}/"):
            os.makedirs(f"data/1_collected/Reichstag/{year}/")
        with open(f"data/1_collected/Reichstag/{year}/{idx_per_year[year]}.txt", "w", encoding="utf-8") as file:
            file.write(text)
