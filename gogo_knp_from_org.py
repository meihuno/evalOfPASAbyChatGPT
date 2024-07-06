import os
import json
import subprocess


def gogo_knp_subprocess(id1, filename):
    
    base_dir = './workplace/knp'
    dir1 = base_dir + '/' + id1[0:13]
    mksavedir(dir1)

    output_file = dir1 + '/' + id1 + '.knp'

    # コマンドを定義
    commands = [
        ["cat", f"{filename}"],
        ["juman", "-i", "#"],
        ["knp", "-anaphora", "-simple"]
    ]

    try:
        # 最初のコマンドを実行してプロセスを開始
        print(f"Starting { commands[0] } ...")
        process = subprocess.Popen(commands[0], stdout=subprocess.PIPE)
        print(f'{commands[0]}')
        # 残りのコマンドを順番に実行してパイプで繋ぐ
        for cmd in commands[1:]:
            process = subprocess.Popen(cmd, stdin=process.stdout, stdout=subprocess.PIPE)

        # 最終的な結果をファイルに保存
        with open(output_file, "wb") as f:
            f.write(process.communicate()[0])

        print("Done! The result was save at ", output_file)

    except subprocess.CalledProcessError as e:
        print("エラーが発生しました:", e)

def gogo_knp_gogo_knp(input_dict):
    for id1, filepath in input_dict.items():
        gogo_knp_subprocess(id1, filepath)

def ret_org_lines(org_sub_dict):
    rlist = []
    for sid, sentence in org_sub_dict.items():
        rlist.append(f"# {sid}\n{sentence}")
    return '\n'.join(rlist)

def ret_knp_input_line_filess(phase_list=['dev']):

    json_open = open('./data/train_test_id.json', 'r')
    train_test_id_dict = json.load(json_open)  
    
    for phase, idlist in train_test_id_dict.items():
        print([phase, len(idlist)])

    # json_open = open('./sample_data/sample2.json', 'r')
    json_open = open('./data/org.json', 'r')
    org_dict = json.load(json_open) 

    base_dir = './workplace/org'
    count = 0
    file_dict = {}
    for phase in phase_list:
        for id1 in train_test_id_dict[phase]:
            lines = ret_org_lines(org_dict[id1])
            # Windowsでも動くようにpathlibとか使うべきなのだがサボる
            dir1 = base_dir + '/' + id1[0:13]
            mksavedir(dir1)

            output_file = dir1 + '/' + id1 + '.txt'
            count += 1

            # 最終的な結果をファイルに保存
            with open(output_file, "w") as f:
                f.write(lines)

            file_dict[id1] = output_file
            
            if count > 0:
                pass
                # break


    return file_dict

def mksavedir(directory_path):
    # directory_path = "./test/one"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def gogo_knp_from_org(phase_list):
    input_file_dict = ret_knp_input_line_filess(phase_list=phase_list)
    gogo_knp_gogo_knp(input_file_dict)



if __name__=="__main__":
    # input_dict = {'sample2': "./sample/sample2.org"}
    # gogo_knp_gogo_knp(input_dict)
    gogo_knp_from_org(['train', 'test'])  
