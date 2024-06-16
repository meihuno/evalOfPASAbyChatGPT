import logging
import json
import datetime
import os
import pprint as pp

"""雑用/未整備
"""

def setup_logger(logger_name, log_file, level=logging.INFO):
    # ロガーを作成
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # フォーマッターを作成
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # ハンドラを作成
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # ロガーにハンドラを追加
    logger.addHandler(file_handler)

    return logger

# 使用例
my_logger = setup_logger('my_logger', 'example.log')
my_logger.info('This is an info message')
my_logger.error('This is an error message')

def print_wait_log(rcount, success):
    if rcount % 100 == 0:
        # 現在の日時を取得
        current_datetime = datetime.datetime.now()
        # フォーマット指定して日時を表示
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # logger.info(f'    {count}, {success}, {float(success)/float(count)}')
        print([formatted_datetime, rcount, float(success)/float(rcount)])

def save_result_json(result_dict, logging_count, base_dir, exp_name):

    # 現在の日付を取得します。
    now = datetime.datetime.now()

    # ファイル名を作成します。
    filename = "result{date}.{c}.json".format(date=now.strftime("%Y%m%d_%H%M%S"), c=logging_count)

    # JSON形式に変換する際に、インデントと文字コードを指定します
    json_data = json.dumps(result_dict, indent=4, ensure_ascii=False)

    # チェックしたいディレクトリのパスを指定
    directory_path_to_check = base_dir + f'/{exp_name}'

    # ディレクトリが存在しない場合は作成する
    create_directory_if_not_exists(directory_path_to_check)

    output_file_path = f'{directory_path_to_check}/{filename}'
    # JSONデータをファイルに保存します
    with open(output_file_path, 'w', encoding='utf-8') as f:
        print(f"saving {output_file_path}")
        f.write(json_data)
        # pass

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"ディレクトリ {directory_path} を作成しました。")
    else:
        print(f"ディレクトリ {directory_path} は既に存在します。")

def _ret_elapsed_time(results):

    import datetime
    
    query_counter = 0
    total_tokens = 0
    times = []
    status_dict = {}
    
    for result_and_status in results:
        result_dict = result_and_status[0]
        total_status = result_and_status[1]

        for id1, exp_dict in result_dict.items():
            for exp_name, response_list in exp_dict.items():
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
                    tokens = one_response['usage']['total_tokens']
                    times.append(time)
                    total_tokens += tokens
    
    print(["status_dict", len(status_dict), status_dict])
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

    return total_tokens, total_seconds, query_counter

def ret_diff_time(start_time, end_time):
    time_difference = end_time - start_time
    # 日数を秒数に変換
    total_seconds = time_difference.total_seconds()

    # 時、分、秒に変換
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    # 経過時間を表示
    print("Total 経過時間: {} 時間 {} 分 {} 秒".format(int(hours), int(minutes), int(seconds)))

