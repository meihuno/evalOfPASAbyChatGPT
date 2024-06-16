def is_anaphora_ok(elem):
    if elem['origin'] == 'anaphora':
        if elem['gr'] == '主語' or elem['gr'] == '目的語' or elem['gr'] == 'ニ格':
            return True
        else:
            return False
    else:
        return False

def is_dep_ok(elem):
    if elem['origin'] == 'dep':
        if elem['surface_case'] == 'が' or elem['surface_case'] == 'を' or elem['surface_case'] == 'に':
            return True
        else:
            return False
    else:
        return False

def is_exp_target(elem, target_flag):
    if target_flag == 'anaphora':
        return is_anaphora_ok(elem)
    elif target_flag == 'dep':
        return is_dep_ok(elem)
    else:
        return True

def ret_gr_from_dep_surface(gr1, surface_case):
    if surface_case == 'が':
        gr1 = '主語'
    elif surface_case == 'を':
        gr1 = '目的語'
    elif surface_case == 'に':
        gr1 = 'ニ格'
    return gr1

# なんか粘土を捏ね繰り返してる気分・・・。
def ret_knp_pred_kv_dict(knp_result_dict, gr2dict, target_type='anaphora'):
    pred_dict = {}
    # KNPの中間出力を評価しやすいように構造化する
    # 最初からこの構造にしておけばよかったんや
    if target_type == 'anaphora_dep':
        target_type1 = 'anaphora'
    else: 
        target_type1 = target_type

    for senid1, knp_result_list in knp_result_dict.items():

        # 先にanaphoraの述語と格要素を抑えてから、その述語がない、述語があった場合に格解析結果がない場合に

        if not senid1 in pred_dict:
            pred_dict[senid1] = {}

        for elem in knp_result_list:
            pred_bunsetsu = elem['pred_bunsetsu']
            pred = elem['pred_bunsetsu']
            pred_id = elem['pred_id']
            
            surface_case = elem['surface_case'] 
            gr1 = elem['gr']
            
            if is_exp_target(elem, target_type1) == True:
                pass
            else:
                continue

            if target_type1 == 'dep':
                gr1 = ret_gr_from_dep_surface(gr1, surface_case)

            if not pred_bunsetsu in pred_dict[senid1]:
                pred_dict[senid1][pred_bunsetsu] = {}
            if not pred_id in pred_dict[senid1][pred_bunsetsu]:
                pred_dict[senid1][pred_bunsetsu][pred_id] = {'pred': pred, 'case': {} }
            
            if gr1 in gr2dict:
                gr = gr2dict[gr1]
                if not gr in pred_dict[senid1][pred_bunsetsu][pred_id]['case']:
                    pred_dict[senid1][pred_bunsetsu][pred_id]['case'][gr] = []
                tmp_dict = ret_case_elem_dict(elem)
                pred_dict[senid1][pred_bunsetsu][pred_id]['case'][gr].append(tmp_dict)

        # anaphora_dep の 場合、dep分を、もう一回やるぜよ
        if target_type == 'anaphora_dep':
            
            for elem in knp_result_list:
                pred_bunsetsu = elem['pred_bunsetsu']
                pred = elem['pred_bunsetsu']
                pred_id = elem['pred_id']

                surface_case = elem['surface_case'] 
                gr1 = elem['gr']

                if is_exp_target(elem, 'dep') == True:
                    pass
                else:
                    continue

                # dep相当の処理をする
                gr1 = ret_gr_from_dep_surface(gr1, surface_case)

                if not pred_bunsetsu in pred_dict[senid1]:
                    pred_dict[senid1][pred_bunsetsu] = {}
                if not pred_id in pred_dict[senid1][pred_bunsetsu]:
                    pred_dict[senid1][pred_bunsetsu][pred_id] = {'pred': pred, 'case': {} }
                
                # print(gr1)
                if gr1 in gr2dict:
                    gr = gr2dict[gr1]
                    if not gr in pred_dict[senid1][pred_bunsetsu][pred_id]['case']:
                        pred_dict[senid1][pred_bunsetsu][pred_id]['case'][gr] = []
                    # print(gr1)

                    tmp_dict = ret_case_elem_dict(elem)
                    tstr = tmp_dict['surface']
                    ttid = tmp_dict['target_id']
                    # grに既存の格要素がない場合に追加する。つまり、
                    # print(["tmp", gr1, tmp_dict])
                    same_flag = False
                    for other_one in pred_dict[senid1][pred_bunsetsu][pred_id]['case'][gr]:
                        osurf = other_one['surface']
                        otid = other_one['target_id']
                        if tstr == osurf or ttid == otid:
                            same_flag = True
                            break
                    
                    if same_flag == False:
                        pred_dict[senid1][pred_bunsetsu][pred_id]['case'][gr].append(tmp_dict)
    
    return pred_dict

def ret_case_elem_dict(elem):
    target_id = elem['target_id']
    rel_dist = elem['rel_dist']
    rel_type = elem['rel_type']
    tstr1 = elem['target']

    tmp_dict = {'surface': tstr1, 'rel_dist': rel_dist, 'rel_type': rel_type, 'target_id': target_id}
    
    return tmp_dict
