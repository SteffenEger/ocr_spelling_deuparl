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
