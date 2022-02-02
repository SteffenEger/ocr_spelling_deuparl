import collections
import glob
import os
from xml.etree import ElementTree
from natsort import natsorted
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

        file_paths = list(natsorted(glob.glob(bsb_folder + "xml/*.xml")))

        idx_per_year[year] += 1
        if not os.path.isdir(f"data/1_collected/Reichstag/{year}/"):
            os.makedirs(f"data/1_collected/Reichstag/{year}/")


        if os.path.isfile(f"data/1_collected/Reichstag/{year}/{idx_per_year[year]}.txt"):
            continue
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
                    s.append(char_param.text)
                lines.append("".join(s))

        text = "\n".join(lines)

        with open(f"data/1_collected/Reichstag/{year}/{idx_per_year[year]}.txt", "w", encoding="utf-8") as file:
            file.write(text)