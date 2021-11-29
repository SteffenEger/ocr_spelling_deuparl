import collections
import glob
import os
import re
import tqdm

if __name__ == "__main__":

    bucket_folders = list(sorted(glob.glob("data/1_collected/Bundestag/*/")))

    count_per_bucket = collections.Counter()
    for bucket_folder in tqdm.tqdm(bucket_folders):
        bucket_name = int(bucket_folder[bucket_folder[:-1].rindex("/") + 1:-1])  # Bundestag -> bucket name is term number

        if not os.path.isdir(f"data/2_preprocessed/Bundestag/{bucket_name}/"):
            os.makedirs(f"data/2_preprocessed/Bundestag/{bucket_name}/")

        file_paths = list(sorted(glob.glob(bucket_folder + "*.txt")))

        for file_path in file_paths:
            print(file_path)
            with open(file_path, encoding="utf-8") as file:
                text = file.readlines()
                 
            # TODO: do the preprocessing here
            lines = text

            # Fix sentence being splited. They are mainly in parentheses. E.g
            #(Hello
            #Everyone)
            #->
            #(Hello Everyone)
            
            lines_fix, buffer = [], []
            for line in lines:
                if line[0] == '(' and line[-2:] != ')\n':
                    buffer.append(line[:-1])
                elif len(buffer) != 0 and line[-2:] != ')\n':
                    buffer.append(line[:-1])
                elif len(buffer) != 0 and line[-2:] == ')\n':
                    buffer.append(line[:-1])
                    lines_fix.append(" ".join(buffer))
                    buffer = []
                else:
                    lines_fix.append(line)
            lines = lines_fix

            ### ----------------------------------------------------------------
            ### Code from Tobi Walter
            start_patterns_bundestag = "|".join([
                "Ich eröffne die \d+ (\n )?Sitzung",
                "Ich eröffne die \d+.( |\n)Sitzung",
                "Mit einer ungewohnten Verspätung eröffne ich die 161.\nSitzung des Deutschen Bundestages.",
                "Die Sitzung wird um 16 Uhr 5 Minuten eingeleitet mit der Ouvertüre „Weihe des Hauses\", Opus 124 von Ludwig van Beethoven.",
                "Die \d+ (\n )?Sitzung des (Deutschen)? (Bundestages|Bundestags) ist eröffnet",
                "Die \d+.( |\n)?Sitzung des (Deutschen)? (Bundestages|Bundestags) ist eröffnet",
                "Ich erkläre die \d+ (\n )?Sitzung des (Deutschen )?(Bundestages|Bundestags) für eröffnet",
                "Ich erkläre die \d+.( |\n)Sitzung des (Deutschen )?(Bundestages|Bundestags) für eröffnet",
                "Die (\n )?Sitzung (\n )?ist (\n )?eröffnet",
                "Ich (\n )?eröffne (\n )?die (\n )?Sitzung",
                "Die      Sitzung ist eröffnet .",
                "Die Sit zung ist eröffnet.",
                "Die Sitzung ist damit eröffnet .",
                "Ich eröffne die erste Sitzung des Deutschen Bundestages",
                "Ich eröffne die 279. 'Sitzung ides Deutschen Bundestages.",
                "Beginn:? \d+ Uhr",
                "Beginn:? \d+. Uhr",
                "Beginn:? \d+.\d+ Uhr",
                "Beginn:? \d+ .\d+ Uhr",
                "Beginn:? \d+.\n\d+ Uhr",
                "Vizepräsident Dr. Schmid: Meine Damen und Herren, vor Eintritt in die Tagesordnung sind zwei Ergänzungsanträge zu bescheiden.",
                "Präsident Dr. Köhler: Meine Damen und Herren!\nIch erklare die 58.\nSitzung des Deutschen Bundestages fur eröffnet.",
                "Die Sitzung wird um \d+ Uhr \d+ Minuten durch den Vizepräsidenten Dr. Schmid eröffnet.",
                "Die Sitzung wird um \d+ Uhr \d+ Minute durch den Präsidenten D. Dr. Gerstenmaier eröffnet.",
                "Die Sitzung wird um \d+ Uhr \d+ Minuten durch die Alterspräsidentin Frau Dr. Dr. h. c. Lüders eröffnet.",
                "Die Sitzung wird um \d+ Uhr \d+ Minuten durch den Präsidenten D. Dr. Gerstenmaier eröffnet.",
                "Vizepräsident Dr. Schmid: Meine Damen und Herren!\nIch habe, vor Eintritt in die Tagesordnung für das Haus eine Erklärung abzugeben.",
                "Die Sitzung eröffnet.",
                "Vizepräsidentin Claudia Roth:  Guten Tag, liebe Kolleginnen und Kollegen!\nIch wün   sche Ihnen einen guten Tag in schweren Stunden, in de nen die Welt, glaube ich, nicht einfacher geworden ist .",
                "Die Sitzung ist      eröffnet.",
                "Ich eröffne als Alterspräsident die erste Sitzung der 19.",
                "Präsident Dr. Wolfgang Schäuble: Guten Tag, liebe Kollegen und Kolleginnen!",
                "Präsident Dr. Wolfgang Schäuble:\nGuten Morgen, liebe Kolleginnen und Kollegen!\nBitte nehmen Sie Platz.",
                "Vizepräsident Thomas Oppermann:\nGuten Tag, Kollegen und Kolleginnen!\nBitte nehmen Sie Platz.",
                "Die Sitzung ist eröffnet."
            ])

            end_patterns_bundestag = "|".join([
                "(Schluß|Schluss) der Sitzung \d+",
                "(Schluß|Schluss) der Sitzung:",
                "(Schluß|Schluss) der 'Sitzung:",
                "Die Sitzung ist geschlossen",
                "Die Sitzung ist 'geschlossen.",
                "ist die Sitzung geschlossen.",
                "Die \d+.\nSitzung ist geschlossen",
                "Sitzung des Deutschen Bundestages erkläre ich für geschlossen.",
                "und erkläre die heutige, die \d+.\nSitzung, für geschlossen.",
                "und schließe die Sitzung.",
                "schließe damit die Sitzung.",
                "Ich hebe die Sitzung auf.",
                "und schließe die heutige Sitzung.",
                "und   schließe die Sitzung.",
                "und schließe   die Sitzung.",
                "Ich schließe die (\n )?Sitzung",
                "Die nächste Sitzung berufe ich auf morgen, den 15. Februar 1990, 9 Uhr ein.",
                "Die Sitzung   ist geschlossen.",
                "Die Sitzung ist damit geschlossen.",
                "und hebe die   Sitzung damit auf.",
                "Die Sitzung ist aufgehoben.",
                "Damit ist die heutige Sitzung geschlossen.",
                "Die Sitzung ist hiermit geschlossen.",
                "Liebe Kolleginnen und Kollegen, die Sitzung ist ge schlossen.",
                "Die Sitzung ist damit geschlossen .",
                "Wir sind damit am Schluss unserer heutigen Tages ordnung .",
                "Wir sind damit am Schluss unserer heutigen Tagesord nung angekommen .",
                "Die   Sitzung ist geschlossen .",
                "Ich schließe hiermit die Sitzung.",
                "Wir sind damit am Schluss unserer heutigen Tages ordnung.",
                "Wir sind am Schluss der Tagesordnung.",
                "Die heutige Sitzung ist auf der Grundlage des gerade festgestellten Abstimmungsergebnisses aufgehoben.",
                "Aber ich darf Sie herzlich bitten, schon zur Feierstunde zum Frauenwahlrecht um 9 Uhr zu erscheinen, auch wenn das freiwillig ist."
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
                # If both patterns found, return only text between start and end indices of the matching objects
                if sitzung_end:
                    temp = temp[sitzung_start.start():sitzung_end.end()]
                # If only one of start/end patterns is found, discard all text before/after the found pattern.
                else:
                    temp = temp[sitzung_start.start():]
            elif sitzung_end:
                temp = temp[:sitzung_end.end()]
            
            ## Split string by new-line character to transform protocol back to line format
            #lines = temp.split(' \n ')
            lines = temp.split('\n')

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

            # replace digits
            #lines = [re.sub(r'\d+', ' ', line).strip() for line in lines]

            # remove double spaces
            lines = [re.sub('\s\s+', ' ', line).strip() for line in lines]

            # reduce numerical sequences
            lines = [re.sub(r'((0)\s?){2,}', '\\2 ', line).strip() for line in lines]

            # filter doc
            lines = [line for line in lines if len(line) > 1]

            # lowercase
            lines_tokens = [[tok.lower() for tok in line.split()] for line in lines]  # FINDME: do split() instead of lemmatization

            ### ----------------------------------------------------------------

            # rejoin token
            lines = [" ".join(tokens) for tokens in lines_tokens]

            count_per_bucket[bucket_name] += 1
            with open(f"data/2_preprocessed/Bundestag/{bucket_name}/{count_per_bucket[bucket_name]}.txt", "a", encoding="utf-8") as file:
                for line in lines:
                    file.write(line + "\n")             