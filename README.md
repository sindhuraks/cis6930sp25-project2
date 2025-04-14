# cis6930sp25-project2

Name: Sindhura Kumbakonam Subramanian

## Assignment Description

The aim of this project is to build a python function that redacts sensitive information i.e. named entities from a set of pdf documents. This project will take the following parameters : input file globs, output directory where redacted pdf files will be saved, names or person entities, a coref flag that will redact coreferences for a given named entity, stats file directory that will hold the metadata of the redacted entity. For a given set of pdf documents given via the input parameter, either names or PERSON entities and its corresponding coreferences will be redacted (a colored, opaque rectangle across the entity) from the input file if the entities are present and the redacted pdf will be saved to the output directory path mentioned in the output parameter. Additionally, a stats will be generated (specified by the stats parameter) which will contain the details about the entity such as from which file it was redacted, name, length and type of entity and in which page the entity was found.

## Installing models

This project requires 3.10 as the version of Python to be used (3.10.16 was used for this project).

1. Create a python project using : `uv init .`, create a virtual environment using `uv venv` and activate the environment using `source .venv/bin/activate`.

2. Install the following packages using `uv add` to add the packages to the pyptoject.toml file:
    - uv add --no-cache pip setuptools wheel pymupdf spacy-experimental tqdm
    - uv run -m spacy download en_core_web_sm
    - uv run -m spacy download en_core_web_trf
    - uv add numpy==1.26.4 (to avoid numpy versioning issues)
    - uv add pytest
    - uv add 'thinc[torch]'
    - uv pip install https://github.com/explosion/spacy-experimental/releases/download/v0.6.1/en_coreference_web_trf-3.4.0a2-py3-none-any.whl

## How to run

1. uv run python main.py --input "resources/test3in.pdf" --output myoutput --names "Kent Jeffrey" --stats stats
2. uv run python main.py --input "resources/test1*" --output myoutput --entities "PERSON" --stats stats
3. uv run python main.py

## Example
![alt text](example.gif)


## Features and functions

#### main.py

1. parse_arguments(sys_args=None) - this function takes sys_args defaulted to None as an argument and parses the arguments given via the command line and returns the input file globs, output file directory, names or entities, coref flag, stats file directory. Throws an error if neither names nor entities are given or the stats file directory is not given.

2. get_input_files(ip_files) - this function takes the input files as globs and returns the file names to be redacted in the ascedning order.

3. process_input_files(files, names, entities, coreferences,output_dir, stats) - this function takes the list of files, loops over the files, opens each pdf file and for every page in the pdf, calls either redact_name_in_pdf if names were given or redact_entities_in_pdf if entities were given along with their coreferences and the output and stats directory where the redacted files and statistics needs to be saved.

4. mark_word(page, text) -  this function returns the page numbers in which the named entity to be redacted was found.

5. redact_name_in_pdf(doc,names,output_dir,file, stats, coreferences) - this function takes the opened pdf document, loops over every page in the document, loops over names (in case multiple names were given), finds the page numbers where the names were found via mark_word function, gets the rectangular cooridnates for every named instances and using these coordinates, annotates the entity using black color using fill parameter in add_redact_annot method and increments the instances found count. The redactions are applied and the output pdf with redacted text is generated iff the instances count is > 0 (no need to generate a pdf file if the name was not found in the pdf). Additionally, with the page numbers found via mark_word function, redact_coreferences_in_pdf method is called to redact the corresponding coreferences for the name.

6. redact_entities_in_pdf(doc, entities, output_dir,fname, stats, coreferences) - this function loads the en_core_web_trf model, takes the opened pdf document, loops over every page in the document, loops over PERSON entities, finds the page numbers where the entities were found via mark_word function, gets the rectangular cooridnates for every named entity instances and using these coordinates, annotates the entity using blue color using fill parameter in add_redact_annot method and increments the instances found count. The redactions are applied and the output pdf with redacted text is generated iff the instances count is > 0 (no need to generate a pdf file if the name was not found in the pdf). Additionally, with the page numbers found via mark_word function, redact_coreferences_in_pdf method is called to redact the corresponding coreferences for the named entity.

7. redact_coreferences_in_pdf(text, page, name) - this function loads the pretrained model for coreference : en_coreference_web_trf, splits the text into chunks of size 512, splits the named entity if len of the entity is greater than 1, gets the first and last name, checks if these names are present in the coref clusters and if present gets the remaining entity values from the list as coreferences, annotates and redacts the text in red color.

8. write_metadata(fname, name, type, page) -  this function takes the filename, name and type of the entity and the page number, writes these details to a tsv file.

9. chunk_text(text, chunk_size = 512) - this function takes the text in the pdf document and returns a chunked text of size 512 in order to avoid `Token indices sequence length is longer than the specified maximum sequence length for this model (580 > 512). Running this sequence through the model will result in indexing errors` returned by en_coreference_web_trf model.

10. main() - this function is the main entry point which parses the command line arguments; processes the pdf files and saves the redacted pdf file to the mentioned path. The processing happens if and only if the input file globs and output directory is given; either names or entitities and the stats file path is mandatory. Otherwise, throws an error to the console stating how the file should be run. If no entity is given via the entities argument, it is defaulted to PERSON. If coref flag is left blank, defaulted to '1'.

## Bugs and Assumptions

### Assumptions

1. While performing coreference redaction of names or named entities, if the name consists of a first and last name like Kent Jeffrey, then we get the first and the last name stored in fname and lname and check if these are present in the coref cluster returned by doc.spans. If present, for example [Mr. Kent Jeffrey, Mr. Jeffrey, you, your], the coreferences for this example is you, your which is retrived from the list and redaction is performed for these. The coreference redaction highly depends upon the coref clusters returned by the en_coreference_web_trf model.

2. When attempting to do named entity redaction using entities flag, "PERSON" is used. Named entity redaction using entities flag entirely depends upon the values returned by the model and redactions are done based on these values.

### Bugs

1. The pdfs used for testing has scanned pages of different fonts. The model does not recognize some of these fonts and if there are any names or entities that needs to be redacted present in these font styles, redaction will not be done. The same goes for coreference redaction as well. Even if the model redacts the entities for a font, it does not redact the coreference for that font style.