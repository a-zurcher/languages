#!/bin/python3
import hashlib

import logging
import genanki
import argparse
import re
import csv

#################
# Logging #######
#################
logging.basicConfig(format='%(levelname)s | %(message)s', level=logging.INFO)


#################
# Arguments #####
#################
parser = argparse.ArgumentParser(
    description='This tools converts CSV files into deck of flashcards for Anki'
)

parser.add_argument(
    '-i', '--input',
    type=str,
    nargs='+',
    help='One or more CSV file(s), if filename contains "cloze", it will be treated as such '
         'flashcards',
    required=True
)

parser.add_argument(
    '-n', '--name',
    type=str,
    help='Name of the generated Anki pack',
    required=True
)

parser.add_argument(
    '-l', '--language',
    type=str,
    help='ISO code for the language, used for text to speech',
    required=False
)

args = parser.parse_args()

files: [str] = args.input
deck_name: str = args.name
deck_name_int_hash: int = int(
    hashlib.shake_256(deck_name.encode("utf-8")).hexdigest(7),
    16
)
language: str = args.language


#################
# Helper function
#################
def get_csv(filename: str, delimiter: str) -> [[str]]:
    csv_rows = []
    with open(filename, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')

        for csv_row in csv_reader:
            csv_rows.append(csv_row)

    return csv_rows


subject_pronouns = ["", "", "", "", "", ""]


def get_subject_functions() -> None:
    """Parses first line of csv containing verb conjugaison and adds it
    to subject_pronouns list"""
    for current_file in files:
        if re.match(pattern='.*verb.*csv', string=current_file):
            verb_csv = get_csv(filename=current_file, delimiter=';')

            if len(verb_csv[0]) != 6:
                logging.warning(f"First line of a verb conjugaison file should have exactly 6 fields '{current_file}'.")
                exit(1)

            # iterates the first line of the verb csv to get the 6 subject pronouns
            for i in range(0, len(subject_pronouns)):
                subject_pronouns[i] = verb_csv[0][i]


# has to be called before template definition
get_subject_functions()


#################
# Anki logic ####
#################
model_basic_and_reversed_with_tts = genanki.Model(
    1485830179,
    'Basic (and reversed card), with TTS',
    fields=[
    {
        'name': 'Front',
        'font': 'Arial',
    },
    {
        'name': 'Back',
        'font': 'Arial',
    },
    ],
    templates=[
    {
        'name': 'Card 1',
        'qfmt': '{{Front}}',
        'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}',
    },
    {
        'name': 'Card 2',
        'qfmt': '{{Back}}',
        'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}',
    },
    ],
    css='.card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white;}',
)

model_verbs = genanki.Model(
    1607392319,
    'Spanish verb Model',
    fields=[
        {'name': 'Infinitive'},
        {'name': 'Translation'},
        {'name': 'SingularFirst'},
        {'name': 'SingularSecond'},
        {'name': 'SingularThird'},
        {'name': 'PluralFirst'},
        {'name': 'PluralSecond'},
        {'name': 'PluralThird'}
    ],
    css='table, td {border: 1px solid;}'
        'table {border-spacing:0; margin:auto;}'
        'td {padding:.5rem;}',
    templates=[
        {
            'name': 'Verb conjugaison',
            'qfmt': '<p style="text-align:center;">{{Translation}}</p>',
            'afmt': """
            <p style="text-align:center;">{{Translation}}<hr id="answer"></p>
            <p style="text-align:center;"><b>{{Infinitive}}</b><span class="invisible">,</span></p>
            <div class="verb-tables">
                <table>
                    <tr>
                        <td tabindex="0">
                            <span class="pronoun">""" + subject_pronouns[0] + """</span> 
                            {{SingularFirst}}<span class="invisible">,</span>
                        </td>
                    </tr>
                    <tr>
                        <td tabindex="1">
                            <span class="pronoun">""" + subject_pronouns[1] + """</span> 
                            {{SingularSecond}}<span class="invisible">,</span>
                        </td>
                    </tr>
                    <tr>
                        <td tabindex="2">
                            <span class="pronoun">""" + subject_pronouns[2] + """</span> 
                            {{SingularThird}}<span class="invisible">,</span>
                        </td>
                    </tr>
                </table>
                <table>
                    <tr>
                        <td tabindex="0">
                            <span class="pronoun">""" + subject_pronouns[3] + """</span> 
                            {{PluralFirst}}<span class="invisible">,</span>
                        </td>
                    </tr>
                    <tr>
                        <td tabindex="1">
                        <span class="pronoun">""" + subject_pronouns[4] + """</span> 
                        {{PluralSecond}}<span class="invisible">,</span>
                        </td>
                    </tr>
                    <tr>
                        <td tabindex="2">
                        <span class="pronoun">""" + subject_pronouns[5] + """</span> 
                        {{PluralThird}}<span class="invisible">,</span>
                        </td>
                    </tr>
                </table>
            </div>
            <style>
                .invisible {opacity:0;}
                .pronoun {font-weight: 100;speak:none;}
                .verb-tables {display:flex; gap: 2rem; justify-content: center}
                .verb-tables table {margin: unset;}
            </style>
            """
        },
    ]
)
my_deck = genanki.Deck(
    deck_id=deck_name_int_hash,
    name=deck_name
)

logging.info(f"Files parsed: ['{"', '".join(files)}']")

for file in files:
    fields = 2

    if re.match(pattern=f".*cloze.*csv", string=file):
        logging.info(f"Cloze flashcards '{file}' detected")
        model = genanki.CLOZE_MODEL
    elif re.match(pattern=".*verb.*csv", string=file):
        logging.info(f"Verb conjugaison flashcards '{file}' detected")
        fields = 8
        model = model_verbs
    elif re.match(pattern=".*csv", string=file):
        model = model_basic_and_reversed_with_tts
    else:
        logging.critical(f"The format of the file '{file}' is not supported !")
        exit(1)

    csv_content = get_csv(filename=file, delimiter=';')

    for row in csv_content:
        # checks if there is two different fields for the current row
        if (len(row)) == fields:
            my_deck.add_note(
                genanki.Note(
                    model=model,
                    fields=row
                )
            )


#################
# Generate deck #
#################
genanki.Package(my_deck).write_to_file(f"{deck_name}.apkg")
logging.info(f"Anki deck file './{deck_name}.apkg' was generated")
