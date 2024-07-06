import re
import glob
import os
import pprint as pp
import json
import unicodedata
import sys
import random
from sentence_parser import SentenceParser
# スクリプトがあるディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# libディレクトリの絶対パスを構築して追加
lib_path = os.path.join(script_dir, 'lib')
sys.path.append(lib_path)

import option_util as opu
import eval_util_evaluation as eval_util_evaluation
import eval_util_knp as eval_util_knp
import eval_util_string_match as eu_strmatch
import eval_util_count as eu_count
import option_util as optu
from json_read_write import JsonReadWrite

import target_file_util as tfu
import experimental_util as experimental_util
import prompt_util as prompt_util

# KWDLC/org/w201106-00000/w201106-0000069777.org
BASE_DIR = './'
rel_tag_pattern = re.compile(r'(\w+)="([^"]+)"')

class EvalConversation(object):
    def __init__(self, verbose_flag=False):
        self.target_case_dict = {'ガ': '主語', 'ヲ' : '目的語', 'ニ' : 'ニ格'} 
        self.gr2case_dict = {'主語': 'subj', '目的語': 'obj', 'ニ格': 'obl', '述語': 'pred'} # 二格
        self.table_regexp = re.compile('^\|.*\|$')
        self.sennum_regexp = re.compile('^\|\s*文\d+\s*')
        self.case_list = ['subj', 'obj', 'obl', 'pred', 'all']
        self.rel_dist_list = ['inter_sentence', 'intra_sentence', 'outer']
        self.rel_type_list = ['dep', 'zero', 'same_bunsetsu', 'rentai']
        self.verbose = verbose_flag 

        self.error_case_dict = {'case_out': 0, 'rel_shift':0, 'pred_not_detect': 0 }
        self.case_lost_dict = {'subj':0, 'obj':0, 'obl':0 }

    def show_error_num(self):
        print(self.error_case_dict)
        print(self.case_lost_dict)

    def _cout_up_crr_sout(self, senid,  crr_target_str, gpt_target_line, case_str, crr_sout_dict):
        for gpt_target_str in gpt_target_line.split('、'):
            check = eu_strmatch.ret_match_type(crr_target_str, gpt_target_str)
            if not eu_strmatch.ret_match_type(crr_target_str, gpt_target_str) == 'not_match':
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
                    pred_check = eu_strmatch.ret_match_type(crr_pred_str, gpt_pred_str)
                    # そもそもPredがマッチしない。
                    if not pred_check == 'not_match':
                        if case_str == 'subj' or case_str == 'obj' or case_str == 'obl':
                            gpt_target = conv_dict[case_str]
                            self._cout_up_crr_sout(senid, crr_target, gpt_target, case_str, crr_sout_dict)
                            
    def _ret_crr_sout_num_dict(self, knp_pred, chatgpt_result):
        # 出力のうち正解したものをカウントする
        crr_sout_dict = eu_count.ret_init_case_count_dict(self.case_list)
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
                        pred_check = eu_strmatch.ret_match_type(crr_pred_str, gpt_pred_str)
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

    
    def ret_knp_count_dict(self, knp_pred_dict, org_dict, knp_pred_ana_dict, chatgpt_dict, stat_dict, target_type='anaphora'):
        """ F1スコアを計算するための計数結果の辞書を返す。
        
        """
        count_dict = {}
        for gr in self.case_list:
            count_dict[gr] = eu_count.ret_init_eval_count_dict()

        rel_count_dict = eu_count.ret_init_rel_count_dict(self.case_list, self.rel_type_list, self.rel_dist_list)
        
        # 正解は全部通す
        knp_pred = eval_util_knp.ret_knp_pred_kv_dict(knp_pred_dict, self.gr2case_dict, target_type='all')
        
        # 評価対象はfilterする
        knp_pred_ana = eval_util_knp.ret_knp_pred_kv_dict(knp_pred_ana_dict, self.gr2case_dict, target_type=target_type)

        for senid, crr_bunsetsu_dict in knp_pred.items():
            ana_sen_bunsetsu_dict = knp_pred_ana[senid]
            chatgpt_sen_dict = {}
            if senid in chatgpt_dict:
                chatgpt_sen_dict = chatgpt_dict[senid]
            
            # もしKNPにpred検出ができていない時にchatGPTさんが検出できていたら、gainじゃよ！
            # 落としていたらloseだよ
            # もしkNPの格を検出できてない時にChatGPTさんが検出できていたらgainだよ。落としていたらloseだよ
            for crr_bun, pred_id_dict in crr_bunsetsu_dict.items():
                
                knp_pred_has = False
                chat_gpt_pred_has = False
                
                knp_case_has = False
                chat_gpt_case_has = False

                ana_pred_bunsetsu_dict = {}
                if crr_bun in ana_sen_bunsetsu_dict:
                    ana_pred_bunsetsu_dict = ana_sen_bunsetsu_dict[crr_bun]
                
                for pred_id, sub_dict in pred_id_dict.items():
                    knp_pred_dict = {'case':{} }

                    crr_case_set = set(sub_dict['case'].keys())

                    if pred_id in ana_pred_bunsetsu_dict:
                        knp_pred_dict = ana_pred_bunsetsu_dict[pred_id]
                        knp_pred_has = True
                        knp_case_set = set(knp_pred_dict['case'].keys())

                        if knp_case_set == crr_case_set:
                            knp_case_has = True

                    for gr, gr_list in sub_dict['case'].items():

                        for tmp_dict in gr_list:
                            rel_dist = tmp_dict['rel_dist']
                            rel_type = tmp_dict['rel_type']
                            target = tmp_dict['surface']
                            if rel_type == 'zero':
                                rel_type = f'{rel_type}_{rel_dist}' 

                            rel_count_dict[rel_type][gr]['cnum'] += 1
                            count_dict[gr]['cnum'] += 1

                            # 正解の中にchatgptと一致するものがあるか
                            for chat_gpt_pred, chatgpt_case_list in chatgpt_sen_dict.items():
                                chat_gpt_pred_match_type = eu_strmatch.ret_match_type(chat_gpt_pred, crr_bun)
                                if not chat_gpt_pred_match_type == 'not_match':
                                    chat_gpt_pred_has = True
                                    for e in chatgpt_case_list:
                                        evalue = e[gr]
                                        # 各caseごと1回チェックする
                                        if evalue == '-' or evalue == 'なし' or evalue == '':
                                            pass
                                        else:
                                            chat_gpt_match = eu_strmatch.ret_match_type(evalue, target)
                                            # chatgpt と 正解が一致
                                            if not chat_gpt_match == 'not_match':
                                                # KNPさんは解析できてない
                                                # print(["yes chatgpt", evalue, gr, crr_bun])
                                                stat_dict['new_one'][gr] += 1    
                                                break
                                                
                    count_dict['pred']['cnum'] += 1

                for chat_gpt_pred, chatgpt_case_list in chatgpt_sen_dict.items():
                    chatgpt_case_set = set()
                    for e in chatgpt_case_list:
                        for ckey in ['subj', 'obj', 'obl']:
                            if e[ckey] == '-' or e[ckey] == 'なし' or e[ckey] == '':
                                pass
                            else:
                                chatgpt_case_set.add(ckey)
                    
                    # print(["Case gogo", "chatgpt", chatgpt_case_set, "correct", crr_case_set])
                    if chatgpt_case_set == crr_case_set:
                        chat_gpt_case_has = True
                
                if chat_gpt_pred_has == True and knp_pred_has == True:
                    stat_dict['pred']['even'] += 1
                elif chat_gpt_pred_has == False and knp_pred_has == True:
                    stat_dict['pred']['lost'] += 1
                elif chat_gpt_pred_has == True and knp_pred_has == False:
                    stat_dict['pred']['gain'] += 1
                elif chat_gpt_pred_has == False and knp_pred_has == False:
                    stat_dict['pred']['difficult'] += 1

                if chat_gpt_case_has == True and knp_case_has == True:
                    stat_dict['case']['even'] += 1
                elif chat_gpt_case_has == False and knp_case_has == True:
                    stat_dict['case']['lost'] += 1
                elif chat_gpt_case_has == True and knp_case_has == False:
                    stat_dict['case']['gain'] += 1
                elif chat_gpt_case_has == False and knp_case_has == False:
                    stat_dict['case']['difficult'] += 1

        for senid, pred_bunsetsu_dict in knp_pred_ana.items():
            crr_bunsetsu_dict = knp_pred[senid]

            chatgpt_sen_dict2 = {}
            if senid in chatgpt_dict:
                chatgpt_sen_dict2 = chatgpt_dict[senid]

            for bunsetsu, pred_id_dict in pred_bunsetsu_dict.items():
                # KNPのpredとchatgptのpredとの比較
                
                if bunsetsu in crr_bunsetsu_dict:
                    count_dict['pred']['csout'] += 1

                    # chatGPとKNPのPredの一致をとる
                    chatgpt_case_list = []
                    for chatbun, clist in chatgpt_sen_dict2.items():
                        cmatch_type = eu_strmatch.ret_match_type(bunsetsu, chatbun)
                        if chatbun == bunsetsu or ( not cmatch_type == 'not match'):
                            chatgpt_case_list = clist
                            break

                    for pred_id, subdict in pred_id_dict.items():
                        
                        if pred_id in crr_bunsetsu_dict[bunsetsu]:
                            crr_case_dict = crr_bunsetsu_dict[bunsetsu][pred_id]['case']
                            
                            for gr, case_list in subdict['case'].items():
                                # KNPの出力の各格について、

                                for sys_out_dict in case_list:
                                    sstr = sys_out_dict['surface']
                                    stid = sys_out_dict['target_id']
                                    rel_type3 = eu_count.ret_rel_type_from_dict(sys_out_dict)
                                    
                                    # 正解と付き合わせて正解/不正解を判定する
                                    check_flag = False
                                    match_flag = False
                                    chatgpt_flag = False

                                    print(f"start line {gr} {sstr}")
                                    print(["Initial", gr, chatgpt_flag, check_flag, match_flag])
                                    if gr in crr_case_dict:
                                        print(f"start, {gr}")
                                        print(["gr", gr, chatgpt_flag, check_flag, match_flag])
                                        crr_list = crr_case_dict[gr]
                                        chatgpt_case_elem_string = ''
                                        for chat_elem_dict in chatgpt_case_list:
                                            chatgpt_case_elem_string = chat_elem_dict[gr]
                                            for crr_case_elem_dict in crr_list:
                                                cstr = crr_case_elem_dict['surface']
                                                cmatch_type = eu_strmatch.ret_match_type(cstr, chatgpt_case_elem_string)
                                                print(["correct vs chatgpt",  cmatch_type, cstr, chatgpt_case_elem_string, 'knp', crr_list])
                                                # print(f"ChatGPT {cstr} {gr} {chatgpt_case_elem_string} {cmatch_type} {crr_bun}")
                                                if not cmatch_type == 'not_match':
                                                    chatgpt_flag = True
                                            
                                            if chatgpt_flag == True:
                                                break
                                        print(["chatgpt_over", gr, chatgpt_flag, check_flag, match_flag])

                                        for crr_case_elem_dict in crr_list:
                                            cstr = crr_case_elem_dict['surface']
                                            ctid = crr_case_elem_dict['target_id']
                                            crr_rel_type3 = eu_count.ret_rel_type_from_dict(crr_case_elem_dict)

                                            match_type = eu_strmatch.ret_match_type(cstr, sstr)
                                            
                                            print(["correct vs knp",  gr, match_type, cstr, sstr])
                                            # print(f"KNP {cstr} {gr} {sstr} {match_type} {crr_bun}")
                                            if stid == ctid and rel_type3 == crr_rel_type3:
                                                check_flag = True
                                                break
                                            # if not match_type == 'not_match':
                                            if not match_type == 'not_match':
                                                match_flag = True

                                            if not match_type == 'not_match' and rel_type3 == crr_rel_type3:
                                                check_flag = True
                                                break
                                        
                                        print(["knp_over", gr, chatgpt_flag, check_flag, match_flag])

                                    if check_flag == True:
                                        count_dict[gr]['csout'] += 1
                                        rel_count_dict[rel_type3][gr]['csout'] += 1
                                    elif match_flag == True:
                                        count_dict[gr]['csout'] += 1
                                    elif check_flag == False and match_flag == False:
                                        pass
                                    
                                    if chatgpt_flag == True and ( match_flag == True or check_flag == True):
                                        stat_dict['resolution']['even'] += 1
                                        print(["resolution even", gr, 'KNP', [chatgpt_flag, match_flag, check_flag], case_list, 'ChatGPT', chatgpt_case_list, 'Correct', crr_case_dict])
                                    elif chatgpt_flag == False and ( match_flag == True or check_flag == True) :
                                        stat_dict['resolution']['lost'] += 1
                                        print(["resolution lost", gr, 'KNP', [chatgpt_flag, match_flag, check_flag], case_list, 'ChatGPT', chatgpt_case_list, 'Correct', crr_case_dict])
                                    elif chatgpt_flag == True and ( match_flag == False and check_flag == False):
                                        stat_dict['resolution']['gain'] += 1
                                        print(["resolution gain", gr, 'KNP', [chatgpt_flag, match_flag, check_flag], case_list, 'ChatGPT', chatgpt_case_list, 'Correct', crr_case_dict])
                                    elif chatgpt_flag == False and (match_flag == False and check_flag == False):
                                        stat_dict['resolution']['difficult'] += 1
                                        print(["resolution difficult", gr, 'KNP', [chatgpt_flag, match_flag, check_flag], case_list, 'ChatGPT', chatgpt_case_list, 'Correct', crr_case_dict])

                for pred_id, sub_dict in pred_id_dict.items():
                    for gr, gr_list in sub_dict['case'].items():
                        for tmp_dict in gr_list:
                            rel_dist = tmp_dict['rel_dist']
                            rel_type = tmp_dict['rel_type']
                            if rel_type == 'zero':
                                rel_type = f'{rel_type}_{rel_dist}' 
                            rel_count_dict[rel_type][gr]['sout'] += 1
                            count_dict[gr]['sout'] += 1
                count_dict['pred']['sout'] += 1
        
        # print([count_dict])
        return count_dict, rel_count_dict


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
            count_dict[gr] = eu_count.ret_init_eval_count_dict()
                

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
                    rel_count_dict[type1][gr] = eu_count.ret_init_eval_count_dict()
        
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
                        pred_check = eu_strmatch.ret_match_type(crr_pred_str, gpt_pred_str)
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
                                    
                                    check = eu_strmatch.ret_match_type(crr_target, gpt_target_str)

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
        start_flag = False
        rlist = []
        for tidx, line in enumerate(lines):
            match = self.table_regexp.match(line)
            sennum_match = self.sennum_regexp.match(line)
            if sennum_match:
                start_flag = True
            if match:
                if tidx > 1 or start_flag == True:
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


    def evaluate_knp(self, knp_pred_dict, train_test_id_dict, org_dict, knp_pasa_result_dict, knp_type, phase, dir1):
        
        ok_pred_content_dict, result_compose_dict, _ = self.ret_result_dict_series(dir1)
        stat_dict = {}
        for exp_name, ok_pred_content_dict1 in ok_pred_content_dict.items():
            
            print(f"----- Start Evaluation {exp_name} -----")
            eval_result_dict = box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict1, phase, exp_name)
            stat_dict[exp_name] = eval_result_dict['all']['f1_score']
            print(f"----- End Of Evaluation {exp_name} -----")

        print(stat_dict)
        # 辞書を値でソートされたタプルのリストに変換する
        sorted_items = sorted(stat_dict.items(), key=lambda x: x[1])

        # ソートされた結果を出力
        for key, value in sorted_items:
            print(key, value)

        chat_gpt_dict = {}
        for id1, conversation in ok_pred_content_dict['zero-shot-modify-knp'].items():
                org_one_dict = org_dict[id1]
                case_lines = self.parse_conversation(org_one_dict, conversation)
                if not id1 in chat_gpt_dict:
                    chat_gpt_dict[id1] = {}
                for chat_elem in case_lines:
                    senid = chat_elem['senid']
                    if not senid in chat_gpt_dict[id1]:
                        chat_gpt_dict[id1][senid] = {}
                    
                    cpred = chat_elem['pred']
                    if not cpred in chat_gpt_dict[id1][senid]:
                        chat_gpt_dict[id1][senid][cpred] = []
                    chat_gpt_dict[id1][senid][cpred].append(chat_elem)

        # 見せてもらおうか。KNPの項構造解析能力の性能とやらを。
        lcount = 0
        count_dict = {}
        for gr in self.case_list:
            count_dict[gr] = eu_count.ret_init_eval_count_dict()
        
        rel_count_dict = eu_count.ret_init_rel_count_dict(self.case_list, self.rel_type_list, self.rel_dist_list)

        json_open = open('./intermediate_data/knp_pred_ana2.json', 'r')
        knp_pred_ana_dict = json.load(json_open) 

        def ret_stat_dict():
            return {'gain':0, 'lost':0, 'even': 0, 'difficult': 0}
        
        def ret_new_one():
            return {'subj':0, 'obj':0, 'obl': 0}

        stat_dict = {'pred': ret_stat_dict(), 'case': ret_stat_dict(), 'resolution': ret_stat_dict(), 'new_one': ret_new_one() }

        exist_5_id_list = ['w201106-0002000003', 'w201106-0002000000', 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']

        for id in train_test_id_dict[phase]:
            knp_pred = knp_pred_dict[id]
            org_one_dict = org_dict[id]
            chatgpt_one_dict = chat_gpt_dict[id]
            
            if id in knp_pasa_result_dict:
                
                if not id in exist_5_id_list:
                    # continue
                    pass

                pasa_dict = knp_pred_ana_dict[id]
                # pasa_dict = knp_pasa_result_dict[id]

                sen_count_dict, sen_rel_count_dict = self.ret_knp_count_dict(knp_pred, org_one_dict, pasa_dict, chatgpt_one_dict, stat_dict, knp_type)
                for case_str, count_key_dict in sen_count_dict.items():
                    for cout_key, freq in count_key_dict.items():
                        count_dict[case_str][cout_key] += freq
                        if not case_str == 'pred':
                            count_dict['all'][cout_key] += freq

                for reltype, subdict in sen_rel_count_dict.items():
                    for case_str, count_key_dict in subdict.items():
                        for cout_key, freq in count_key_dict.items():
                            rel_count_dict[reltype][case_str][cout_key] += freq
                            rel_count_dict[reltype]['all'][cout_key] += freq
                
                lcount += 1
        
        self.show_error_num()

        pp.pprint(count_dict)
        eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(count_dict)
        pp.pprint(eval_result_dict)
        
        print("----")
        pp.pprint(rel_count_dict)
        detail_eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(rel_count_dict)
        pp.pprint(detail_eval_result_dict)
        print([lcount, float(lcount)/float(len(train_test_id_dict[phase]))])

        print(stat_dict)


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
        

    def evaluate(self, knp_pred_dict, train_test_id_dict, org_dict, result_dict, phase, exp_name):
        """ChatGPTの結果と正解データとの結果を比較するメソッド"""
        lcount = 0
        count_dict = eu_count.ret_init_count_dict(self.case_list)
        detail_count_dict = {}
        st = ['w201106-0002000003', 'w201106-0002000000', 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']
        for id in train_test_id_dict[phase]:
            
            #if not id in st:
            #    continue

            knp_pred = knp_pred_dict[id]
            org_one_dict = org_dict[id] 
            
            if id in result_dict:
                conversation = result_dict[id]
                case_lines = self.parse_conversation(org_one_dict, conversation)
                
                count_dict1 = self.ret_count_dict(knp_pred, org_one_dict, case_lines)
                # pp.pprint(count_dict1)
                for case_str, count_sub_dict in count_dict1.items():
                    for count_type, freq in count_sub_dict.items():
                        count_dict[case_str][count_type] += freq
                
                crr_pred_dict, _ = prompt_util.ret_table_row_dict(knp_pred)
                
                if self.verbose == True:
                    print(f"----- {id} 本文 -----")
                    pp.pprint(org_one_dict)
                    print(f"----- {id} 出力 -----")
                    print(conversation)
                    pp.pprint(case_lines)
                    print(f"----- {id} 正解 -----")
                    pp.pprint(crr_pred_dict)
                    print(f"----- {id} カウント -----")
                    pp.pprint(count_dict1)

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
        
        eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(count_dict)
        if self.verbose == True:
            print("----- 精度カウント -----")
            pp.pprint(count_dict)
            pp.pprint(eval_result_dict)
        
        table_line = self.ret_eval_simple_table_line(exp_name, eval_result_dict)
        print(table_line)

        return eval_result_dict
        

        # Detailは後回し
        # pp.pprint(detail_count_dict)
        # detail_eval_result_dict = eval_util_evaluation.ret_evaluation_result_dict(detail_count_dict)
        # pp.pprint(detail_eval_result_dict)
        # table_line = self.ret_eval_detail_table_line(detail_eval_result_dict)
        # print(table_line)
    

    def _round_to_significant_digits(self, number, digits):
        # 数値を指定した桁数に丸める関数
        return round(number, digits)

    
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
            # rows = ['', key, cstr, str(p1), str(r1), str(f1), '']
            rows = ['', key, str(f1), '']
            row_line = '|'.join(rows)
            rlist.append(row_line)
            key_count += 1
        return rlist

    def _ret_eval_head_lines(self):
        rows = ['', '述語との距離関係', '格要素','Precision', 'Recall','F1スコア', '']
        row_line = '|'.join(rows)
        tlines = [row_line]
        return tlines

    def ret_eval_simple_table_line(self, exp_name, dict1):
        tlines = self._ret_eval_head_lines()
        tlines = []
        clist = ['all', 'subj', 'obj', 'obl', 'pred']
        # print(dict1)
        for row_line in self._ret_eval_table_row_line(exp_name, dict1, clist):
            tlines.append(row_line)
            break
            
        return '\n'.join(tlines)

    def ret_eval_detail_table_line(self, dict1):
        tlines = self._ret_eval_head_lines()
        clist = ['subj', 'obj', 'obl', 'all']
        for key1, ctype_f1values in dict1.items():
            for row_line in self._ret_eval_table_row_line(key1, ctype_f1values,clist):
                tlines.append(row_line)
            
        return '\n'.join(tlines)


    def ret_result_dict_series(self, dirname):
        ok_pred_content_dict = {}
        result_compose_dict = {}
        input_dict = {}
        ok_results_list = glob.glob(f'./{dirname}/*.json')
        for file1 in ok_results_list:
            self.set_result_dict_series(file1, ok_pred_content_dict, result_compose_dict, input_dict)
        # print(ok_pred_content_dict)
        return ok_pred_content_dict, result_compose_dict, input_dict
    

    def set_result_dict_series(self, file1, ok_pred_content_dict, result_compose_dict, input_dict):
        json_open = open(file1, 'r')
        pred_dict = json.load(json_open) 

        for id1, res_dict in pred_dict.items():
            
            result = res_dict['result']

            for exp_name, response_list in result.items(): 

                conv_dict = response_list[-1]
                
                status = conv_dict['status']
                input = conv_dict['input']

                if not exp_name in result_compose_dict:
                    result_compose_dict[exp_name]= {}
                    
                if not id1 in result_compose_dict[exp_name]:
                    result_compose_dict[exp_name][id1] = {}

                if not status in result_compose_dict[exp_name][id1]:
                    result_compose_dict[exp_name][id1][status] = 0
                result_compose_dict[exp_name][id1][status] += 1

                if not exp_name in ok_pred_content_dict:
                    ok_pred_content_dict[exp_name] = {}

                if conv_dict['status'] == 'ok':
                    contents = conv_dict['response']["choices"][0]["message"]["content"]
                    ok_pred_content_dict[exp_name][id1] = contents

                if not exp_name in input_dict:
                    input_dict[exp_name] = {}
                input_dict[exp_name][id1] = input[0]['content']

def evaluate_extra(args, verbose_flag=False):

    def ret_case_elem_dict(line, pred):
        l = line.split(pred)
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
    
    sbox = SentenceParser()
    knp_pred_dict, train_test_id_dict, org_dict = tfu.ret_experimental_files()

    dir1 = args.td
    
    box = EvalConversation(verbose_flag=verbose_flag)
    ok_pred_content_dict, result_compose_dict, input_dict = box.ret_result_dict_series(dir1)

    print([len(ok_pred_content_dict), ok_pred_content_dict.keys(), result_compose_dict.keys()])
    for k,v in ok_pred_content_dict.items():
        # print(v)
        pass

    file1 = './workplace/prompt/knp_pred_elem_dict.json'
    json_open = open(file1, 'r')
    knp_pred_elem_dict = json.load(json_open) 
    phase = 'dev'
    knp_pred_new_dict = {}
    for exp_name, content_dict in ok_pred_content_dict.items():
        if not exp_name in knp_pred_new_dict:
            knp_pred_new_dict[exp_name] = {}

        for id1, content in content_dict.items():
            if not id1 in knp_pred_new_dict[exp_name]:
                knp_pred_new_dict[exp_name][id1] = {}

            pred_elem = knp_pred_elem_dict[id1]
            tmp_dict = {}
            for line in re.split('[？。]', content):
                for senid, pred_dict in pred_elem.items():

                    if not senid in tmp_dict:
                        tmp_dict[senid] = {}

                    for pred, case_dict in pred_dict.items():
                        if pred in line:
                            # sdict = sbox.parse(line)
                            # print([pred, sdict])
                            case_row_dict = ret_case_elem_dict(line, pred)
                            tmp_dict[senid][pred] = case_row_dict
                            prompt_util.ret_table_row_lines(tmp_dict) 
                    
            knp_pred_new_dict[exp_name][id1] = prompt_util.ret_table_row_lines(tmp_dict)
    # print(knp_pred_new_dict)
    # exit()
    # 実験設定ごとに精度を出すのだ。

    stat_dict = {}
    for exp_name, extra_dict1 in ok_pred_content_dict.items():
        # if not exp_name in stat_dict:
        # print(f"----- Start Evaluation {exp_name} -----")
        ok_pred_content_dict1 = knp_pred_new_dict[exp_name]
        eval_result_dict = box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict1, phase, exp_name)
        stat_dict[exp_name] = eval_result_dict['all']['f1_score']
        # print(f"----- End Of Evaluation {exp_name} -----")

    print(stat_dict)


def evaluate_each_experient(args, verbose_flag=False):

    knp_pred_dict, train_test_id_dict, org_dict = tfu.ret_experimental_files()

    dir1 = args.td
    box = EvalConversation(verbose_flag=verbose_flag)
    ok_pred_content_dict, result_compose_dict, _ = box.ret_result_dict_series(dir1)
    # 実験設定ごとに精度を出すのだ。
    # print(ok_pred_content_dict)

    # pp.pprint([ok_pred_content_dict, result_compose_dict])
    # print(len(ok_pred_content_dict), len(result_compose_dict))
    phase = 'dev'
    ok_ids = set()
    for exp_name, res_dict in result_compose_dict.items():
        ok_count = 0
        for id1, status_dict in res_dict.items():
            if 'ok' in status_dict:
                # if exp_name == 'zero-shot-simple':
                ok_ids.add(id1)
                ok_count += 1
            else:
                print(f"{id1}")
        print(["ok count", exp_name, ok_count])

    for id2 in train_test_id_dict[phase]:
        if not id2 in ok_ids:
            # print(id2)
            pass
    
    stat_dict = {}
    for exp_name, ok_pred_content_dict1 in ok_pred_content_dict.items():
        print(f"----- Start Evaluation {exp_name} -----")
        eval_result_dict = box.evaluate(knp_pred_dict, train_test_id_dict, org_dict, ok_pred_content_dict1, phase, exp_name)
        print(eval_result_dict)
        stat_dict[exp_name] = eval_result_dict['all']['f1_score']
        print(f"----- End Of Evaluation {exp_name} -----")

    print(stat_dict)
    # 辞書を値でソートされたタプルのリストに変換する
    sorted_items = sorted(stat_dict.items(), key=lambda x: x[1])

    # ソートされた結果を出力
    for key, value in sorted_items:
        print(key, value)

def analysis():
    knp_pred_dict, train_test_id_dict, org_dict = tfu.ret_experimental_files()

    exp_name = 'trial'
    dirname = f'./result/dev1/{exp_name}'
    
    box = EvalConversation()
    ok_pred_content_dict, result_compose_dict = EvalConversation.ret_result_dict_series(dirname)
    

if __name__=="__main__":
    # evaluate()
    args = optu.get_eval_option()
    verbose_flag = False
    if args.verbose == 'yes':
        verbose_flag = True

    knp_pred_dict, train_test_id_dict, org_dict = tfu.ret_experimental_files()
    json_open = open('./intermediate_data/knp_pred_ana2.json', 'r')
    knp_pred_ana_dict = json.load(json_open) 
    dir1 = args.td
    # pp.pprint(knp_pred_ana_dict)

    if args.process == 'evaluation':
        evaluate_each_experient(args, verbose_flag=verbose_flag)
    elif args.process == 'knp':
        dir1 = args.td
        knp_type = args.kt
        box = EvalConversation(verbose_flag=verbose_flag)
        box.evaluate_knp(knp_pred_dict, train_test_id_dict, org_dict, knp_pred_ana_dict, knp_type, 'dev', dir1)
    
    elif args.process == 'extra':
        evaluate_extra(args, verbose_flag=verbose_flag)
    