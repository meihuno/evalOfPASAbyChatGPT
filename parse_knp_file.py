# orgの取得、idと文のlistで保持
import re
import glob
import os
import pprint as pp
import option_util as opu
from json_read_write import JsonReadWrite
# KWDLC/org/w201106-00000/w201106-0000069777.org
BASE_DIR = './'
rel_tag_pattern = re.compile(r'(\w+)="([^"]+)"')

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
        rlist = []
        if rel_tags:
            for rel_tag in rel_tags: 
                tag_dict = self._ret_rel_dict(rel_tag)
                # print(tag_dict)
                if 'mode' in tag_dict:
                    if tag_dict['mode'] == '？':
                        pass
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

    def _ret_target_rel_list(self, rel_list):
        rlist = []
        for rel_dict in rel_list:
            if 'type' in rel_dict:
                for case, pred in self.target_case_dict.items():
                    if rel_dict['type'] == case:
                        rlist.append(rel_dict)
        return rlist

    def _ret_dep_elem_dict(self, link_num=-1, dep_type='D', tags='', sen_id='dummy'):
        dep_elem_dict = {
            'sen_id': sen_id, 
            'link': link_num,  
            'dep_type':dep_type, 
            'words': [], 
            'rel_list': [], 
            'ne_list': [], 
            'preds' : [] 
        }
        rel_tags = self._ret_rel_tag_elem_list(tags)
        ne_tags = self._ret_ne_tag_elem_list(tags)
        dep_elem_dict['rel_list'] = rel_tags
        dep_elem_dict['ne_list'] = ne_tags

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
    
    def ret_pred_case_dict(self, sid, line_dict, dep_dict, elem2dep_dict):
        """
        KNPのタグつけデータをタグ情報を格納した辞書の配列に変換して返すメソッド。
        -------
        本スクリプトの中心部である。
        """
        rlist = []
        # +行の要素が回る。pred_idは行番号
        for pred_id, elem_tmp_dict in line_dict.items():
            rel_list = elem_tmp_dict['rel_list']
            # タグが所属している文節のid
            bunsetsu_id = elem2dep_dict[pred_id]
            bunsetsu = dep_dict[bunsetsu_id]
            bunsetsu_str = self._ret_word_surface(bunsetsu)
            # 行の係り先のタグ
            pred_link_num = int(elem_tmp_dict['link'])
            # 文節の係り先の文節
            pred_bunsetsu_link_num = int(bunsetsu['link'])

            target_rel_list = self._ret_target_rel_list(rel_list)
            predstr = self._ret_main_term_surface(elem_tmp_dict)
            
            # print(['OKK', pred_id, bunsetsu_id, elem_tmp_dict, pred_bunsetsu_link_num, bunsetsu])

            # 以下は行に付与されてるタグ
            for target_elem_dict in target_rel_list:
                surface_case = target_elem_dict['type']
                target = target_elem_dict['target']
                grammatical_role = self.target_case_dict[surface_case]
                
                # target_dictの格要素が係り受けしていないならゼロ。
                # 同文内にあれば、intra、文外ならばinter、さらに文章外なら外界照応
                # print(target_elem_dict)
                rel_dist = 'intra_sentence'
                target_sid = 'none'
                if 'sid' in target_elem_dict:
                    target_sid = 'S-ID:' + target_elem_dict['sid']
                    if not sid == target_sid:
                        # print(["target", sid, target_sid])
                        rel_dist = 'inter_sentence'
                else:
                    rel_dist = 'outer'

                rel_type = 'none'
                # 例えば、「行う」の行の「俺たち」targetを処理
                if 'id' in target_elem_dict and rel_dist == 'intra_sentence':
                    # この id が同じ文内にある
                    target_id = int(target_elem_dict['id'])
                    
                    if target_id in elem2dep_dict:
                        
                        # targetの文節。俺たち。
                        target_bunsetsu_id = elem2dep_dict[target_id]

                        if target_bunsetsu_id in dep_dict:
                            link_dep_dict = dep_dict[target_bunsetsu_id]
                            # print(["no", target, link_dep_dict, target_id, target_bunsetsu_id, pred_bunsetsu_link_num])
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
                                # for printing debugging
                
                if rel_type == 'none' and rel_dist == 'outer':
                    # ターゲットが文IDがないなら文章外でゼロ代名詞
                    rel_type = 'zero'
                elif rel_type == 'none' and rel_dist == 'inter_sentence':
                    # ターゲットが文IDがありPredの文IDと異なるなら文間照応でゼロ代名詞
                    rel_type = 'zero'
                
                if rel_type == 'none':
                    pp.pprint(["Endless none", sid, rel_type, surface_case, target, predstr, target_elem_dict, elem2dep_dict])

                gr_dict = {
                    'surface_case': surface_case, 
                    'gr': grammatical_role, 
                    'rel_dist': rel_dist,
                    'rel_type': rel_type,  
                    'pred': predstr, 
                    'pred_bunsetsu' : bunsetsu_str,
                    'target': target,
                    'target_sid': target_sid
                    }
                rlist.append(gr_dict)
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

        bun_index = -1
        elem_index = -1

        list1 = line.split()
        sid = list1[1]
        line2 = f.readline()
        while line2:
            line2 = line2.strip()
            dep_match = re.findall('\*\s([-0123456789]+)([A-Z])', line2)
            tag_line_match = re.findall('\+\s([-0123456789]+)([A-Z])\s*(.*)$', line2)
            if dep_match:
                link_num = dep_match[0][0]
                dep_type = dep_match[0][1]
                bun_index += 1
                dep_dict[bun_index] = self._ret_bun_dict(link_num=link_num, dep_type=dep_type)
                
            elif tag_line_match:
                id_num = tag_line_match[0][0]
                id_dep_type = tag_line_match[0][1]
                id_tag = tag_line_match[0][2]
                elem_index += 1
                elem_dict[elem_index] = self._ret_dep_elem_dict(link_num=id_num, dep_type=id_dep_type, tags=id_tag, sen_id=sid)
                elem2dep_dict[elem_index] = bun_index

            elif line2 == 'EOS':
                break
            else:
                dep_dict[bun_index]['words'].append(line2)
                elem_dict[elem_index]['words'].append(line2)
                pass
            line2 = f.readline()
        
        # pp.pprint([elem_dict, dep_dict, elem2dep_dict])
        return dep_dict, elem_dict, elem2dep_dict

    def parse_knp_file(self, filename):
        """
        KNPファイルをパースしてタグ要素、文節の情報を格納した辞書を返す。
        """
        knp_elem_dict = {}
        knp_pred_dict = {}
        filekey = os.path.basename(filename).split('.')[0]
        with open(filename, "r", encoding='utf-8') as f:
            
            line = f.readline()
            sid = 'dummy'
            while line:
                # ここに処理内容を記述します
                line = line.strip()
                match = re.findall('#\sS\-ID:', line)

                if match:
                    sentence_head_list = line.split()
                    sid = sentence_head_list[1]
                    dep_dict, elem_dict, elem2dep_dict = self.parse_knp_sentence_lines(f, line)
                    pred_case_dict = self.ret_pred_case_dict(sid, elem_dict, dep_dict, elem2dep_dict)
                    knp_elem_dict[sid] = elem_dict
                    knp_pred_dict[sid] = pred_case_dict
                # 次の行を読み込みます
                line = f.readline()
        # pp.pprint([knp_elem_dict, knp_pred_dict])
        # exit()
        return filekey, knp_elem_dict, knp_pred_dict

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

if __name__=="__main__":
    
    args = opu.get_parse_option()
 
    if args.process == 'parse':
        convert_knp_json()
    elif args.process == 'test_date':
        make_test_json_date()