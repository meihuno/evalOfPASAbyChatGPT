from argparse import ArgumentParser

def get_eval_option():
    argparser = ArgumentParser()
    argparser.add_argument('-p', '--process', type=str,
                           default='evaluation',
                           help='evaluation or analysis')
    return argparser.parse_args()

def get_parse_option():
    argparser = ArgumentParser()
    argparser.add_argument('-p', '--process', type=str,
                           default='parse',
                           help='parse or test_data')
    return argparser.parse_args()