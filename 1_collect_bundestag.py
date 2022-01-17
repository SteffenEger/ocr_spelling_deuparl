import glob
import os
from xml.etree import ElementTree
from natsort import natsorted
import tqdm

if __name__ == "__main__":

    #####################################################
    # https://github.com/SteffenEger/bundestagsprotokolle
    #####################################################

    bucket_folders = list(sorted(glob.glob("data/source/Bundestag/*/")))

    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[bucket_folder[:-1].rindex("/") + 1:-1])  # Bundestag -> bucket name is term number

        file_paths = list(natsorted(glob.glob(bucket_folder + "*.xml")))

        if not os.path.isdir(f"data/1_collected/Bundestag/{bucket_name}/"):
            os.makedirs(f"data/1_collected/Bundestag/{bucket_name}/")

        if bucket_name != 19:

            for idx, file_path in enumerate(file_paths):

                ##################################################################################################
                # source: https://github.com/SteffenEger/bundestagsprotokolle/blob/master/Bundestag_XML_Parsing.py
                ##################################################################################################

                lines = []
                with open(file_path, encoding="utf-8") as file:
                    root = ElementTree.parse(file).getroot()
                    # extracting all information
                    for line in root.iter():
                        lines.append(line.text)

                ################################################################################################
                # source: https://github.com/SteffenEger/bundestagsprotokolle/blob/master/Concatenating_sents.py
                ################################################################################################

                # concatenates sentences based on "-"

                res = []
                prevLine = ""

                for i in range(0, len(lines)):
                    if i < len(lines) - 1 and len(lines[i]) > 1 and not lines[i].endswith(" -") and lines[i][-1] == '\n' and lines[i][-2] == '-' and lines[i + 1][0].islower():
                        prevLine = prevLine + lines[i][:-2]
                    elif i < len(lines) - 1 and len(lines[i]) > 1 and not lines[i].endswith(" -") and lines[i][-1] == '\n' and lines[i][-2] == '-' and lines[i + 1][0].isupper():
                        prevLine = prevLine + lines[i][:-1]
                    elif i < len(lines) - 2 and len(lines[i]) > 1 and not lines[i].endswith(" -") and lines[i][-1] == '\n' and lines[i][-2] == '-' and lines[i + 1][0].islower() and lines[i + 2][0].islower():
                        prevLine = prevLine + lines[i][:-2]
                    elif i < len(lines) - 2 and len(lines[i]) > 1 and not lines[i].endswith(" -") and lines[i][-1] == '\n' and lines[i][-2] == '-' and lines[i + 1].startswith('\n') and lines[i + 2][0].islower():
                        prevLine = prevLine + lines[i][:-2]
                    elif lines[i].startswith('\n'):
                        res.append("")
                    else:
                        res.append(prevLine)
                        res.append(lines[i])
                        prevLine = ""

                lines = res

                ##################################################################################################
                # source: https://github.com/SteffenEger/bundestagsprotokolle/blob/master/Tokenizing_into_sents.py
                ##################################################################################################
                #
                # # uses nltk sentence tokenization so that one line is one sentence
                # # better do this in postprocessing after OCR post-correction and spelling normalization
                #
                # sentences = nltk.sent_tokenize(" ".join(lines), language="german")
                # lines = sentences

                text = "\n".join(lines)

                with open(f"data/1_collected/Bundestag/{bucket_name}/{idx + 1}.txt", "w", encoding="utf-8") as file:
                    file.write(text)

        else:  # session 19

            for idx, file_path in enumerate(file_paths):

                #######################################################################################
                # source: https://github.com/SteffenEger/bundestagsprotokolle/blob/master/19_Periode.py
                #######################################################################################

                lines = []
                with open(file_path, encoding="utf-8") as file:
                    root = ElementTree.parse(file).getroot()
                    for line in root.iter():
                        if line.text != None and line.tag != 'seite' and line.tag != 'seitenbereich':
                            if line.tag == 'vorname' or line.tag == 'name' or line.tag == 'vorname' or line.tag == 'titel' or line.tag == 'fraktion':
                                if lines == []:
                                    lines.append(line.text + " ")
                                else:
                                    lines[-1] += line.text + " "
                            else:
                                if lines == []:
                                    lines.append(line.text)
                                else:
                                    lines[-1] += line.text
                                lines.append("")

                if lines != [] and lines[-1] == "":
                    lines = lines[:-1]

                #############################################################################################
                # source: https://github.com/SteffenEger/bundestagsprotokolle/blob/master/19_Periode_Sents.py
                #############################################################################################
                #
                # # uses nltk sentence tokenization so that one line is one sentence
                # # better do this in postprocessing after OCR post-correction and spelling normalization
                #
                # sentences = nltk.sent_tokenize("\n".join(lines), language="german")
                # lines = sentences

                text = "\n".join(lines)

                with open(f"data/1_collected/Bundestag/{bucket_name}/{idx + 1}.txt", "w", encoding="utf-8") as file:
                    file.write(text)
