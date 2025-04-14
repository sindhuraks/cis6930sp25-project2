import main
import os
import pymupdf
import spacy
import warnings

def test_name_redaction_in_pdf():

    warnings.filterwarnings("ignore")
    spacy.load('en_core_web_trf')
    doc = pymupdf.open('resources/test3in.pdf')
    names = ['Kent Jeffrey']
    output_dir = 'output'
    fname = 'test3in.pdf'
    stats = 'stats'
    coref = '1'
    os.makedirs(output_dir, exist_ok=True)
    main.redact_name_in_pdf(doc, names, output_dir, fname, stats, coref)
    assert os.path.exists(output_dir+'/'+fname)