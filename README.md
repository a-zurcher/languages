# Languages

Python script and vocabulary files to generate [Anki flashcards](https://apps.ankiweb.net/). 

## Usage

1. Install the required python libraries:
   ```commandline
   pip install -r requirements.txt
   ```
2. Generate the Anki deck:
    ```commandline
    python3 csv_to_anki.py -i spanish/*.csv -n Spanish
    ```
3. You can then import the generated `.apkg` file into Anki.