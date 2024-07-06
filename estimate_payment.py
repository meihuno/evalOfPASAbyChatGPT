import os
import pprint as pp
import sys
import glob
import json
import datetime

def traverse():

    # dirname = './result/dev4_extra/'
    dirname = './result/dev5_gpt4_o.back'

    query_counter = 0
    total_tokens = 0
    completion_tokens = 0
    prompt_tokens = 0

    token_count_dict = {}

    times = []
    status_dict = {}
    ok_results_list = glob.glob(f'./{dirname}/*.json')

    for file1 in ok_results_list:

        json_open = open(file1, 'r')
        pred_dict = json.load(json_open) 

        for id1, res_dict in pred_dict.items():
            
            result = res_dict['result']
            for exp_name, response_list in result.items(): 
                if not exp_name in token_count_dict:
                    token_count_dict[exp_name] = {'completion':0, 'prompt':0, 'total':0}

                for res in response_list:
                    status = res['status']
                    if not id1 in status_dict:
                        status_dict[id1] = {}
                    if not status in status_dict[id1]:
                        status_dict[id1][status] = 0
                    status_dict[id1][status] += 1

                    query_counter += 1
                    one_response = res['response']
                    time = one_response['created']
                    prompt_tokens = one_response['usage']['prompt_tokens']
                    completion_tokens = one_response['usage']['completion_tokens']
                    tokens = one_response['usage']['total_tokens']
                    token_count_dict[exp_name]['completion'] += completion_tokens
                    token_count_dict[exp_name]['prompt'] += prompt_tokens
                    token_count_dict[exp_name]['total'] += tokens
                    times.append(time)
                    total_tokens += tokens
    
    print([len(status_dict), status_dict])
    print(["query_counter", query_counter])
    print(["total_tokens", total_tokens])

    sorted_times = sorted(times)
    start_time = sorted_times[0] 
    end_time = sorted_times[-1]  # ソートされた新しいリストを返す # ソートされた新しいリストを返す

    # タイムスタンプを日時オブジェクトに変換
    start_object = datetime.datetime.fromtimestamp(start_time)
    end_object = datetime.datetime.fromtimestamp(end_time)

    # 日時オブジェクトを任意のフォーマットの文字列に変換
    date_string1 = start_object.strftime('%Y-%m-%d %H:%M:%S')
    date_string2 = end_object.strftime('%Y-%m-%d %H:%M:%S')
    print(["from", date_string1, "to", date_string2])
    # 差分を計算
    time_diff = end_object - start_object

    # 差分を時間、分、秒に変換
    total_seconds = time_diff.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    # 時間を示す文字列に変換
    time_string = f"{hours}時間{minutes}分{seconds}秒"

    print(f"経過は、{time_string}")

    pp.pprint(token_count_dict)
    total_total = 0.0
    idx1 = 1
    for exp_name, sub in token_count_dict.items():
        # print(exp_name)
        comp = sub['completion']
        prompt = sub['prompt']
        # print(["input ", 5.0 * (prompt/1000000.0)])
        # print(["output ", 15.0 * (comp/1000000.0)])
        input = 5.0 * (prompt/1000000.0)
        input = round(input, 3)
        output = 15.0 * (comp/1000000.0)
        output = round(output, 3)
        total = input + output
        total = round(total, 3)
        comp = round(comp, 3)
        prompt = round(prompt, 3)
        total_total += total
        print(f'|{idx1}|{exp_name}|{input}({prompt} tokens)|{output}({comp} tokens)|{total}|')
        idx1 += 1

    print([total_total, 155 * total_total])


if __name__=="__main__":
    traverse()