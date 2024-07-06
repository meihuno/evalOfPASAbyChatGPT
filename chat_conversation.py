import os
import pprint as pp
from openai import OpenAI
from openai import AsyncOpenAI
import sys
import glob
from tenacity import retry, stop_after_attempt, wait_random_exponential
import nest_asyncio
nest_asyncio.apply()
import asyncio
from datetime import datetime
import time
# from google.colab import userdata

# スクリプトがあるディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# libディレクトリの絶対パスを構築して追加
lib_path = os.path.join(script_dir, 'lib')
sys.path.append(lib_path)

import target_file_util as tfu
import experimental_util as experimental_util
import option_util as opu

class ChatConversation(object):
    """ChatGPTにプロンプトで対話する
    """
    def __init__(self, model_name='gpt-3.5-turbo', base_dir='./result/dev5_gpt4_o', async_flag=True, prompt_type='gogo', sample_limit=1000, process_env='local', skip_process_flag=False):
        # APIのシークレットコードが保存されている環境変数のキー
        
        self.model_name = model_name
        # self.sample_size = 5
        self.sample_size = 1
        self.base_dir = base_dir
        self.async_flag = async_flag
        self.prompt_type = prompt_type
        self.sample_limit = sample_limit
        self.process_environment =  process_env
        self.skip_process_flag = skip_process_flag

    def _ret_openai_clinet(self):
        SECRET_KEY_ENV_VARIABLE = 'OPEN_AI_KEY'
        api_secret_key = None

        # 環境変数からAPIのシークレットコードを取得
        if self.process_environment == 'local':
            api_secret_key = os.environ.get(SECRET_KEY_ENV_VARIABLE)
        elif self.process_environment == 'colab':
            api_secret_key = userdata.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")

        # os.environ.get(SECRET_KEY_ENV_VARIABLE)
        client = None
        if api_secret_key is None:
            print(f"エラー: {SECRET_KEY_ENV_VARIABLE} 環境変数が設定されていません。")
            exit()
        else:
            # APIのシークレットコードを使用して何かしらの処理を行う
            if self.async_flag == True:
                client = AsyncOpenAI(api_key=api_secret_key)
            elif self.async_flag == False:
                client = OpenAI(api_key=api_secret_key)
        return client


    # 実験時にextra扱いのpromptを特別扱いした。
    def _ret_batch_dict(self, target_id_list, prompt_files):
        if self.prompt_type == 'extra':
            return self._ret_gogo_batch_dict(target_id_list, prompt_files)
        else:
            return self._ret_gogo_batch_dict(target_id_list, prompt_files)

    def _ret_gogo_batch_dict(self, target_id_list, prompt_files):
        rdict = {}
        gogo_prompt_list = []
        counter = 0
        key = 0
        for id1 in target_id_list:
            prompt_dict = prompt_files[id1]
            for exp_name, prompt_dict1 in prompt_dict.items():
                # if exp_name == 'paraphrase-cont2' :
                # if exp_name == 'order-sequence' or exp_name == 'reading' or exp_name =='paraphrase' or exp_name == 'translation' or exp_name == 'compare-translation-cont':
                # if exp_name == 'few-shot-semantic-search' or exp_name == 'zero-shot-standard': 
                # if exp_name == 'order-sequence' or exp_name == 'zero-shot-simple' or exp_name =='zero-shot-modify-knp' or exp_name == 'few-shot-simple' or exp_name == 'summary':
                gogo_prompt_list.append([id1, exp_name, prompt_dict1])
            
            counter += 1
            if self.sample_size == counter:
                rdict[key] = gogo_prompt_list
                gogo_prompt_list = []
                counter = 0
                key += 1

        if len(gogo_prompt_list) > 0:
            rdict[key] = gogo_prompt_list
        return rdict

    def _ret_extra_batch_dict(self, target_id_list, prompt_files):
        rdict = {}
        counter = 0
        key = 0
        gogo_prompt_list = []
        # print(target_id_list)
        # print(prompt_files)
        for id1 in target_id_list:
            prompt_dict = prompt_files[id1]
            for exp_name, prompt_dict1 in prompt_dict.items():
                gogo_prompt_list.append([id1, exp_name, prompt_dict1])
                counter += 1
                if counter == 15:
                    rdict[key] = gogo_prompt_list
                    gogo_prompt_list = []
                    counter = 0
                    key += 1
        if len(gogo_prompt_list) > 0:
            rdict[key] = gogo_prompt_list
        # print(rdict)
        # exit()
        return rdict

    def gogo_prompt(self, target_id_list, prompt_files):
        # id1 と exp_name に フラットな list を返す。パラメータは サンプル数と 実験数

        gogo_prompt_dict = self._ret_batch_dict(target_id_list, prompt_files)
        print(f"target_id_list {len(target_id_list)}, prompt_files: {len(prompt_files)}")
        # target_id_list = ['w201106-0002000000']
        async def main1(gogo_prompt_list):

            print(["batch size 1: ", len(gogo_prompt_list)])
            gogo_list = []
            for pidx, prompt_list in enumerate(gogo_prompt_list):
                id1 = prompt_list[0]
                exp_name = prompt_list[1]
                prompt_dict1 = prompt_list[2]
                gogo_list.append(asyncio.create_task(self.ret_one_response(id1, exp_name, prompt_dict1, 1)) )

            print(["batch size 2:", len(gogo_list)])
            results = await asyncio.gather(
                *gogo_list,
                return_exceptions=False,
                )

            total_tokens, total_seconds, query_counter = experimental_util._ret_elapsed_time(results)
            minutes = total_seconds / 60.0
            tpm = 0.0
            rpm = 0.0
            if minutes > 0.0:
                tpm = total_tokens /  minutes
                rpm = query_counter / minutes
            print(f"tpm {tpm}, rpm {rpm}")
            if tpm > ( 90000 - 5000 )  or ( rpm > 3500 - 100 ):
                print("Waiting")
                time.sleep(100)
            self.save_jsons(results)
        
        count = 0
        print(f"Now I showed the length of gogo_prompt_dict is {len(gogo_prompt_dict)}.")
        for key, gogo_prompt_list in gogo_prompt_dict.items():
            print(f"gogo number {key}...")
            if self.skip_process_flag == True:
                print([f"skipping {len(gogo_prompt_list)} promps of {key}"])
                pass
            else:
                asyncio.run(main1(gogo_prompt_list))
            count += 1
            if count > self.sample_limit:
                break

    def save_jsons(self, results):
    # for id1 in train_test_id_dict[phase]:
        # id, exp_name, result : []
        rdict = {}
        
        for result_and_status in results:
            result_dict = result_and_status[0]
            total_status = result_and_status[1]

            for id1, exp_dict in result_dict.items():
                if not id1 in rdict:
                    rdict[id1] = {}
                    rdict[id1]['status'] = total_status
                    rdict[id1]['result'] = {}
                
                for exp_name, rlist in exp_dict.items():
                    rdict[id1]['result'][exp_name] = rlist 

        tfu.save_result_json_simple(rdict, self.base_dir, id1)


    # async def ret_one_response(self, id1, exp_name, prompt_dict1, delay):
    async def ret_one_response(self, id1, exp_name, prompt_dict1, delay):
        
        def ret_history_message(response_dict):
            content = response_dict['response']['choices'][0]['message']['content']
            return {'role': 'assistant', 'content': content}

        rdict = {}
        rdict[id1] = {}
        rdict[id1][exp_name] = []

        messages = prompt_dict1['messages']
        assistant_type = prompt_dict1['assistant_type']
        response_history = []
        success_count = 0

        for midx, message in enumerate(messages):
            # messageに１つのrequestセットが入っている。
            # もし response_history が 空 で ないなら message に historyを詰め込む
            if assistant_type == 'incremental_assistant':
                if len(response_history) > 0:
                    message = response_history + message
            elif assistant_type == 'flow_merge':
                # flow_mergeは最後の場合だけhistoryを使う
                if len(response_history) > 0 and midx == len(messages) - 1:
                    message = response_history + message

            start = datetime.now()
            print(f"prepare {id1} {exp_name} {midx} at {start.strftime('%X')}")
            # print(["current_message", message])
            client = self._ret_openai_clinet()
            model_name = self.model_name
            # await asyncio.sleep(delay)
            response = await self.ret_response_dict(client, model_name, message)
            
            if response['status'] == 'ok':
                if assistant_type == 'incremental_assistant' or assistant_type == 'flow_merge':
                    if exp_name == 'order-sequence' and midx > 0:
                        pass
                    else:
                        # inputをhistoryに含める
                        response_history = response_history + message
                    # responseをhistoryにつめる
                    response_history.append( ret_history_message(response) )    
                success_count += 1
                
            rdict[id1][exp_name].append(response)
            end = datetime.now()
            print(f"over {id1} {exp_name} {midx} at {end.strftime('%X')}")
        
        status = 'ng'
        if success_count == len(messages):
            status = 'ok'
        return rdict, status

    async def ret_response_dict(self, client, model_name, messages):

        @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
        async def ret_chatgpt_response_dict(client, model_name, messages, temperature=0):
            # 推論
            if self.async_flag == True:
                chat_completion = await client.chat.completions.create(
                    messages= messages,
                    temperature=temperature,
                    model=model_name,
                    # response_format={"type": "json_object"},
                )
            elif self.async_flag == False:
                chat_completion = client.chat.completions.create(
                    messages= messages,
                    temperature=temperature,
                    model=model_name,
                    # response_format={"type": "json_object"},
                )
            
            return chat_completion

        def obj2dict(response):
            rdict = vars(response)
            clist = []
            for choice in rdict['choices']:
                c1 = vars(choice)
                c1['message'] = vars(choice.message) #tmp_dict
                clist.append(c1)
            rdict['choices'] = clist
            usage = rdict['usage']
            rdict['usage'] = vars(usage)
            # pp.pprint(rdict)
            return rdict
        
        response_dict = {}
        if 1 == 1:
        # try:
            response = await ret_chatgpt_response_dict(client, model_name, messages, temperature=0)
            response_dict['status'] = 'ok'
            response_dict['response'] = obj2dict(response)
            response_dict['input'] = messages
        else:
        # except Exception as e:
            print(str(e))
            response_dict['status'] = 'ng'
            response_dict['input'] = messages
            response_dict['error_message'] = str(e)

        return response_dict

def main():
    # train dev の区別を呼び出すっぴ
    _, train_test_id_dict, org_dict = tfu.ret_experimental_files()

    args = opu.get_chat_option()
    async_flag = True
    if args.asyn == 'no':
        async_flag = False

    print(["skip", args.skip])
    skip_flag = False
    if args.skip == 'yes':
        skip_flag = True

    # opton loading
    base_dir = args.otd
    model_name = args.model
    ok_dir = args.okd
    prompt_type = args.pt
    sample_limit = args.limit
    process_env = args.penv

    ok_target_id_list = []
    print(f'ok_dir {ok_dir}')
    dirpat =  f'{ok_dir}/*.json'
    jfiles = glob.glob(dirpat)
    ok_set = set()
    for jfile in jfiles:
        # ファイル名のみを取得
        check_dict = tfu.ret_result_json_status_dict(jfile)
        for exist_id, status in check_dict.items():
            if status == 'ok':
                ok_set.add(exist_id)
    
    ok_target_id_list = list(ok_set)
    print(["ok id ", len(ok_target_id_list)])

    # すでに取得済みのデータのidを得る
    exist_5_id_list = ['w201106-0002000003', 'w201106-0002000000', 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']
    ok_target_id_list = list(set(ok_target_id_list + exist_5_id_list))

    phase = 'dev'
    target_id_list = train_test_id_dict[phase]
    a = set(target_id_list) - set(ok_target_id_list)
    # current_target_id_list = ['w201106-0002000003', 'w201106-0002000000'] # , 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']
    if args.sampling == 'sample5':
        current_target_id_list = ['w201106-0002000003', 'w201106-0002000000', 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']
    else:
        # current_target_id_list = [list(a)[0]]
        current_target_id_list = list(set(a))
    print(f"target_id: {len(target_id_list)}, ok id :{len(ok_target_id_list)}, current_target_id :{len(current_target_id_list)}")

    if prompt_type == 'gogo':
        prompt_file = './workplace/prompt/over_prompt.json'
    elif prompt_type == 'extra':
        prompt_file = './workplace/prompt/extra_prompt.json'
    else:
        print("Prompt type, Not set")
        exit()
    prompt_files = tfu.ret_dict_from_json(prompt_file)
    # exit()
    box = ChatConversation(model_name, base_dir=base_dir, async_flag=async_flag, prompt_type=prompt_type, sample_limit=sample_limit, process_env=process_env, skip_process_flag=skip_flag)
    box.gogo_prompt(current_target_id_list, prompt_files)


if __name__=="__main__":
    main()
