def ret_evaluation_result_dict(count_dict):
        rdict = {}
        if 'all' in count_dict:
            for key, num_dict in count_dict.items():
                rdict[key] = _ret_eval_result_dict(num_dict)
        else:
            for key, num_dict in count_dict.items():
                rdict[key] = {}
                rdict[key] = ret_evaluation_result_dict(num_dict)

        return rdict

def _ret_eval_result_dict(count_dict):
        cnum = count_dict['cnum']
        sout = count_dict['sout']
        csout = count_dict['csout']
        rdict = _ret_f1_score_dict(csout, sout, cnum)
        return rdict

def _ret_f1_score_dict(correct_system_outputs, system_outputs, correct_num):
    """
    F値を計算する
    """
    if system_outputs == 0:
        if correct_system_outputs == 0:
            precision = 0.0
        elif correct_system_outputs > 0:
            precision = 0.0
    else:
        if correct_system_outputs >= system_outputs:
            precision = 1.0
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