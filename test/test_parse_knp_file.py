import unittest
import pprint as pp
import json
from json_read_write import JsonReadWrite
from parse_knp_file import KNPDataLoader

class TestKNPDataLoader(unittest.TestCase):

    def _ret_case_elem_num_dict(self):
        case_elem_num_dict = {
            'S-ID:w201106-0000060050-1': {}, 
            'S-ID:w201106-0000060050-2': {} , 
            'S-ID:w201106-0000060050-3': {} 
        }

        case_elem_num_dict['S-ID:w201106-0000060050-1'] = {
            'subj': 5, 
            'obj' : 2,
            'obl': 0,
        }
        
        case_elem_num_dict['S-ID:w201106-0000060050-2'] = {
            'subj': 2, 
            'obj' : 1,
            'obl': 0,
        }

        case_elem_num_dict['S-ID:w201106-0000060050-3'] = {
            'subj': 5, 
            'obj' : 1,
            'obl': 2,
        }
        return case_elem_num_dict

    def _ret_case_content_dict(self):
        case_target_dict =  {'S-ID:w201106-0000060050-1': [{'gr': '主語',
                                 'pred': 'トス',
                                 'pred_bunsetsu': 'コイントスを',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '不特定:人',
                                 'target_sid': 'none'},
                                {'gr': '目的語',
                                 'pred': 'トス',
                                 'pred_bunsetsu': 'コイントスを',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'same_bunsetsu',
                                 'surface_case': 'ヲ',
                                 'target': 'コイン',
                                 'target_sid': 'S-ID:w201106-0000060050-1'},
                                {'gr': '主語',
                                 'pred': '行う',
                                 'pred_bunsetsu': '行う',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '不特定:人',
                                 'target_sid': 'none'},
                                {'gr': '主語',
                                 'pred': '行う',
                                 'pred_bunsetsu': '行う',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '読者',
                                 'target_sid': 'none'},
                                {'gr': '主語',
                                 'pred': '行う',
                                 'pred_bunsetsu': '行う',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '著者',
                                 'target_sid': 'none'},
                                {'gr': '目的語',
                                 'pred': '行う',
                                 'pred_bunsetsu': '行う',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ヲ',
                                 'target': 'トス',
                                 'target_sid': 'S-ID:w201106-0000060050-1'},
                                 {'gr': '主語',
                                 'pred': '行う',
                                 'pred_bunsetsu': '行う',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'rentai',
                                 'surface_case': 'ガ',
                                 'target': '俺たち',
                                 'target_sid': 'S-ID:w201106-0000060050-1'}
                                 ],
  'S-ID:w201106-0000060050-2': [{'gr': '主語',
                                 'pred': '出た',
                                 'pred_bunsetsu': '出た',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ガ',
                                 'target': '表',
                                 'target_sid': 'S-ID:w201106-0000060050-2'},
                                {'gr': '目的語',
                                 'pred': '破壊する。',
                                 'pred_bunsetsu': '破壊する。',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ヲ',
                                 'target': 'モンスター',
                                 'target_sid': 'S-ID:w201106-0000060050-2'},
                                {'gr': '主語',
                                 'pred': '破壊する。',
                                 'pred_bunsetsu': '破壊する。',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '不特定:状況',
                                 'target_sid': 'none'}],
  'S-ID:w201106-0000060050-3': [{'gr': 'ニ格',
                                 'pred': '１度',
                                 'pred_bunsetsu': '１度だけ',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ニ',
                                 'target': 'ターン',
                                 'target_sid': 'S-ID:w201106-0000060050-3'},
                                {'gr': '主語',
                                 'pred': 'メイン',
                                 'pred_bunsetsu': 'メインフェイズに',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'same_bunsetsu',
                                 'surface_case': 'ガ',
                                 'target': 'フェイズ',
                                 'target_sid': 'S-ID:w201106-0000060050-3'},
                                {'gr': '主語',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '不特定:人',
                                 'target_sid': 'none'},
                                {'gr': '目的語',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ヲ',
                                 'target': '効果',
                                 'target_sid': 'S-ID:w201106-0000060050-3'},
                                {'gr': '主語',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '著者',
                                 'target_sid': 'none'},
                                {'gr': '主語',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'outer',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '読者',
                                 'target_sid': 'none'},
                                {'gr': 'ニ格',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'intra_sentence',
                                 'rel_type': 'dep',
                                 'surface_case': 'ニ',
                                 'target': 'フェイズ',
                                 'target_sid': 'S-ID:w201106-0000060050-3'},
                                 {'gr': '主語',
                                 'pred': '使用する事',
                                 'pred_bunsetsu': '使用する事ができる。',
                                 'rel_dist': 'inter_sentence',
                                 'rel_type': 'zero',
                                 'surface_case': 'ガ',
                                 'target': '俺たち',
                                 'target_sid': 'S-ID:w201106-0000060050-1'}
                                 ]
        }
        return case_target_dict

    def _ret_elem_link_dict(self):
        elem_link_dict = {
            'S-ID:w201106-0000060050-1': {}, 
            'S-ID:w201106-0000060050-2': {}, 
            'S-ID:w201106-0000060050-3': {}
        }

        elem_link_dict['S-ID:w201106-0000060050-1'] = {
            0 : 1, 
            1 : 3,
            2 : 3,
            3 : 4,
            4 : -1
        }
        
        elem_link_dict['S-ID:w201106-0000060050-2'] = {
            0 : 1, 
            1 : 2,
            2 : 5,
            3 : 4,
            4 : 5,
            5 : -1
        }

        elem_link_dict['S-ID:w201106-0000060050-3'] = {
            0 : 1, 
            1 : 8,
            2 : 3,
            3 : 4,
            4 : 8,
            5 : 7,
            6 : 7,
            7 : 8,
            8 : -1
        }
        return elem_link_dict

    def setUp(self):
        # テストケースごとに実行される前処理を記述する場合、setUpメソッドを使用します
        self.knpload = KNPDataLoader()

        self.senid_list = ['S-ID:w201106-0000060050-1', 'S-ID:w201106-0000060050-2', 'S-ID:w201106-0000060050-3']
        self.bunnum_dict = {'S-ID:w201106-0000060050-1': 5, 
                'S-ID:w201106-0000060050-2': 6, 
                'S-ID:w201106-0000060050-3': 9 }

        self.prednum_dict = {'S-ID:w201106-0000060050-1': 7, 
                            'S-ID:w201106-0000060050-2': 3, 
                            'S-ID:w201106-0000060050-3': 8 }

        self.elem_link_dict = self._ret_elem_link_dict()

        self.case_elem_num_dict = self._ret_case_elem_num_dict()
        self.case_content_dict = self._ret_case_content_dict()

    @classmethod
    def tearDownClass(cls):
        
        knp_key='./test/data/*.knp'
        box = KNPDataLoader()
        knp_dict, pred_dict = box.ret_knp_dict(knp_key=knp_key)
        
        BASE_DIR = './test/data/'
        orgjsonfile = 'knp1.json'
        JsonReadWrite.write_json(BASE_DIR, orgjsonfile, knp_dict)

        orgjsonfile = 'knp_pred1.json'
        JsonReadWrite.write_json(BASE_DIR, orgjsonfile, pred_dict)

    def _ret_case_num_dict(self):
        case_dict = {'subj': 0, 'obj': 0, 'obl': 0 }
        return case_dict

    def test_ret_parse_knp_file(self):
        # テストメソッドの命名規則は「test_」で始める必要があります
        filename = './test/data/w201106-0000060050.knp'
        filekey, knp_bun_elem_dict, knp_pred_dict = self.knpload.parse_knp_file(filename)
        # 各文の文節の数をチェックする。
        for senid in self.senid_list:
            self.assertEqual(senid in knp_bun_elem_dict , True)
            self.assertEqual(senid in knp_pred_dict , True)
        
        # 要素数をチェックする。
        for senid, bunnum in self.bunnum_dict.items():
            elem_dict = knp_bun_elem_dict[senid]
            self.assertEqual(len(list(elem_dict.keys())), bunnum)
        
        case_num_dict = {}
        for senid, prednum in self.prednum_dict.items():
            pred_elem_list = knp_pred_dict[senid]
            case_num_tmp_dict = self._ret_case_num_dict()
            case_elem_list = []
            for tmp_dict in pred_elem_list:
                if tmp_dict['surface_case'] == 'ガ':
                    case_num_tmp_dict['subj'] += 1
                elif tmp_dict['surface_case'] == 'ヲ':
                    case_num_tmp_dict['obj'] += 1
                elif tmp_dict['surface_case'] == 'ニ':
                    case_num_tmp_dict['obl'] += 1

                case_elem_list.append(tmp_dict)
            case_num_dict[senid] = case_num_tmp_dict

            # 抜け漏れチェック
            check_dict = {}
            check_target_dict = {}
            correct_elem_count = 0
            for correct_elem_dict in self.case_content_dict[senid]:
                # correct_elem_dict に 完全に一致するものが 出力の辞書配列にあるか否かを確認する
                check_flag = False
                for target_dict1 in case_elem_list:
                    if correct_elem_dict == target_dict1:
                        check_flag = True
                        break
                check_target_dict[correct_elem_count] = correct_elem_dict
                check_dict[correct_elem_count] = check_flag
                correct_elem_count += 1
            print([f'Coverage check for annotated words in {senid}', check_dict])
            
            for num, check_flag in check_dict.items():
                if check_flag == False:
                    print(check_target_dict[num])
                    pp.pprint(case_elem_list)

                self.assertEqual(check_flag, True)
                
            
            # ゴミなし
            chatgpt_dict = {}
            check_chatgpt_dict = {}
            chatgpt_elem_count = 0
            for target_dict1 in case_elem_list:
                # correct_elem_dict に 完全に一致するものが 出力の辞書配列にあるか否かを確認する
                check_flag = False
                for correct_elem_dict in self.case_content_dict[senid]:
                    if correct_elem_dict == target_dict1:
                        check_flag = True
                        break
                check_chatgpt_dict[chatgpt_elem_count] = target_dict1
                chatgpt_dict[chatgpt_elem_count] = check_flag
                chatgpt_elem_count += 1
            print(chatgpt_dict)
            for num, check_flag in chatgpt_dict.items():
                self.assertEqual(check_flag, True)
            # pp.pprint(self.case_elem_string_dict[senid])
            self.assertEqual(len(pred_elem_list), prednum)

        # 文節のリンクが正しいかチェックする
        for senid, elink in self.elem_link_dict.items():
            for depnum, correctlink in elink.items():
                linknum = knp_bun_elem_dict[senid][depnum]['link']
                self.assertEqual(linknum, str(correctlink))

        for senid, crr_case_num_dict in self.case_elem_num_dict.items():
            for casestr, crr_casenum in crr_case_num_dict.items():
                sys_casenum = case_num_dict[senid][casestr]
                self.assertEqual(sys_casenum, crr_casenum)
        # 格要素の数をチェックする
        # ガ格、ヲ格、ニ格の数を数える
        # self.assertEqual('ok', 'ng')


if __name__ == '__main__':
    unittest.main()
