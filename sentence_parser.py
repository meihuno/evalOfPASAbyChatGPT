import spacy

class SentenceParser(object):

    def __init__(self):
        model = 'ja_ginza'
        self.nlp = spacy.load(model)
        print(f"load {model} done.")

    def ret_case_elem_dict(self, sentence):
        pass

    def parse(self, sentence):

        def _check_case(token):
            if token.dep_ == 'nsubj' or token.dep_ == 'obj' or token.dep_ == 'obl':
                return True
            else:
                return False

        def _ret_gr(cstr):
            if cstr == 'nsubj':
                return '主語'
            elif cstr == 'obj':
                return '目的語'
            elif cstr == 'obl':
                return 'ニ格'
            else:
                return 'Other'
        
        doc = self.nlp(sentence)
        compound_info_dict = {}
        
        for sent in doc.sents:
            dep_dict = {}
            for token in sent:
                hidx = token.head.i
                if _check_case(token) == True:
                    if not hidx in dep_dict:
                        dep_dict[hidx] = {'nsubj':[], 'obj': [], 'obl': []}
                    dep_dict[hidx][token.dep_].append(token.i)
        
            rdict = {}
            for pred_idx, case_dict in dep_dict.items():
                pred = sent[pred_idx].text
                if not pred in rdict:
                    rdict[pred] = {'主語':[], '目的語': [], 'ニ格': []}
                for cstr, tidx_list in case_dict.items():
                    gr = _ret_gr(cstr)
                    for tidx in tidx_list:
                        tstr = sent[tidx].text
                        rdict[pred][gr].append(tstr)

            return rdict


    def ret_case_elem_dict(self, sentence, pred):
        # print([l, pred])
        case_line = l[0]
        case_dict = {'主語': [], '目的語': [], 'ニ格':[ ] }
        for elem in case_line.split('、'):
            subj_match = re.findall('(.*)が$', elem)
            obj_match = re.findall('(.*)を$', elem)
            obl_match = re.findall('(.*)に$', elem)
            if subj_match:
                case_dict['主語'].append(subj_match[0])
            elif obj_match:
                case_dict['目的語'].append(obj_match[0])
            elif obl_match:
                case_dict['ニ格'].append(obl_match[0])
        return case_dict

if __name__=="__main__":
    box = SentenceParser()
    box.parse("")