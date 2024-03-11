#!/bin/python3

import genanki
import argparse
import re
import csv

#################
# Arguments #####
#################
parser = argparse.ArgumentParser(
    description='This tools converts CSV files into deck of flashcards for Anki'
)

parser.add_argument(
    "-i", "--input",
    type=str,
    nargs="+",
    help='One or more CSV file(s), if filename contains "cloze", it will be treated as such '
         'flashcards',
    required=True
)

parser.add_argument(
    "-n", "--name",
    type=str,
    help='Name of the generated Anki pack',
    required=True
)

args = parser.parse_args()

files = args.input
deck_name = args.name


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


#################
# Anki logic ####
#################
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
      'afmt': '<p style="text-align:center;">{{Translation}}</p>'
              '<p style="text-align:center;"><b>{{Infinitive}}</b><hr id="answer"></p>'
              '<table>'
              '<tr>'
                '<td>{{SingularFirst}}</td>'
                '<td>{{PluralFirst}}</td>'
              '</tr>'
              '<tr>'
                '<td>{{SingularSecond}}</td>'
                '<td>{{PluralSecond}}</td>'
              '</tr>'
              '<tr>'
                '<td>{{SingularThird}}</td>'
                '<td>{{PluralThird}}</td>'
              '</tr>'
              '</table>'
    },
  ])
my_deck = genanki.Deck(
    deck_id=2059400110,
    name=deck_name
)

print(f"Files parsed: {", ".join(files)}")
for file in files:
    fields = 2

    if re.match(pattern=f".*cloze.*csv", string=file):
        print(f"{file} detected to contain cloze flashcards.")
        model = genanki.CLOZE_MODEL
    elif re.match(pattern=".*verb.*csv", string=file):
        print(f"{file} detected to contain verb conjugaison flashcards.")
        fields = 8
        model = model_verbs
    elif re.match(pattern=".*csv", string=file):
        model = genanki.BASIC_AND_REVERSED_CARD_MODEL
    else:
        print(f"Error ! The format of the file \"{file}\" is not supported.")
        exit(1)

    csv_content = get_csv(filename=file, delimiter=";")

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
genanki.Package(my_deck).write_to_file(f'{deck_name}.apkg')
print(f"Anki deck file {deck_name}.apkg was generated")
