def ret_rel_type_from_dict(dict1):
    rel_dist1 = dict1['rel_dist']
    rel_type1 = dict1['rel_type']
    rel_type3 = rel_type1
    if rel_type1 == 'zero':
        rel_type3 = f'{rel_type1}_{rel_dist1}' 
    return rel_type3

def ret_init_count_dict(case_list):
    count_dict = {}
    for gr in case_list:
        count_dict[gr] = ret_init_eval_count_dict()
    return count_dict

def ret_init_eval_count_dict():
    num_dict = {'sout':0, 'csout':0, 'cnum': 0 }
    return num_dict

def ret_init_case_count_dict(case_list):
    eval_count_dict = {}
    for gr in case_list:
        eval_count_dict[gr] = 0            
    return eval_count_dict

def ret_init_rel_count_dict(case_list, rel_type_list, rel_dist_list):
    rel_count_dict = {}
        # 初期化
    for type1 in rel_type_list:
        for type2 in rel_dist_list:
            type3 = type1
            if type1 == 'zero':
                type3 = f'{type1}_{type2}'
            # type1 = self._ret_type_str(case_elem)
            if not type3 in rel_count_dict:
                rel_count_dict[type3] = {}
            for gr in case_list:
                # pred は対象外
                if not gr == 'pred':
                    rel_count_dict[type3][gr] = ret_init_eval_count_dict()
            if not type1 == 'zero':
                break
    return rel_count_dict