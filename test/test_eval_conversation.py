import unittest
import pprint as pp
import json
from eval_conversation import EvalConversation
import lib.eval_util_evaluation as eval_util_evaluation
import lib.eval_util_string_match as eval_util_string_match

class TestEvalConversation(unittest.TestCase):

    def setUp(self):
        self.box = EvalConversation()
        self.dirname = './test/chatgpt_testdata/'

        json_open = open('./test/data/knp_pred1.json', 'r')
        self.knp_pred_dict = json.load(json_open) 

        json_open = open('./data/train_test_id.json', 'r')
        self.train_test_id_dict = json.load(json_open)  

        # json_open = open('./sample_data/sample2.json', 'r')
        json_open = open('./test/data/org_for_test.json', 'r')
        self.org_dict = json.load(json_open) 

        dirname = './test/chatgpt_testdata/'
        phase = 'dev'
        ok_pred_content_dict, result_compose_dict = self.box.ret_result_dict_series(dirname)
        self.conversation = ok_pred_content_dict['unit-test']['w201106-0000060050']
        # w201106-0000060050
        self.org_one_dict = self.org_dict['w201106-0000060050']
        self.knp_pred = self.knp_pred_dict['w201106-0000060050']


    def test__ret_match_type(self):
        
        cstr = '著者'
        gpt_str = '筆者'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'author')
        
        cstr = '筆者'
        gpt_str = '著者'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'author')

        # ChatGPTの「-」は出力と見做さない
        cstr = '筆者'
        gpt_str = '-'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'not_match')

        # ChatGPTの「」（空白）は出力と見做さない
        cstr = '筆者'
        gpt_str = ''
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'not_match')

        # 一致
        cstr = '筆者'
        gpt_str = '筆者'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'match')

        # 一方が他方を包含
        cstr = 'NekoNeko'
        gpt_str = 'とてもNekoNekoYes'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'gpt_long')

        # 一方が他方を包含
        cstr = 'とてもNekoNekoYes'
        gpt_str = 'NekoNeko'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'crr_long')

        # 前方完全一致
        cstr = '定めの小'
        gpt_str = '定めの小判'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'gpt_start_with_crr')
  
        # 前方完全一致
        cstr = '定めの小判'
        gpt_str = '定めの小'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'crr_start_with_gpt')

        # 前方一致
        cstr = '定めの小判'
        gpt_str = '定めの小Neko'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'head_match')

        # 前方一致
        cstr = '定めの小Neko'
        gpt_str = '定めの小小判'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'head_match')

        # 部分一致
        cstr = 'ABC共通文字列を持つEFG'
        gpt_str = 'YYY共通の文字列を持つZZZ'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'part_match')

        # 先頭の漢字が一致し、ひらがなが続
        cstr = '呼ばれる。'
        gpt_str = '呼ぶ'
        type1 = eval_util_string_match.ret_match_type(cstr, gpt_str)
        self.assertEqual(type1, 'head_kanji_match')

        
    def test_ret_content_dict2(self):

        dirname = './test/chatgpt_response/'
        phase = 'dev'
        ok_pred_content_dict, result_compose_dict = self.box.ret_result_dict_series(dirname)
        
        conversation = ok_pred_content_dict['zero-shot-simple']['w201106-0002000000']
        # w201106-0000060050

        json_open = open('./intermediate_data/knp_pred1.json', 'r')
        knp_pred_dict = json.load(json_open) 

        json_open = open('./data/train_test_id.json', 'r')
        train_test_id_dict = json.load(json_open)  

        # json_open = open('./sample_data/sample2.json', 'r')
        json_open = open('data/org.json', 'r')
        org_dict = json.load(json_open) 

        org_one_dict = org_dict['w201106-0002000000']
        knp_pred = knp_pred_dict['w201106-0002000000']

        case_lines = self.box.parse_conversation(org_one_dict, conversation)
        count_dict1 = self.box.ret_count_dict(knp_pred, org_one_dict, case_lines)
        eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(count_dict1)
        
        crr_count_dict = {
            'zero-shot-simple': 
            {'all': {'cnum': 12, 'csout': 2, 'sout': 7},
                'obj': {'cnum': 3, 'csout': 2, 'sout': 2},
                'obl': {'cnum': 2, 'csout': 0, 'sout': 2},
                'subj': {'cnum': 7, 'csout': 0, 'sout': 3},
                'pred': {'cnum': 6, 'csout': 3, 'sout': 3}
            }
        }

        for case1, count_num_dict in count_dict1.items():
            for count_type, num in count_num_dict.items():
                crr_num = crr_count_dict['zero-shot-simple'][case1][count_type]
                self.assertEqual(num, crr_num)
        # case_lines = self.box.parse_conversation(self.org_one_dict, self.conversation)

    def test_ret_content_dict(self):
        
        case_lines = self.box.parse_conversation(self.org_one_dict, self.conversation)
        count_dict1 = self.box.ret_count_dict(self.knp_pred, self.org_one_dict, case_lines)
        
        eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(count_dict1)

        # box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict, phase)
        for key, score_dict1 in eval_result_dict.items():
            f1_score = score_dict1['f1_score']
            self.assertEqual(f1_score, 1.0)

    def test_ret_detail_content_dict(self):
        
        case_lines = self.box.parse_conversation(self.org_one_dict, self.conversation)
        
        # print(lcount)
        detail_count_dict1 = self.box.ret_detail_count_dict(self.knp_pred, self.org_one_dict, case_lines)
        
        pp.pprint(detail_count_dict1)
        eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(detail_count_dict1)

        # box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict, phase)
        for key, score_subdict in eval_result_dict.items():
            for cstr, score_dict1 in score_subdict.items():
                f1_score = score_dict1['f1_score']
                # 正解があればF値1.0、なければF値0.0のテスト
                if detail_count_dict1[key][cstr]['cnum'] == 0:
                    self.assertEqual(f1_score, 0.0)
                else:
                    self.assertEqual(f1_score, 1.0)
        

    def test_eval_result_dict(self):
        count_dict = {
            'dep': {'all': {'cnum': 6, 'csout': 6, 'sout': 6},
                    'obj': {'cnum': 3, 'csout': 3, 'sout': 3},
                    'obl': {'cnum': 1, 'csout': 1, 'sout': 1},
                    'subj': {'cnum': 2, 'csout': 2, 'sout': 2}}
        }
        score_dict = eval_util_evaluation.ret_evaluation_result_dict(count_dict)
        for _, score_subdict in score_dict.items():
            for key, eval_result_dict in score_subdict.items():
                f1_score = eval_result_dict['f1_score']
                self.assertEqual(f1_score, 1.0)
    
if __name__ == '__main__':
    unittest.main()

