# orgの取得、idと文のlistで保持
import re
import glob
import os
import pprint as pp
import json
import unicodedata
import option_util as opu
from json_read_write import JsonReadWrite
# KWDLC/org/w201106-00000/w201106-0000069777.org
BASE_DIR = './'
rel_tag_pattern = re.compile(r'(\w+)="([^"]+)"')

class EvalConversation(object):
    def __init__(self):
        self.target_case_dict = {'ガ': '主語', 'ヲ' : '目的語', 'ニ' : 'ニ格'} 
        self.gr2case_dict = {'主語': 'subj', '目的語': 'obj', 'ニ格': 'obl'} # 二格
        self.table_regexp = re.compile('^\|.*\|$')
        self.case_list = ['subj', 'obj', 'obl', 'pred', 'all']
        self.rel_dist_list = ['inter_sentence', 'intra_sentence', 'outer']

    def _ret_init_count_dict(self):
        count_dict = {}
        for gr in self.case_list:
            count_dict[gr] = self._ret_init_eval_count_dict()
        return count_dict

    def _ret_init_eval_count_dict(self):
        num_dict = {'sout':0, 'csout':0, 'cnum': 0 }
        return num_dict
    
    def _ret_init_case_count_dict(self):
        eval_count_dict = {}
        for gr in self.case_list:
            eval_count_dict[gr] = 0            
        return eval_count_dict


    def _startswith(self, str1, str2, length=1):
        for i in range(len(str1), 0, -1):
            substring = str1[:i]
            if len(substring) > length:
                if str2.startswith(substring) == True:
                    return True
            else:
                break
        return False

    def _partmatch(self, str1, str2, length=1):
        """片方の文字列の先頭と末尾を削っていき2文字以上の場合にもう一方の文字列に一致がある場合を検出する"""
        l = list(str1)
        cursor1 = 0
        cursor2 = len(l)
        while cursor1 < cursor2:
            cursor1 += 1
            cstr1 = l[cursor1:cursor2]
            if len(cstr1) > length:
                if ''.join(cstr1) in str2:
                    return True
            cursor2 = cursor2 - 1
            cstr2 = l[cursor1:cursor2]
            if len(cstr2) > length:
                if ''.join(cstr1) in str2:
                    return True
        return False

    def _ret_match_type(self, crr_str, gpt_str):
        
        if crr_str == '筆者' and gpt_str == '著者':
            return 'author'
        elif crr_str == '著者' and gpt_str == '筆者':
            return 'author'

        mstr = 'not_match'
        if gpt_str == '-' or gpt_str == '':
            return mstr

        if crr_str == gpt_str:
            return 'match'
        
        if gpt_str.startswith(crr_str) == True:   
            mstr = "gpt_start_with_crr"
        elif crr_str.startswith(gpt_str) == True:   
            mstr =  "crr_start_with_gpt"
        elif crr_str in gpt_str:
            mstr =  "gpt_long"
        elif gpt_str in crr_str:
            mstr = "crr_long"
        elif self._startswith(gpt_str, crr_str, length=1):
            mstr = "head_match"
        elif self._startswith(crr_str, gpt_str, length=1):
            mstr = "head_match"
        elif self._partmatch(gpt_str, crr_str, length=1):
            mstr = "part_match"
        elif self._partmatch(crr_str, gpt_str, length=1):
            mstr = "part_match"
        
        return mstr

    def ret_evaluation_result_dict(self, count_dict):
        rdict = {}
        if 'all' in count_dict:
           for key, num_dict in count_dict.items():
                rdict[key] = self._ret_eval_result_dict(num_dict)
        else:
            for key, num_dict in count_dict.items():
                rdict[key] = {}
                rdict[key] = self.ret_evaluation_result_dict(num_dict)

        return rdict

    def _ret_eval_result_dict(self, count_dict):
        cnum = count_dict['cnum']
        sout = count_dict['sout']
        csout = count_dict['csout']
        rdict = self._ret_f1_score_dict(csout, sout, cnum)
        return rdict

    def _ret_f1_score_dict(self, correct_system_outputs, system_outputs, correct_num):
        """
        F値を計算する
        """
        if system_outputs == 0:
            if correct_system_outputs == 0:
                precision = 0.0
            elif correct_system_outputs > 0:
                precision = 0.0
        else:
            if correct_system_outputs > system_outputs:
                precision = 0.0
            else: 
                precision = correct_system_outputs / system_outputs

        if correct_num == 0:
            if correct_system_outputs == 0:
                recall = 0.0
            else:
                recall = 0.0
        else:
            recall = correct_system_outputs / correct_num

        if precision + recall == 0.0:
            f1_score = 0.0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)
        return {'precision': precision, 'recall': recall, 'f1_score': f1_score}

    def _cout_up_crr_sout(self, senid,  crr_target_str, gpt_target_line, case_str, crr_sout_dict):
        for gpt_target_str in gpt_target_line.split('、'):
            check = self._ret_match_type(crr_target_str, gpt_target_str)
            if not self._ret_match_type(crr_target_str, gpt_target_str) == 'not_match':
                crr_sout_dict[case_str] += 1
                crr_sout_dict['all'] += 1
    
    def _count_up_crr_sout_dict(self, knp_pred_dict, gpt_pred_str, conv_dict, crr_sout_dict):
        """
        ChatGPTのテーブルの1行ごとにチェックを行う。
        Pred、subj、obj、obl を順々に。
        
        """

        subj_target = conv_dict['subj']
        obj_target = conv_dict['obj']
        obl_target = conv_dict['obl']
        
        # そもそも一致する正解 Pred あるの？
        for senid, pred_list in knp_pred_dict.items():
            if senid == conv_dict['senid']:
                for case_elem in pred_list:
                    crr_pred_str = case_elem['pred']
                    crr_target = case_elem['target']
                    
                    case_str = self.gr2case_dict[case_elem['gr']]    
                    pred_check = self._ret_match_type(crr_pred_str, gpt_pred_str)
                    # そもそもPredがマッチしない。
                    if not pred_check == 'not_match':
                        if case_str == 'subj' or case_str == 'obj' or case_str == 'obl':
                            gpt_target = conv_dict[case_str]
                            self._cout_up_crr_sout(senid, crr_target, gpt_target, case_str, crr_sout_dict)
                            
    def _ret_crr_sout_num_dict(self, knp_pred, chatgpt_result):
        # 出力のうち正解したものをカウントする
        crr_sout_dict = self._ret_init_case_count_dict()
        gpt_pred_dict = {}
        crr_pred_dict = {}

        for senid, pred_list in knp_pred.items():
            if not senid in crr_pred_dict:
                crr_pred_dict[senid] = set()
            for case_elem in pred_list:
                crr_pred_str = case_elem['pred']
                crr_pred_dict[senid].add(crr_pred_str)

        for conv_dict in chatgpt_result:
            # predの一致を見る
            gpt_pred_line = conv_dict['pred']
            gpt_senid = conv_dict['senid']
            if not gpt_senid in gpt_pred_dict:
                gpt_pred_dict[gpt_senid] = set()
            
            gpt_pred_list = gpt_pred_line.split('、')
            for gpt_pred_str in gpt_pred_list:
                gpt_pred_dict[gpt_senid].add(gpt_pred_str)
            # 正解してる？

            for gpt_pred_str in gpt_pred_list:
                self._count_up_crr_sout_dict(knp_pred, gpt_pred_str, conv_dict, crr_sout_dict)

        for senid, pred_set in crr_pred_dict.items():
            if senid in gpt_pred_dict:
                gpt_pred_set = gpt_pred_dict[senid]
                for crr_pred_str in list(pred_set):
                    for gpt_pred_str in list(gpt_pred_set):
                        pred_check = self._ret_match_type(crr_pred_str, gpt_pred_str)
                        if not pred_check == 'not_match':
                            crr_sout_dict['pred'] += 1
                            break
        
        return crr_sout_dict

    def _check_no_output(self, case_target_str):
        if case_target_str == '-':
            return True
        elif case_target_str == 'ない':
            return True
        elif case_target_str == 'なし':
            return True
        else:
            return False

    def ret_count_dict(self, knp_pred, org_dict, chatgpt_result):
        """ F1スコアを計算するための計数結果の辞書を返す。
        格要素の一致/不一致を素直にカウントして精度を算出する。
        ret_count_dict (cnum, soutをカウント)
            _ret_crr_sout_num_dict、(csoutをカウント)
                _count_up_crr_sout_dict（ChatGPTのpredごとにsoutをチェックする）
                    _cout_up_crr_sou（格要素のマッチングを行う）
        """
        
        count_dict = {}
        for gr in self.case_list:
            count_dict[gr] = self._ret_init_eval_count_dict()
        
        # 出力の数をカウント
        for gpt_elem in chatgpt_result:
            for cstr in ['subj', 'obj', 'obl']:
                case_target_line = gpt_elem[cstr]
                for case_target_str in case_target_line.split('、'):
                    if not self._check_no_output(case_target_str) == True:
                        count_dict[cstr]['sout'] += 1
                        count_dict['all']['sout'] += 1
            
            # pred は 1行 につき １つ出力
            count_dict['pred']['sout'] += 1
        
        # 本当の正解の数をカウント
        for senid, pred_list in knp_pred.items():
            pred_count_dict = {}
            for case_elem in pred_list:
                crr_pred_str = case_elem['pred']
                if not crr_pred_str in pred_count_dict:
                    pred_count_dict[crr_pred_str] = 0
                pred_count_dict[crr_pred_str] += 1

                target = case_elem['target']
                if case_elem['gr'] == '主語' or case_elem['gr'] == '目的語' or case_elem['gr'] == 'ニ格':
                    case_str = self.gr2case_dict[case_elem['gr']]
                    count_dict[case_str]['cnum'] += 1
                    count_dict['all']['cnum'] += 1
            count_dict['pred']['cnum'] += len(list(pred_count_dict.keys()))
                
        # 出力の中の正解数をカウント
        crr_sout_dict = self._ret_crr_sout_num_dict(knp_pred, chatgpt_result)
        for case_str, num in crr_sout_dict.items():
            count_dict[case_str]['csout'] += num

        return count_dict

    def _ret_type_str(self, case_elem):
        rel_dist = case_elem['rel_dist']
        rel_type = case_elem['rel_type']
        type1 = rel_type
        if rel_type == 'zero':
            type1 = f'{rel_type}_{rel_dist}'
        return type1

    def _ret_dist_relation_type(self, senid, org_dict, target_str):
        # 位置関係だけを返す
        # intra_sentence（文中）
        # inter_sentence（文外）
        # outer（文章外）
        """
        if senid in org_dict:
            senstr = org_dict[senid]
            senstr = senstr.replace('「', '')
            senstr = senstr.replace('」', '')
            if target_str in senstr:
                return 'intra_sentence'
        """
        
        if senid in org_dict:   
            senstr = org_dict[senid]
            senstr = senstr.replace('「', '')
            senstr = senstr.replace('」', '')
            if target_str in senstr:
                return 'intra_sentence'

        for tmp_senid, senstr in org_dict.items():
            if tmp_senid == senid:
                continue
            senstr = senstr.replace('「', '')
            senstr = senstr.replace('」', '')
            if target_str in senstr:
                return 'inter_sentence'

        return 'outer'
        # senid, org_dict, target_str

    def ret_detail_count_dict(self, knp_pred, org_dict, chatgpt_result):
        """ ChatGPTとKNPのPredが一致した場合の正解をカウントする
        （本来の姿）
        格要素のタイプごとにsub、obj、oblの正解数をカウントする。
                    | subj| obj | obl | all
        dep         |
        rentai      | 
        sahen       | 
        zero_intra  |
        zero_inter  |
        zero_outer  |

        zeroは、文内、文外、文章外で分かれる。
        
        （現状の実装）
        ChatGPTの出力には上記の関係はわからないので、
        intra_sentence
        inter_sentence
        outer
        の3種類の距離関係（rel_dist）で精度を計ることにする。
        """

        rel_count_dict = {}
         # 初期化
        for type1 in self.rel_dist_list:
            # type1 = self._ret_type_str(case_elem)
            if not type1 in rel_count_dict:
                rel_count_dict[type1] = {}
            for gr in self.case_list:
                # pred は対象外
                if not gr == 'pred':
                    rel_count_dict[type1][gr] = self._ret_init_eval_count_dict()
        
        gpt_pred_dict = {}
         # ChatGPT の 出力を 構造化する
        for gpt_elem in chatgpt_result:
            senid1 = gpt_elem['senid']
            if not senid1 in gpt_pred_dict:
                gpt_pred_dict[senid1] = {}
            for gpt_pred_str in gpt_elem['pred'].split('、'):
                if not gpt_pred_str in gpt_pred_dict[senid1]:
                    gpt_pred_dict[senid1][gpt_pred_str] = {}
                for cstr in ['subj', 'obj', 'obl']:
                    case_target_line = gpt_elem[cstr]
                    gpt_pred_dict[senid1][gpt_pred_str][cstr] = case_target_line.split('、')

        match_pred_dict = {}

        # KNPの正解とChatGPTとの付き合わせ
        for senid, pred_list in knp_pred.items():
            for case_elem in pred_list:
                crr_pred_str = case_elem['pred']
                crr_target = case_elem['target']
                type1 = rel_dist = case_elem['rel_dist']
                # type1 = self._ret_type_str(case_elem)
                if senid in gpt_pred_dict:
                    
                    for gpt_pred_str, gpt_case_elem_dict in gpt_pred_dict[senid].items():
                        pred_check = self._ret_match_type(crr_pred_str, gpt_pred_str)
                        # Predがマッチした時にのみ、cnum、sout、csoutをカウントする。
                        if not pred_check == 'not_match':
                            
                            # KNPとChatGPTとで一致した述語を記憶しておく
                            if not senid in match_pred_dict:
                                match_pred_dict[senid] = {}
                            if not gpt_pred_str in match_pred_dict[senid]:
                                match_pred_dict[senid][gpt_pred_str] = {}

                            if case_elem['gr'] == '主語' or case_elem['gr'] == '目的語' or case_elem['gr'] == 'ニ格':
                                case_key_str = self.gr2case_dict[case_elem['gr']]
                                rel_count_dict[type1][case_key_str]['cnum'] += 1
                                rel_count_dict[type1]['all']['cnum'] += 1
                                
                                #か空でなければ出力したとみなす
                                for gpt_target_str in gpt_case_elem_dict[case_key_str]:
                                    if not case_key_str in match_pred_dict[senid][gpt_pred_str]:
                                        match_pred_dict[senid][gpt_pred_str][case_key_str] = {}
                                    match_pred_dict[senid][gpt_pred_str][case_key_str][gpt_target_str] = True
                                    
                                    check = self._ret_match_type(crr_target, gpt_target_str)

                                    if not check == 'not_match':
                                        rel_count_dict[type1][case_key_str]['csout'] += 1
                                        rel_count_dict[type1]['all']['csout'] += 1
                                        break
                                break
        
        # KNPとマッチした述語に関して、ChatGPTが出力した文字列の文内、文外、文章外判定する。 
        for senid, gpt_case_elem_dict1 in gpt_pred_dict.items():
            for gpt_pred_str, gpt_case_elem_dict in gpt_case_elem_dict1.items():
                if senid in match_pred_dict:
                    if gpt_pred_str in match_pred_dict[senid]:
                        for case_key_str, target_dict in match_pred_dict[senid][gpt_pred_str].items():

                            for target_str in target_dict.keys():
                                type1 = self._ret_dist_relation_type(senid, org_dict, target_str) 
                                rel_count_dict[type1][case_key_str]['sout'] += 1
                                rel_count_dict[type1]['all']['sout'] += 1

        return rel_count_dict


    def ret_sennum_list(self, org, pred, sennum):
        sen_count = 1
        sennum = unicodedata.normalize('NFKC', sennum)
        match = re.findall('\d+', sennum)
        match_list = []
        senid_list = list(org.keys())
        
        if match:
            sennum = int(match[0])
            if len(senid_list) >= sennum:
                senid = senid_list[sennum-1]
                match_list.append(senid)
        return match_list
    
    def _parse_row_line(self, line):
        l = line.split('|')
        
        elem_dict = {'sennum': 0, 
            'pred': '',
            'subj': '',
            'obj': '',
            'obl': ''  
        }

        for lidx, elem in enumerate(l):
            elem = elem.replace(' ', '')
            if lidx == 1:
                elem_dict['sennum'] = elem
            elif lidx == 2:
                elem_dict['pred'] = elem
            elif lidx == 3:
                elem_dict['subj'] = elem
            elif lidx == 4:
                elem_dict['obj'] = elem
            elif lidx == 5:
                elem_dict['obl'] = elem
        
        return elem_dict
                    

    def parse_conversation(self, org_dict, conversation):
        lines = conversation.split('\n')
        rlist = []
        for tidx, line in enumerate(lines):
            match = self.table_regexp.match(line)
            if match:
                if tidx > 1:
                    elem_dict = self._parse_row_line(line)
                    sennum = elem_dict['sennum']
                    pred = elem_dict['pred']
                    senid_list = self.ret_sennum_list(org_dict, pred, sennum)
                    for senid in senid_list:
                        tmp_dict = {}
                        tmp_dict['senid'] = senid
                        tmp_dict['subj'] = elem_dict['subj']
                        tmp_dict['obj'] = elem_dict['obj']
                        tmp_dict['obl'] = elem_dict['obl']
                        tmp_dict['pred'] = elem_dict['pred']
                        rlist.append(tmp_dict)
        
        return rlist


    def _set_sum_stat_all1(self, dict1):
        total = 0
        for key, value in dict1.items():
            if not key == 'all':
                total += value
        dict1['all'] = total
        return dict1

    def _set_sum_stat_all(self, dict1):
        total = 0
        rdict = {}
        for key, vdict in dict1.items():
            rdict[key] = self._set_sum_stat_all1(vdict)
        return rdict

    def _ret_sub_sum_dict(self, dict0):
        total = 0
        rdict = {}
        for phase, dict1 in dict0.items():
            for key, sub_dict in dict1.items():
                if not key in rdict:
                    rdict[key] = {}
                for ckey, num in sub_dict.items():
                    if not ckey in rdict[key]:
                        rdict[key][ckey] = 0
                    rdict[key][ckey] += num
        return rdict

    def analysis(self, knp_pred_dict, train_test_id_dict):
        # 本当の正解の数をカウント
        
        case_count_dict = {}
        case_count_rt_dict = {}
        
        for phase, id_list in train_test_id_dict.items():
            
            if not phase in case_count_dict:
                case_count_dict[phase] = {}

            if not phase in case_count_rt_dict:
                case_count_rt_dict[phase] = {}

            for id in id_list:
                knp_pred = knp_pred_dict[id]
                for senid, pred_list in knp_pred.items():
                    for case_elem in pred_list:
                        crr_pred_str = case_elem['pred']
                        target = case_elem['target']
                        rel_dist = case_elem['rel_dist']
                        rel_type = case_elem['rel_type']
                        case_str = self.gr2case_dict[case_elem['gr']]

                        if not rel_dist in case_count_dict[phase]:
                            case_count_dict[phase][rel_dist] = {'all': 0, 'subj': 0, 'obj': 0, 'obl': 0}

                        if not rel_type in case_count_rt_dict[phase]:
                            case_count_rt_dict[phase][rel_type] = {'all': 0, 'subj': 0, 'obj': 0, 'obl': 0}
                        
                        case_count_dict[phase][rel_dist][case_str] += 1
                        case_count_rt_dict[phase][rel_type][case_str] += 1

       
        # pp.pprint(case_count_rt_dict)
        dict1 = self._ret_sub_sum_dict(case_count_dict)
        # pp.pprint(dict1)
        pp.pprint(self._set_sum_stat_all(dict1))
        
        dict1 = self._ret_sub_sum_dict(case_count_rt_dict)
        # pp.pprint(dict1)
        pp.pprint(self._set_sum_stat_all(dict1))
        

    def evaluate(self, knp_pred_dict, train_test_id_dict, org_dict, result_dict, phase):
        lcount = 0
        count_dict = self._ret_init_count_dict()
        detail_count_dict = {}
        for id in train_test_id_dict[phase]:
            knp_pred = knp_pred_dict[id]
            org_one_dict = org_dict[id] 
            
            if id in result_dict:
                conversation = result_dict[id]
                case_lines = self.parse_conversation(org_one_dict, conversation)
                
                
                count_dict1 = self.ret_count_dict(knp_pred, org_one_dict, case_lines)
                for case_str, count_sub_dict in count_dict1.items():
                    for count_type, freq in count_sub_dict.items():
                        count_dict[case_str][count_type] += freq

                detail_count_dict1 = self.ret_detail_count_dict(knp_pred, org_one_dict, case_lines)
                
                for type1, detail_count_sub_dict in detail_count_dict1.items():
                    if not type1 in detail_count_dict:
                        detail_count_dict[type1] = {}
                    for case_str, detail_count_sub_dict2 in detail_count_sub_dict.items():
                        if not case_str in detail_count_dict[type1]:
                            detail_count_dict[type1][case_str] = {}
                        for count_type, freq in detail_count_sub_dict2.items():
                            if not count_type in detail_count_dict[type1][case_str]:
                                detail_count_dict[type1][case_str][count_type] = 0
                            detail_count_dict[type1][case_str][count_type] += freq
                
                lcount += 1
                # break
        pp.pprint(count_dict)
        eval_result_dict = self.ret_evaluation_result_dict(count_dict)
        pp.pprint(eval_result_dict)
        table_line = box.ret_eval_simple_table_line(eval_result_dict)
        print(table_line)

        pp.pprint(detail_count_dict)
        detail_eval_result_dict = self.ret_evaluation_result_dict(detail_count_dict)
        pp.pprint(detail_eval_result_dict)

        table_line = box.ret_eval_detail_table_line(detail_eval_result_dict)
        print(table_line)

    def ret_result_dict_series(self, dirname='ok_result_dev'):
        # json_open = open('./sample_data/sample2.json', 'r')
        ok_pred_content_dict = {}
        result_compose_dict = {}
        ok_results_list = glob.glob(f'./{dirname}/*.json')
        for file1 in ok_results_list:
            json_open = open(file1, 'r')
            pred_dict = json.load(json_open) 
            for id1, conv_dict in pred_dict.items():
                if not id1 in result_compose_dict:
                    result_compose_dict[id1] = {}
                status = conv_dict['status']
                if not status in result_compose_dict[id1]:
                    result_compose_dict[id1][status] = 0
                result_compose_dict[id1][status] += 1

                if conv_dict['status'] == 'ok':
                    contents = conv_dict['response']["choices"][0]["message"]["content"]
                    ok_pred_content_dict[id1] = contents
        
        return ok_pred_content_dict, result_compose_dict

    def _round_to_significant_digits(self, number, digits):
        # 数値を指定した桁数に丸める関数
        return round(number, digits)

    def ret_org_line(self, org_sub_dict):
        rlist = []
        for senid, sentext in org_sub_dict.items():
            rlist.append(f'# {senid}')
            rlist.append(sentext)

        return '\n'.join(rlist)
    
    def _ret_eval_table_row_line(self, key1, ctype_f1values, case_list):
        key_count = 0
        gr2case_swap = {v: k for k, v in self.gr2case_dict.items()}
        rlist = []
        for ctype1 in case_list:
            f1values = ctype_f1values[ctype1]
            if ctype1 in gr2case_swap:
                ctype = gr2case_swap[ctype1]
                cstr = f'{ctype}({ctype1})'
            elif ctype1 == 'all':
                cstr = '格要素(all)'
            if key_count == 0:
                key = key1
            else:
                key = ''
            
            p1 = self._round_to_significant_digits(f1values['precision'],  3)
            r1 = self._round_to_significant_digits(f1values['recall'],  3)
            f1 = self._round_to_significant_digits(f1values['f1_score'],  3)
            rows = ['', key, cstr, str(p1), str(r1), str(f1), '']
            row_line = '|'.join(rows)
            rlist.append(row_line)
            key_count += 1
        return rlist

    def _ret_eval_head_lines(self):
        rows = ['', '述語との距離関係', '格要素','Precision', 'Recall','F1スコア', '']
        row_line = '|'.join(rows)
        tlines = [row_line]
        return tlines

    def ret_eval_simple_table_line(self, dict1):
        tlines = self._ret_eval_head_lines()
        clist = ['all', 'subj', 'obj', 'obl', 'pred']
        
        for row_line in self._ret_eval_table_row_line('empty', dict1, clist):
            tlines.append(row_line)
            
        return '\n'.join(tlines)

    def ret_eval_detail_table_line(self, dict1):
        tlines = self._ret_eval_head_lines()
        clist = ['subj', 'obj', 'obl', 'all']
        for key1, ctype_f1values in dict1.items():
            for row_line in self._ret_eval_table_row_line(key1, ctype_f1values,clist):
                tlines.append(row_line)
            
        return '\n'.join(tlines)

    def ret_table_line_from_knp(self, knp_sub_pred_dict):
        row_lines = []
        rows = ['', '文番号', '述語','主語(subj)', '目的語(obj)','斜格語(obl)', '']
        row_lines.append('|'.join(rows))
        row_dict = {}
        for senid, elem_list in knp_sub_pred_dict.items():
            if not senid in row_dict:
                row_dict[senid] = {}
            for tmp_dict in elem_list:
                pred = tmp_dict['pred']
                if not pred in row_dict[senid]:
                    row_dict[senid][pred] = {'主語':[], '目的語': [], 'ニ格':[] }
                gr = tmp_dict['gr']
                rel_type = tmp_dict['rel_type']
                rel_dist = tmp_dict['rel_dist']
                target = tmp_dict['target']
                row_dict[senid][pred][gr].append(f'{target}({rel_type}_{rel_dist})')
        for senid, pred_dict1 in row_dict.items():
            for pred, gr_dict in pred_dict1.items():
                
                subj = '、'.join(gr_dict['主語'])
                obj = '、'.join(gr_dict['目的語'])
                obl = '、'.join(gr_dict['ニ格'])
                if subj == '':
                    subj = '-'
                if obj == '':
                    obj = '-'
                if obl == '':
                    obl = '-'
                rows = ['', senid, pred,  subj, obj, obl, '']
                row_lines.append('|'.join(rows))

        return '\n'.join(row_lines)

    def filter_id_dict_by_dist_dict(self, dist_dict, knp_pred_dict):
        target_dict = {}
        for id1, knp_sub_pred_dict in knp_pred_dict.items():
            for senid, tmp_list in knp_sub_pred_dict.items():
                for tmp_dict in tmp_list:
                    rel_type = tmp_dict['rel_type']
                    rel_dist = tmp_dict['rel_dist']
                    if dist_dict['rel_type'] == tmp_dict['rel_type']:
                        if dist_dict['rel_dist'] == tmp_dict['rel_dist']:
                            target_dict[id1] = True
                            break
        return target_dict

if __name__=="__main__":

    # 引数をパース
    args = opu.get_eval_option()

    box = EvalConversation()
    json_open = open('./intermediate_data/knp_pred1.json', 'r')
    knp_pred_dict = json.load(json_open) 

    json_open = open('./data/train_test_id.json', 'r')
    train_test_id_dict = json.load(json_open)  
    
    for phase, idlist in train_test_id_dict.items():
        print([phase, len(idlist)])

    # json_open = open('./sample_data/sample2.json', 'r')
    json_open = open('./data/org.json', 'r')
    org_dict = json.load(json_open) 

 
    if args.process == 'analysis':
        box.analysis(knp_pred_dict, train_test_id_dict)
    else:
        # pass
        # print(["size of results via ChatGPT: ", len(result_compose_dict), len(ok_pred_content_dict)])
        dirname = 'ok_result_dev'
        phase = 'dev'
        ok_pred_content_dict, result_compose_dict = box.ret_result_dict_series(dirname)
        print(len(ok_pred_content_dict), len(result_compose_dict))
        okcount = 0
        for k,v in result_compose_dict.items():
            if 'ng' in v:
                okcount += 1
        print(okcount)

        box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict, phase)
        
        # 特定のidの文章をエラーアナリシス
        id1 = 'w201106-0002000002'
        line = box.ret_table_line_from_knp(knp_pred_dict[id1])
        print(line)
        line = box.ret_org_line(org_dict[id1])
        print(line)
        pp.pprint(ok_pred_content_dict[id1])
        
        # 文間ゼロ照応の事例をエラーアナリシスします
        target_id_dict = box.filter_id_dict_by_dist_dict({'rel_type': 'zero', 'rel_dist': 'inter_sentence'}, knp_pred_dict)
        show_count = 0
        for id1, _ in target_id_dict.items():
            
            if id1 in ok_pred_content_dict:
                line = box.ret_table_line_from_knp(knp_pred_dict[id1])
                print(line)
                line = box.ret_org_line(org_dict[id1])
                print(line)
                pp.pprint(ok_pred_content_dict[id1])
                show_count += 1

            if show_count == 5:
                break
        