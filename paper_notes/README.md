Experiments - Preprocessing - Reichstag

A comparison between short and long lines on the basis of a law from the year 1877. The original file has 228 lines, the file with short lines keeps this and the file with long lines comes now on 73. The file with long lines has a maximum line length of 299 characters and starts a new line after each point, here 44 changes were made by OCR and Spelling Normalization, 39 were correct and five of them were errors, among other things two char sequences under the length of six characters were removed, the word "Vornahmen" was changed to "Vorname" and the word "Ereigniß" was mapped to "Ergniß". The file with short lines only reassembles separated words at the end of the line. Here 43 changes were made, of which three were errors, among other things char sequences were deleted again, this time only with a maximum length of two characters. With short lines three errors were not made, which were made with long lines, one error in the original file more was found and correctly changed and only one new error was made.  

References:
_________________________________________________
 /     | original               | OCR & Spelling Normalization
 short | short-lines_1877_1.txt | short-lines_1877_1_out.txt
 long  | long-lines_1877_1.txt  | long-lines_1877_1_out.txt
_________________________________________________

Quantitative Evaluation - Preprocessing - OCR - Spelling Normalization

From a short test passage of a transcript of a Reichstag session from 1880. The text passage has 143 lines at the end of the pipeline and starts from line number 3846.

_______________________________________________________________________
Error type                        | Frequency                          |
----------------------------------|------------------------------------|
Preprocessing                     |                                    |
Number in a wrong line            |      3                             |
Lists with wrong structure        |      1                             |
Header in text                    |      1                             |
no space between Word and Number  |      1                             |
----------------------------------|------------------------------------|
OCR                               |                                    |
Z -> I                            |     41                             |
Or. -> Dr.                        |      1                             |
Numbers                           |      1                             |
----------------------------------|------------------------------------|
Spelling Norm                     |                                    |
Th -> t correctly                 |     43                             |
Th -> t erroneously               |      3                             |
§ correctly detected              |      1                             |
upper/lower correctly             |      1                             |
“ieren” ending                    |      3                             |
ß -> ss,s correctly               |     19                             |
ß -> ss,s erroneously             |      2                             |
Ue -> Ü correctly                 |      1                             |
----------------------------------|------------------------------------|
Deletet character sequences       |                                    |                   
characters correctly deleted      |      8                             |
characters erroneously deleted    |     11                             |
spaces erroneously deleted        |     13                             |


References:
1-1880-data-collection.txt
1-1880-preprocessing.txt
1-1880-ocr-spelling.txt


