import json
import logging
import datetime
import os

# ここで複数のモデルを識別する仕組みが必要
def ret_result_dict_series(dirname='ok_result_dev'):
        # json_open = open('./sample_data/sample2.json', 'r')
        ok_pred_content_dict = {}
        result_compose_dict = {}
        
        ok_results_list = glob.glob(f'./{dirname}/*.json')
        
        for file1 in ok_results_list:
            json_open = open(file1, 'r')
            pred_dict = json.load(json_open) 
            ok_pred_content_dict, result_compose_dict = ret_pred_dict_file(file1)
            

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

def save_result_json_simple(result_dict, base_dir, id1):

    # 現在の日付を取得します。
    now = datetime.datetime.now()

    # ファイル名を作成します。
    filename = "result{date}.{id1}.json".format(date=now.strftime("%Y%m%d_%H%M%S"), id1=id1)

    # JSON形式に変換する際に、インデントと文字コードを指定します
    json_data = json.dumps(result_dict, indent=4, ensure_ascii=False)

    # チェックしたいディレクトリのパスを指定
    directory_path_to_check = base_dir

    # ディレクトリが存在しない場合は作成する
    create_directory_if_not_exists(directory_path_to_check)

    output_file_path = f'{directory_path_to_check}/{filename}'
    # JSONデータをファイルに保存します
    with open(output_file_path, 'w', encoding='utf-8') as f:
        print(f"saving {output_file_path}")
        f.write(json_data)


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"ディレクトリ {directory_path} を作成しました。")
    else:
        print(f"ディレクトリ {directory_path} は既に存在します。")

def save_result_json(result_dict, logging_count, base_dir, exp_name, id1):

    # 現在の日付を取得します。
    now = datetime.datetime.now()

    # ファイル名を作成します。
    filename = "result{date}.{id1}.json".format(date=now.strftime("%Y%m%d_%H%M%S"), id1=id1)

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

def ret_experimental_files(correct_json='./intermediate_data/knp_pred1.json', 
                            target_id_json='./data/train_test_id.json', 
                                org_json = './data/org.json' ):
    """実験で利用するファイルセットを辞書にして返す関数です。
    """
    # knpの中間データが入る。おぷしょんで指定できるようにしたほうがいいよね
    json_open = open(correct_json, 'r')
    knp_pred_dict = json.load(json_open) 

    json_open = open(target_id_json, 'r')
    train_test_id_dict = json.load(json_open)  
    
    # json_open = open('./sample_data/sample2.json', 'r')
    json_open = open(org_json, 'r')
    org_dict = json.load(json_open) 

    return knp_pred_dict, train_test_id_dict, org_dict

def ret_dict_from_json(target_file):
    # './intermediate_data/knp_pred_ana1.json'
    # knpの中間データが入る
    json_open = open(target_file, 'r')
    target_dict = json.load(json_open) 

    return target_dict

def ret_result_json_status_dict(file1):

    check_rdict = {}

    json_open = open(file1, 'r')
    pred_dict = json.load(json_open) 

    for id1, res_dict in pred_dict.items():
        result = res_dict['result']
        status = res_dict['status']

        check_rdict[id1] = status
    
    return check_rdict
