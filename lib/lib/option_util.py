from argparse import ArgumentParser

def get_eval_option():
    argparser = ArgumentParser()
    argparser.add_argument('-p', '--process', type=str,
                           default='evaluation',
                           help='evaluation or analysis or knp or extra')
    argparser.add_argument('--kt', '--knp-type', type=str,
                           default='anaphora',
                           help='knp type')
    argparser.add_argument('--td', '--target-dir', type=str,
                           default='./result/dev4/',
                           help='path of directory containing eval json files')    
    argparser.add_argument('--verbose', '--verbose-flag', type=str,
                           default='no',
                           help='yes or no')
    return argparser.parse_args()

def get_chat_option():
    argparser = ArgumentParser()
    argparser.add_argument('--asyn', '--asyncc', type=str,
                           default='yes',
                           help='async yes or not')
    argparser.add_argument('--okd', '--existing-ok-dir', type=str,
                           default='./result/dev4/',
                           help='path of directory containing eval json files')
    argparser.add_argument('--otd', '--output-target-dir', type=str,
                           default='./result/dev4/',
                           help='path of directory containing eval json files')
    argparser.add_argument('--model', '--model-name', type=str,
                           default='gpt-3.5-turbo',
                           help='model_name')
    argparser.add_argument('--pt', '--prompt-type', type=str,
                           default='gogo',
                           help='extra or gogo')
    argparser.add_argument('--limit', '--sample-limit', type=int,
                           default=1000,
                           help='sampling limit. default is 1000.')
    argparser.add_argument('--penv', '--process-environment', type=str,
                           default='local',
                           help='local or colab')
    argparser.add_argument('--sampling', '--sampling-type', type=str,
                           default='phase',
                           help='phase or sample5')
    argparser.add_argument('--skip', '--skip-process', type=str,
                           default='yes',
                           help='skip processing. yes or no')
    return argparser.parse_args()

def get_parse_option():
    argparser = ArgumentParser()
    argparser.add_argument('-p', '--process', type=str,
                           default='parse',
                           help='parse or test_data')
    argparser.add_argument('--knppat', '--knp-file-pattern', type=str,
                           default='./workplace/knp/*/*.knp',
                           help='search pattern for knp files')
    argparser.add_argument('--od', '--output-dir', type=str,
                           default='./intermediate_data/',
                           help='output directory')
    argparser.add_argument('--depfile', '--knp-dep-filename', type=str,
                           default='knp_ana2.json',
                           help='filename for bunsetsu dep info')
    argparser.add_argument('--predfile', '--knp-pred-filename', type=str,
                           default='knp_pred_ana2.json',
                           help='filename for pred info')
    return argparser.parse_args()