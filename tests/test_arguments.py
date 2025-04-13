import main
import warnings

def test_arguments_passed_for_name_redaction():
    '''
    Tests for the arguments given via the command line
    '''
    warnings.filterwarnings("ignore")

    args = main.parse_arguments(['--input','resources/test3in.pdf','--output','myoutput/', '--names','Kent Jeffrey', '--stats', 'stats'])
    assert args.input == ['resources/test3in.pdf']
    assert args.output == 'myoutput/'
    assert args.names == ['Kent Jeffrey']
    assert args.stats == 'stats'

def test_arguments_passed_for_entity_redaction():
    '''
    Tests for the arguments given via the command line
    '''
    warnings.filterwarnings("ignore")

    args = main.parse_arguments(['--input','resources/test3in.pdf','--output','myoutput/', '--entities','PERSON', '--stats', 'stats'])
    assert args.input == ['resources/test3in.pdf']
    assert args.output == 'myoutput/'
    assert args.entities == ['PERSON']
    assert args.stats == 'stats'