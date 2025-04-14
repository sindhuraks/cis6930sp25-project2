import argparse
import glob
import os
import pymupdf
import spacy
import sys

def parse_arguments(sys_args = None):

    '''
    Parses the arguments given via the command line
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,action='append',help='Input files globs')
    parser.add_argument('--output', type=str, required=True,help='Output directory for pdf files')
    parser.add_argument('--names', type=str, required=False,action='append',help='Takes one or more case sensitive tokens as input')
    parser.add_argument('--entities', type=str, required=False,action='append',help='Get all named entities',nargs='?', const='')
    parser.add_argument('--coref', type=str, required=False,help='Redact all coreferences',nargs='?', const='')
    parser.add_argument('--stats', type=str, required=False,help='Specify the location of the stats file')
    
    arguments = parser.parse_args(sys_args)

    # throw an error if neither a name nor entity is defined and stats argument is not given
    if not(arguments.names or arguments.entities) or not(arguments.stats):
        parser.print_help(sys.stderr)
    
    return arguments


def get_input_files(ip_files):

    '''
    Returns the set of input files in a directory in ascending order
    '''

    pdf_files = set()
    for file in ip_files:
        for name in glob.glob(file):
            pdf_files.add(name)
    
    return sorted(pdf_files)

def process_input_files(files, names, entities, coreferences,output_dir, stats):

    '''
    Processes the input files and redacts either names or entities depeding on the flag passed
    '''

    # perform redactions for the files given as input
    for file in files:
        fname = file.split('/')[1] # get the file name (eg: resources/test1in.pdf => test1in.pdf)
        doc = pymupdf.open(file) # open the file
        # if names flag was given, redact the names
        if names:
            redact_name_in_pdf(doc, names, output_dir, fname, stats,coreferences) 
        # if entities flag was given, redact the entities and its corresponding coreferences
        elif entities:
            redact_entities_in_pdf(doc, entities, output_dir,fname, stats, coreferences)

def mark_word(page, text):

    '''
    Returns the page number where the name/ entity was found
    '''

    found = 0
    page_nos = []
    wlist = page.get_text("blocks")  # make the word list
    for w in wlist:  # scan through all words on page
        if text in w[4]:  # w[4] is the word's string
            page = str(page)
            page = page.split(' ')
            page_no = page[1]
            page_nos.append(int(page_no))
            found += 1 
            break

    return found, page_nos

def redact_name_in_pdf(doc,names,output_dir,file, stats, coreferences):

    '''
    Redacts the name, its corresponding coreferences and saves the redacted pdf file to the output directory
    '''

    instances_found = 0
    is_entity = False
    
    for page in doc: # iterate over all the pages in the document
        for name in names: # iterate over all names
            found , page_nos= mark_word(page, name)
            if found:
                text = page.get_text()
                if coreferences:
                    redact_coreferences_in_pdf(text, page, name, is_entity)
            instances = page.search_for(name) # returns the rectangular instances of the names
            for instance in instances:
                page.add_redact_annot(instance, fill=(0,0,0))
                instances_found += 1
            if stats:
                type = 'Name'
                write_metadata(file,name, type, page_nos, stats)

        page.apply_redactions()

    if instances_found > 0: # save the redacted file iff the instances were redacted
        output_filename = output_dir+'/'+file
        doc.save(output_filename)

def redact_entities_in_pdf(doc, entities,output_dir,file, stats,coreferences):

    '''
    Redacts the PERSON entities, its corresponding coreferences and saves the redacted pdf file to the output directory
    '''

    if entities:
        instances_found = 0
        is_entity = True
        nlp = spacy.load('en_core_web_trf')

        for page in doc:
            text = page.get_text()
            docx = nlp(text)

            for ent in docx.ents:
                if ent.label_ in entities:
                    instances = page.search_for(ent.text)
                    for instance in instances:
                        page.add_redact_annot(instance, fill=(0,0,1))
                        instances_found += 1
                    found, page_nos = mark_word(page, ent.text)
                    if found:
                        ent_text = page.get_text()
                        if coreferences:
                            redact_coreferences_in_pdf(ent_text, page, ent.text, is_entity)
                        if stats:
                            type = 'Entity'
                            name = ent.text
                            if name is not None:
                                write_metadata(file,name,type, page_nos)
        
            page.apply_redactions()
    
    if instances_found > 0:
        output_filename = output_dir+'/'+file
        doc.save(output_filename)

def chunk_text(text, chunk_size = 512):
     
     return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def redact_coreferences_in_pdf(text, page, name, is_entity):

    '''
    Redacts the coreferences for the named entities
    '''

    nlp = spacy.load("en_coreference_web_trf")
    corefs = []

    name = name.split(' ')
    if len(name) > 1:
        fname = name[0]
        lname = name[len(name) - 1]

    chunked_text = chunk_text(text)

    for chunk in chunked_text:

        doc = nlp(chunk)

        clusters = [
            val for key, val in doc.spans.items() if key.startswith("coref_cluster")
        ]
    
        # add annotation for the coreferences of the corresponding named entities
        for cluster in clusters:
            if len(name) > 1:
                if fname in [token.text for span in cluster for token in span] or lname in [token.text for span in cluster for token in span]:
                    coreferences_to_redact = [span for span in cluster if name not in [token.text for token in span]]
                    for coref in coreferences_to_redact:
                        if fname in str(coref) or lname in str(coref):
                            continue
                        corefs.append(coref)

                    for span in corefs:
                        for token in span:
                            wlist = page.get_text("words", delimiters=None)
                            for word in wlist:
                                if token.text in word[4]:
                                    r = pymupdf.Rect(word[:4])
                                    page.add_redact_annot(r, fill=(1,0,0))
            else:
                if any(name[0] in token.text for span in cluster for token in span):
                    coreferences_to_redact = [span for span in cluster if name not in [token.text for token in span]]
                    for coref in coreferences_to_redact:
                        if name[0] in str(coref):
                            continue
                        corefs.append(coref)

                    for span in corefs:
                        for token in span:
                            wlist = page.get_text("words", delimiters=None)
                            for word in wlist:
                                if token.text in word[4]:
                                    r = pymupdf.Rect(word[:4])
                                    page.add_redact_annot(r, fill=(1,0,0))

def write_metadata(fname, name, type, page, stats):

    '''
    Writes the filename, page number where the redacted text is found, name, length and type of the token
    and returns the file with theese data
    '''

    # create a directory if it does not exist
    if not os.path.exists(stats):
        os.makedirs(stats)

    metadata = [{'Column Name':'File', 'Description':'The name of the file','Example':fname},
                {'Column Name':'Location', 'Description':'The location of the token redacted file','Example':str(page)},
                {'Column Name':'Token', 'Description':'The token redacted','Example':name},
                {'Column Name':'Length', 'Description':'The length of the token redacted','Example':str(len(name))},
                {'Column Name':'Type', 'Description':'The type of token redacted','Example':type},

    ]

    with open(stats+'/'+'new_file.tsv', 'a', newline='') as tsvfile:
        for pno in page:
            for row in metadata:
                if row['Column Name'] == 'Location':
                    row['Example'] = str(pno+1)
                cell_values = row.values()
                line = "\t".join(cell_values) + '\n'
                tsvfile.write(line)

def main():
    
    args = parse_arguments()
    if not(args.entities): # if no entity is given, then the default is PERSON
        args.entities = 'PERSON'
    
    if not(args.coref):
        args.coref = '1'
    files = get_input_files(args.input)
    if args.names or (args.entities or args.coref):
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        process_input_files(files,args.names,args.entities, args.coref,args.output, args.stats)


if __name__ == "__main__":
    main()