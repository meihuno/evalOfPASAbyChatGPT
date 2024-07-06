# orgの取得、idと文のlistで保持
import re
import glob
import os
import pprint as pp
import json
import lib.option_util as opu
from lib.json_read_write import JsonReadWrite
# KWDLC/org/w201106-00000/w201106-0000069777.org
BASE_DIR = './'
rel_tag_pattern = re.compile(r'(\w+)="([^"]+)"')

from pyknp import KNP

class KNPDataLoader(object):
    """KNPのデータを中間データとして加工してintermediate_dataに保存する"""
    def __init__(self):
        self.target_case_dict = {'ガ': '主語', 'ガ２': '主語', 'ヲ' : '目的語', 'ニ' : 'ニ格'} 
        self.connector_morph_list = ['助詞']

    def _ret_bun_dict(self, link_num=-1, dep_type='D'):
        dep_bun_dict = {'link': link_num,  'dep_type':dep_type, 'words': []}
        return dep_bun_dict

    def _ret_rel_dict(self, rel_tag):
        rdict = {}
        match = rel_tag_pattern.findall(rel_tag)
        tag_dict = dict(match)
        return tag_dict

    def _ret_rel_tag_elem_list(self, tags):
        rel_tags = re.findall('<rel\s.*?\/>', tags)
        #p_tags = re.find(<項構造:ガ/江戸川太郎/1>)
        rlist = []
        if rel_tags:
            for rel_tag in rel_tags: 
                tag_dict = self._ret_rel_dict(rel_tag)
                if 'mode' in tag_dict:
                    if tag_dict['mode'] == '？':
                        pass
                rlist.append(tag_dict)
        return rlist

    def _ret_pasa_tag_elem_list(self, tags):
        pasa_tags = re.findall('<項構造:(.*?)>', tags)
        #p_tags = re.find(<項構造:ガ/江戸川太郎/1>)
        rlist = []
        if pasa_tags:
            for pasa_tag in pasa_tags: 
                pasa_list = pasa_tag.split(';')
                for pelem in pasa_list:
                    plist = pelem.split('/')
                    type1 = plist[0]
                    target = plist[1]
                    id = plist[2] 
                    tag_dict = {'type': type1, 'target': target, 'sid': None, 'id': id, 'origin': 'anaphora'}
                    rlist.append(tag_dict)
        return rlist

    def _ret_ne_tag_elem_list(self, tags):
        ne_tags = re.findall('<NE:(.*?):(.*?)>', tags)
        rlist = []
        if ne_tags:
            for ne_tag in ne_tags:
                ne_attr = ne_tag[0]
                ne_str = ne_tag[1]
                ne_tag_dict = {'attr': ne_attr, 'surface': ne_str}
                rlist.append(ne_tag_dict)
        return rlist

    def _ret_eid_tag_elem_list(self, tags):
        eid_tags = re.findall('<EID:(.*?)>', tags)
        type1 = 'unknown'
        if eid_tags:
            type1 = eid_tags[0]
        if '<体言>' in tags:
            type1 = '体言'
        elif '<用言:動>' in tags:
            type1 = '用言:動詞'
        elif '<用言:判>' in tags:
            type1 = '用言:判'
        # <EID:3><項構造:ガ/江戸川太郎/1>
        rlist = []
        if eid_tags:
            for eid_num in eid_tags:
                eid_tag_dict = {'attr': 'EID', 'eid': eid_num, 'type1': type1}
                rlist.append(eid_tag_dict)
        return rlist

    def _ret_target_rel_list(self, rel_list):
        rlist = []
        for rel_dict in rel_list:
            if 'type' in rel_dict:
                for case, pred in self.target_case_dict.items():
                    if rel_dict['type'] == case:
                        rlist.append(rel_dict)
        return rlist

    def _ret_case_type(self, conn_list):
        rstr = 'none'
        return rstr
    # editting
    def _ret_bunsetsu_surface_and_connector_dict(self, bun, elem_id, sid):
        term_list = []
        conn_list = []
        case_marker_list = []
        case_marker_flag = False
        in_flag = True
        for word in bun['words']:
            wl = word.split()
            sstr = wl[0]
            morph = wl[3]
            morph_detail = wl[5]
            info = wl[-1]
            if info == 'NIL':
                in_flag = False
            
            if in_flag == True:
                term_list.append(sstr)
            elif in_flag == False:
                if morph == '特殊':
                    break
                elif morph == '助詞':
                    if morph_detail == '格助詞':
                        case_marker_flag = True
                    case_marker_list.append(sstr)
                else:
                    conn_list.append(sstr)

        target = ''.join(term_list) 
        if case_marker_flag == True:
            type1 = case_marker_list[0]
        elif len(case_marker_list) > 0:
            type1 = ''.join(case_marker_list)
        else:
            type1 = ''.join(conn_list)

        tag_dict = {'type': type1, 'target': target, 'sid': sid, 'id': elem_id, 'origin': 'dep'}
        return tag_dict

    def _ret_dep_elem_dict(self, link_num=-1, dep_type='D', tags='', sen_id='dummy'):
        dep_elem_dict = {
            'sen_id': sen_id, 
            'link': link_num,  
            'dep_type':dep_type, 
            'words': [], 
            'rel_list': [], 
            'ne_list': [], 
            'eid_list': [],
            'pasa_list': [],
            'dep_list': [],
            'preds' : [] 
        }
        rel_tags = self._ret_rel_tag_elem_list(tags)
        ne_tags = self._ret_ne_tag_elem_list(tags)
        eid_tags = self._ret_eid_tag_elem_list(tags)
        pasa_tags = self._ret_pasa_tag_elem_list(tags)
        dep_elem_dict['rel_list'] = rel_tags
        dep_elem_dict['ne_list'] = ne_tags
        dep_elem_dict['eid_list'] = eid_tags
        dep_elem_dict['pasa_list'] = pasa_tags

        return dep_elem_dict

    def _ret_word_surface(self, elem_tmp_dict):
        rlist = []
        for line in elem_tmp_dict['words']:
            lines = line.split()
            surface = lines[0]
            rlist.append(surface)
        rstr = ''.join(rlist)
        return rstr

    def _ret_main_term_surface(self, elem_tmp_dict):
        rlist = []
        break_flag = False
        for line in elem_tmp_dict['words']:
            lines = line.split()
            surface = lines[0]
            morph = lines[3]
            if morph in self.connector_morph_list:
                break
            else:
                rlist.append(surface)
        rstr = ''.join(rlist)
        return rstr
    
    def ret_pred_case_dict(self, sid, line_dict, dep_dict, elem2dep_dict, elem2dep_dict2=None, eid2elem_dict=None):
        """
        KNPのタグつけデータをタグ情報を格納した辞書の配列に変換して返すメソッド。
        -------
        本スクリプトの中心部である。
        """
        
        rlist = []
        # +行の要素が回る。pred_idは行番号
        for pred_id, elem_tmp_dict in line_dict.items():
            
            # タグが所属している文節のid
            bunsetsu_id = elem2dep_dict[pred_id]
            bunsetsu = dep_dict[bunsetsu_id]
            bunsetsu_str = self._ret_word_surface(bunsetsu)
            # 行の係り先のタグ
            pred_link_num = int(elem_tmp_dict['link'])
            # 文節の係り先の文節
            pred_bunsetsu_link_num = int(bunsetsu['link'])

            # 関係
            rel_list = elem_tmp_dict['rel_list']
            target_rel_list = self._ret_target_rel_list(rel_list)
            predstr = self._ret_main_term_surface(elem_tmp_dict)

            does_pred_have_relation_flag = False
            # 以下は行に付与されてるタグ
            # for target_elem_dict in target_rel_list:
            for target_elem_dict in rel_list:
                surface_case = target_elem_dict['type']
                target = target_elem_dict['target']
                origin = target_elem_dict['origin']

                if surface_case in self.target_case_dict:
                    grammatical_role = self.target_case_dict[surface_case]
                else:
                    grammatical_role = 'not set'
                
                # print(target_elem_dict)
                # target_dictの格要素が係り受けしていないならゼロ。
                # 同文内にあれば、intra、文外ならばinter、さらに文章外なら外界照応
                rel_dist = 'intra_sentence'
                target_sid = 'none'
                if 'sid' in target_elem_dict:
                    target_sid = target_elem_dict['sid']
                    if not target_sid.startswith('S-ID:'):
                        target_sid = 'S-ID:' + target_sid
                    
                    if not sid == target_sid:
                        rel_dist = 'inter_sentence'
                else:
                    rel_dist = 'outer'

                # 例えば、「行う」の行の「俺たち」targetを処理
                rel_type = 'none'
                target_id = -1
                if 'id' in target_elem_dict and rel_dist == 'intra_sentence':
                    # この id が同じ文内にある
                    target_id = int(target_elem_dict['id'])
                    
                    if not eid2elem_dict is None:
                        if target_id in eid2elem_dict:
                            target_id = eid2elem_dict[target_id]
                    
                    elem2dep = elem2dep_dict
                    # if not elem2dep_dict2 is None:
                    #    elem2dep = elem2dep_dict2

                    if target_id in elem2dep:
                        # targetの文節。俺たち。
                        target_bunsetsu_id = elem2dep[target_id]

                        if target_bunsetsu_id in dep_dict:
                            link_dep_dict = dep_dict[target_bunsetsu_id]
                            if 'link' in link_dep_dict:
                                target_bunsetsu_link_num = int(link_dep_dict['link'])
                                link_bunsetsu_str = self._ret_word_surface(link_dep_dict)
                                if target_bunsetsu_id == bunsetsu_id:
                                    rel_type = 'same_bunsetsu'
                                elif target_bunsetsu_link_num == bunsetsu_id:
                                    rel_type = 'dep'
                                elif pred_bunsetsu_link_num == target_bunsetsu_id:
                                    rel_type = 'rentai'
                                else:
                                    rel_type = 'zero'
                
                if rel_type == 'none' and rel_dist == 'outer':
                    # ターゲットが文IDがないなら文章外でゼロ代名詞
                    rel_type = 'zero'
                elif rel_type == 'none' and rel_dist == 'inter_sentence':
                    # ターゲットが文IDがありPredの文IDと異なるなら文間照応でゼロ代名詞
                    rel_type = 'zero'
                
                # elem2dep_dictのid番号が足りんのでは？
                # eid で id を セットするのがそもそもいかんのでは？ eidは行番号ではない故に
                # あと番号ずれてますね。EIDは順番に付与されているわけではないな。
                # であれば、eid と token idとの対応表を準備すればよい！
                if rel_type == 'none':
                    pp.pprint(["Endless none", sid, rel_type, surface_case, target, predstr, target_elem_dict, elem2dep_dict, elem2dep])
                
                gr_dict = {
                    'surface_case': surface_case, 
                    'gr': grammatical_role, 
                    'rel_dist': rel_dist,
                    'rel_type': rel_type,  
                    'pred': predstr, 
                    'pred_bunsetsu' : bunsetsu_str,
                    'target': target,
                    'target_sid': target_sid,
                    'target_id': target_id,
                    'pred_id': pred_id,
                    'origin': origin
                    }
                does_pred_have_relation_flag = True
                rlist.append(gr_dict)

        if does_pred_have_relation_flag == False:
            if len(elem_tmp_dict['eid_list']) > 0:
                if '用言:動詞' in elem_tmp_dict['eid_list'][0]['type1']:
                    # pp.pprint(["yougen?", elem_tmp_dict])
                    gr_dict = {
                        'surface_case': 'empty',
                        'gr': 'none',
                        'rel_dist': [],
                        'rel_type': 'none',  
                        'pred': predstr, 
                        'pred_bunsetsu' : bunsetsu_str,
                        'target': 'empty',
                        'target_sid': 'none',
                        'target_id': -9999,
                        'pred_id': pred_id,
                        'origin': 'unknown'
                        }
                    rlist.append(gr_dict)
                # exit()
        return rlist

    def parse_knp_sentence_lines(self, f, line):
        """
        KNPファイルをパースしてタグ要素、文節の情報を格納した辞書を返す。1文単位の処理を行なっている。
        -------
        """
        dep_dict = {}
        # dep2elem_dict = {}
        elem2dep_dict = {}
        elem_dict = {}
        eid2elemdict = {}

        bun_index = -1
        elem_index = -1

        list1 = line.split()
        sid = list1[1]
        line2 = f.readline()
        bun_rlink_dict = {}
        bundep_type_dict = {}
        bun2elem_dict = {}

        elem_rlink_dict = {}
        elemdep_type_dict = {}

        while line2:
            line2 = line2.strip()
            dep_match = re.findall('\*\s([-0123456789]+)([A-Z])', line2)
            tag_line_match = re.findall('\+\s([-0123456789]+)([A-Z])\s*(.*)$', line2)
            if dep_match:
                link_num = dep_match[0][0]
                dep_type = dep_match[0][1]
                
                bun_index += 1
                
                # 文節の係りうけ関係を保持する
                link_num_int = int(link_num)
                if not link_num_int in bun_rlink_dict:
                    bun_rlink_dict[int(link_num_int)] = []
                #if not bun_index == -1:
                bun_rlink_dict[link_num_int].append(bun_index)
                bundep_type_dict[bun_index] = {'dep_type': dep_type, 'link_num': link_num_int}

                dep_dict[bun_index] = self._ret_bun_dict(link_num=link_num, dep_type=dep_type)
            # anaphora処理で付与した結果が格納される。
            # では、普通の文節の係り受けを格納するにはどうしたらいいのか？
            # 係り元の、係り先を把握する必要がある。
            elif tag_line_match:
                id_num = tag_line_match[0][0]
                id_dep_type = tag_line_match[0][1]
                id_tag = tag_line_match[0][2]
                # eid_list = re.findall('<EID:(.*?)>')
                elem_index += 1

                elink_num_int = int(id_num)
                if not elink_num_int in elem_rlink_dict:
                    elem_rlink_dict[int(elink_num_int)] = []
                #if not bun_index == -1:
                elem_rlink_dict[elink_num_int].append(elem_index)
                elemdep_type_dict[elem_index] = {'dep_type': id_dep_type, 'link_num': elink_num_int}

                dep_elem_dict1 = self._ret_dep_elem_dict(link_num=id_num, dep_type=id_dep_type, tags=id_tag, sen_id=sid)
                for eid_dict1 in dep_elem_dict1['eid_list']:
                    eid1 = eid_dict1['eid']
                    eid2elemdict[int(eid1)] = elem_index
                elem_dict[elem_index] = dep_elem_dict1
                elem2dep_dict[elem_index] = bun_index
                if not bun_index in bun2elem_dict:
                    bun2elem_dict[bun_index] = []
                bun2elem_dict[bun_index].append(elem_index)

            elif line2 == 'EOS':
                break
            else:
                dep_dict[bun_index]['words'].append(line2)
                elem_dict[elem_index]['words'].append(line2)
                pass
            line2 = f.readline()
                
        # 0 と 1 の elem_indexの文節IDをひく
        print(elem_rlink_dict)
        for bidx, modb_idx_list in elem_rlink_dict.items():
            
            for modb_idx in modb_idx_list:
                link_num = bidx
                dep_type =  elemdep_type_dict[modb_idx]['dep_type']
                # 文節情報にアクセス
                # 同じ文節内 か 別の文節か 判定する
                if bidx > 0: # -1を回避
                    mod_bun_idx = elem2dep_dict[modb_idx]
                    bmod_bun_idx = elem2dep_dict[bidx]
                    if mod_bun_idx == bmod_bun_idx:
                        # 複合名詞
                        pass
                    else:
                        bun = dep_dict[mod_bun_idx]
                        tmp_dict = self._ret_bunsetsu_surface_and_connector_dict(bun, modb_idx, sid)
                        elem_dict[bidx]['dep_list'].append(tmp_dict)

        # pp.pprint(elem_dict)

        return dep_dict, elem_dict, elem2dep_dict, eid2elemdict

    def parse_knp_file(self, filename):
        """
        KNPファイルをパースしてタグ要素、文節の情報を格納した辞書を返す。
        """
        knp_elem_dict = {}
        knp_pred_dict = {}
        knp_dep_dict = {}
        knp_elem2dep_dict = {}
        knp_eid2elem_dict = {}

        filekey = os.path.basename(filename).split('.')[0]
        with open(filename, "r", encoding='utf-8') as f:
            
            line = f.readline()
            sid = 'dummy'
            while line:
                # ここに処理内容を記述します
                line = line.strip()
                match = re.findall('#\sS\-ID:', line)
                # ここからが1文ごとの処理
                if match:
                    sentence_head_list = line.split()
                    sid = sentence_head_list[1]
                    dep_dict, elem_dict, elem2dep_dict, eid2elem_dict = self.parse_knp_sentence_lines(f, line)
                    # 一巡目
                    pred_case_dict = self.ret_pred_case_dict(sid, elem_dict, dep_dict, elem2dep_dict)
                    knp_dep_dict[sid] = dep_dict
                    knp_elem2dep_dict[sid] = elem2dep_dict
                    knp_elem_dict[sid] = elem_dict
                    knp_pred_dict[sid] = pred_case_dict
                    knp_eid2elem_dict[sid] = eid2elem_dict
                # 次の行を読み込みます
                line = f.readline()
        
        # pasa_list の senidのセット
        eid2senid_dict = {}
        for senid, elem_dict1 in knp_elem_dict.items():
            for num, num_dict1 in elem_dict1.items():
                for eid_dict in num_dict1['eid_list']:
                    eid = eid_dict['eid']
                    eid2senid_dict[eid] = senid

        knp_inc_elem2dep_dict = {}
        eid_inc = 0
        einc = 0
        for senid, elem2dep_dict1 in knp_elem2dep_dict.items():
            tmp_elem2dep_dict = {}
            for eid, bunsetsu_dep in elem2dep_dict1.items():
                tmp_elem2dep_dict [ eid + eid_inc ] = bunsetsu_dep
                einc = eid
            eid_inc = eid_inc + einc + 1
            knp_inc_elem2dep_dict[senid] = tmp_elem2dep_dict

        # print(eid2senid_dict)
        for senid, elem_dict1 in knp_elem_dict.items():
            for num, num_dict1 in elem_dict1.items():
                for pasa_dict in num_dict1['pasa_list']:
                    pasa_dict['sid'] = eid2senid_dict[pasa_dict['id']]
                # rel_listが空であれば（正解のタグがなく、anaphoraのタグしかない）、rel_listをpasa_listで置き換えている
                # ここにdepやlistとanaphora由来のlistを投入する
                if len(num_dict1['rel_list']) == 0:
                    for tmp_dict in num_dict1['pasa_list']:
                        num_dict1['rel_list'].append(tmp_dict)
                    for tmp_dict in num_dict1['dep_list']:
                        num_dict1['rel_list'].append(tmp_dict)

        for senid, elem_dict1 in knp_elem_dict.items():
            elem2dep_dict1 = knp_elem2dep_dict[senid]
            elem2dep_dict2 = knp_inc_elem2dep_dict[senid]
            eid2elem_dict1 = knp_eid2elem_dict[senid] 
            dep_dict1 = knp_dep_dict[senid]
            # 2巡目
            pred_case_dict1 = self.ret_pred_case_dict(senid, elem_dict1, dep_dict1, elem2dep_dict1, elem2dep_dict2, eid2elem_dict1)
            # 置き換え
            knp_pred_dict[senid] = pred_case_dict1
        return filekey, knp_elem_dict, knp_pred_dict


    def _delete_sid_prefix(self, original_string):
        prefix = "S-ID:"
        if original_string.startswith(prefix):
            result = original_string[len(prefix):]
        else:
            result = original_string

        return result

    def ret_knp_dict(self, knp_key='./KWDLC/knp/*/*.knp'):
        """
        KWDLC/knp下の*.knpファイルからタグつけ情報と係り受け情報を辞書に格納して返す
        ------
        タグ情報を格納したknp_dictの構成

        係り受け情報をdep_dictの構成

        """
        glob_key = BASE_DIR +  knp_key
        knp_list1 = glob.glob(glob_key)
        knp_dict = {}
        dep_dict = {}
        count = 0
        
        for filename in knp_list1:
            filekey, knp_tmp_dict, knp_pred_dict = self.parse_knp_file(filename)
            # pred_case_dict = self.ret_pred_case_dict(knp_tmp_dict)
            knp_dict[filekey] = knp_tmp_dict
            dep_dict[filekey] = knp_pred_dict
        return knp_dict, dep_dict


def convert_knp_json():
    box = KNPDataLoader()
    knp_dict, pred_dict = box.ret_knp_dict()
    print(pred_dict)
    exit()
    BASE_DIR = './intermediate_data/'
    orgjsonfile = 'knp1.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, knp_dict)

    orgjsonfile = 'knp_pred1.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, pred_dict)

def make_test_json_date():
    knp_key='./test/data/*.knp'
    box = KNPDataLoader()
    knp_dict, pred_dict = box.ret_knp_dict(knp_key=knp_key)
    
    BASE_DIR = './test/data/'
    orgjsonfile = 'knp1.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, knp_dict)

    orgjsonfile = 'knp_pred1.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, pred_dict)

def parse_anaphora(knp_file='knp_ana2.json', 
                    pred_file='knp_pred_ana2.json', 
                    knp_key ='./workplace/knp/*/*.knp', 
                    base_dir='./intermediate_data/'):

    box = KNPDataLoader()
    knp_dict, pred_dict = box.ret_knp_dict(knp_key=knp_key)
    
    BASE_DIR = base_dir
    JsonReadWrite.write_json(BASE_DIR, knp_file, knp_dict)
    JsonReadWrite.write_json(BASE_DIR, pred_file, pred_dict)


if __name__=="__main__":

    # parse_anaphora()
    # exit()
    args = opu.get_parse_option()
    
    knp_key = args.knppat
    output_dir = args.od
    knp_file = args.depfile
    pred_file = args.predfile

    if args.process == 'parse':
        convert_knp_json()
    elif args.process == 'test_date':
        make_test_json_date()
    elif args.process == 'parse_anaphora':
        parse_anaphora()
    elif args.process == 'pred':
        # parse_anaphora(knp_file=knp_file, pred_file=pred_file, knp_key = knp_key, base_dir = output_dir)
        parse_anaphora()
