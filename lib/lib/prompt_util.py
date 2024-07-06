"""テーブルを扱うUtility
"""

def ret_table_case_dict_value_list():
    rdict = {'主語':[], '目的語': [], 'ニ格':[] }
    return rdict

def ret_table_case_dict_value_dict():
    rdict = {'主語':{}, '目的語': {}, 'ニ格':{} }
    return rdict


def ret_sentence_line(org_sub_dict):
    rlist = []
    for senid, sentext in org_sub_dict.items():
        rlist.append(f'# {senid}')
        rlist.append(sentext)

    return '\n'.join(rlist)

def ret_sentence_line_simple(org_sub_dict):
    rlist = []
    sencount = 1
    for senid, sentext in org_sub_dict.items():
        rlist.append(f'文{sencount}「{sentext}」')
        sencount += 1

    return '\n'.join(rlist)

def ret_role_dict(role_type, content):
    role_dict = {'role': role_type, 'content': content}
    return role_dict

def ret_table_row_lines(row_dict):
    row_lines = []
    rows = ['', '文番号', '述語', '主語(subj)', '目的語(obj)','斜格語(obl)', '']
    row_lines.append('|'.join(rows))
    sennum = 1
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
            rows = ['', f'文{sennum}', pred,  subj, obj, obl, '']
            row_lines.append('|'.join(rows))
        sennum += 1

    return '\n'.join(row_lines)

def ret_table_row_dict(knp_sub_pred_dict):
    row_dict = {}
    row_rel_dict = {}
    for senid, elem_list in knp_sub_pred_dict.items():
        if not senid in row_dict:
            row_dict[senid] = {}
            row_rel_dict[senid] = {}
        
        for tmp_dict in elem_list:
            pred = tmp_dict['pred']
            if not pred in row_dict[senid]:
                row_dict[senid][pred] = ret_table_case_dict_value_list()
                row_rel_dict[senid][pred] = ret_table_case_dict_value_dict()
            gr = tmp_dict['gr']
            rel_type = tmp_dict['rel_type']
            rel_dist = tmp_dict['rel_dist']
            target = tmp_dict['target']
            if gr in row_dict[senid][pred]:
                row_dict[senid][pred][gr].append(f'{target}')
                row_rel_dict[senid][pred][gr][target] = {'rel_type': rel_type, 'rel_dist': rel_dist}

    return row_dict, row_rel_dict

def ret_pred_row_table_dict(knp_pred_dict):
    row_dict = {}
    for senid, pred_dict in knp_pred_dict.items():
        if not senid in row_dict:
            row_dict[senid] = {}
        for pred, pred_content_dict in pred_dict.items():
            if not pred in row_dict[senid]:
                row_dict[senid][pred] = {}
            row_dict[senid][pred] = ret_table_case_dict_value_list()
    return row_dict

def ret_pred_list(knp_pred_dict):
    rlist = []
    for senid, pred_dict in knp_pred_dict.items():
        for pred, pred_content_dict in pred_dict.items():
            rlist.append(f'「{pred}」')
    return rlist

def ret_sentence_lines(row_dict):
    sen_lines = []
    sennum = 1
    for senid, pred_dict1 in row_dict.items():
        phrase_lines = []
        for pred, gr_dict in pred_dict1.items():
            pas_list1 = []
            for elem in gr_dict['ニ格']:
                cstr = elem + 'に'
                pas_list1.append(cstr)
            for elem in gr_dict['目的語']:
                cstr = elem + 'を'
                pas_list1.append(cstr)
            for elem in gr_dict['主語']:
                cstr = elem + 'が'
                pas_list1.append(cstr)
            phrase_lines.append(''.join(pas_list1) + pred)

        phrase_str = ' '.join(phrase_lines)
        sen_line = f'文{sennum}: {phrase_str}'
        sen_lines.append(sen_line)
        sennum += 1

        return '\n'.join(sen_lines)