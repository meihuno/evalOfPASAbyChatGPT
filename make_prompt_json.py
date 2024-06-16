import re
import glob
import os
import pprint as pp
import json
import unicodedata
import sys
import random

# スクリプトがあるディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# libディレクトリの絶対パスを構築して追加
lib_path = os.path.join(script_dir, 'lib')
sys.path.append(lib_path)

import option_util as opu
import eval_util_evaluation as eval_util_evaluation
import eval_util_string_match as eu_strmatch
import eval_util_count as eu_count
import prompt_message as prompt_message
import prompt_util as prompt_util
from json_read_write import JsonReadWrite
import target_file_util as tfu

class MakePromptJson(object):

    def __init__(self):
        self.cot_sample_dict = {}

        self.prompt_type_dict = {}
        self.prompt_type_dict['summary'] = MakePromptJson.summary_prompt
        self.prompt_type_dict['zero-shot-simple'] = MakePromptJson.zero_shot_simple_prompt
        self.prompt_type_dict['zero-shot-with-system-message'] = MakePromptJson.zero_shot_with_system_message_prompt
        self.prompt_type_dict['zero-shot-standard'] = MakePromptJson.zero_shot_standard_prompt
        self.prompt_type_dict['zero-shot-ss'] = MakePromptJson.zero_shot_ss_prompt
        self.prompt_type_dict['zero-shot-with-knp'] = MakePromptJson.zero_shot_with_knp_prompt
        self.prompt_type_dict['zero-shot-modify-knp'] = MakePromptJson.zero_shot_modify_knp_prompt
        self.prompt_type_dict['order-sequence'] = MakePromptJson.order_sequence_prompt
        self.prompt_type_dict['few-shot-simple'] = MakePromptJson.few_shot_simple_prompt
        self.prompt_type_dict['few-shot-with-cheering'] = MakePromptJson.few_shot_with_cheering_prompt
        self.prompt_type_dict['few-shot-semantic-search'] = MakePromptJson.few_shot_semantic_search_prompt
        self.prompt_type_dict['chain-of-thought'] = MakePromptJson.chain_of_thougth_prompt
        self.prompt_type_dict['chain-of-thought-mod-knp'] = MakePromptJson.chain_of_thougth_mod_knp_prompt
        self.prompt_type_dict['paraphrase'] = MakePromptJson.paraphrase_prompt
        self.prompt_type_dict['reading'] = MakePromptJson.reading_prompt

        self.prompt_type_dict['paraphrase-cont'] = MakePromptJson.paraphrase_cont_prompt
        self.prompt_type_dict['paraphrase-cont2'] = MakePromptJson.paraphrase_cont_prompt2
        
        self.prompt_type_dict['reading-cont'] = MakePromptJson.reading_cont_prompt
        self.prompt_type_dict['reading-cont2'] = MakePromptJson.reading_cont_prompt2
        
        self.prompt_type_dict['translation'] = MakePromptJson.translation_prompt
        self.prompt_type_dict['compare-translation'] = MakePromptJson.compare_translation_prompt

        self.prompt_type_dict['translation-cont'] = MakePromptJson.translation_cont_prompt
        self.prompt_type_dict['compare-translation-cont'] = MakePromptJson.compare_translation_cont_prompt
        self.prompt_type_dict['compare-translation-cont2'] = MakePromptJson.compare_translation_cont_prompt2
        
        """
        """

    def set_cot_sample_dict(self, cot_sample):
        self.cot_sample_dict = cot_sample

    def ret_prompt_dict(self, args):
        rdict = {}
        for prompt_key, prompt_method in self.prompt_type_dict.items():
            messages, assistant_type = prompt_method(args)
            rdict[prompt_key] = {'messages': messages, 'assistant_type': assistant_type}
        
        return rdict

    @classmethod
    def summary_prompt(cls, args):
        """要約をもとに述語項目構造解析を行う。テーブルへの変換は別途専用のスクリプトで行う
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # 後で示す文章に対して指定された述語に関する要約を行ってください。要約は、与えられた述語に対して、「〜が、~が、〜を、〜に、述語」のように述語に格助詞が後続する表現を述語に付与することで行います。以下に実施例を示します。
        # 例文
        # 　文1 「太郎は本屋に行きました。」　
        # 　文2 「本を買いました。
        # 　文3 「よく売れた本です。」
        # 要約対象述語：「行きました」、「書いました」、「売れた」。
        # 要約結果：太郎が、本屋に、行きました。太郎が、本を、買いました。本が、不特定:人、に売れた。
        # 要約結果は文として成り立つこと、テキスト中に述語に先行する表現が見つからない場合でも、要約として含めるべき物事が文中から読み取れる場合は、「不特定:人」「不特定:物」「筆者」といった表現を用いて要約に含めること。

        # では、要約の対象となる文を示します。
        # 例文
        # 要約対象述語: 
        # 要約結果：

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)
        knp_pred_list = args['knp_pred_list']

        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_summary_prompt(sen_str, knp_pred_list)) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'


    @classmethod
    def zero_shot_simple_prompt(cls, args):
        """zero-shot prompt
        | 最もシンプル。インタラクションなし
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_simple(sen_str)) )
        
        req_res.append(messages)
        return req_res, 'no_assistant'

    @classmethod
    def zero_shot_with_system_message_prompt(cls, args):
        """zero-shot prompt
        | 最もシンプル。システムメッセージ付き
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # システムメッセージ付き
        messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase()) )
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_simple(sen_str)) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def zero_shot_standard_prompt(cls, args):
        """zero-shot prompt
        | 手順を説明。インタラクションなし
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_standard(sen_str)) )
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def zero_shot_ss_prompt(cls, args):
        """zero-shot prompt
        | 最もシンプル。インタラクションなし
        """
        req_res = []
        
        org_dict = args['org_dict']
        core_rel_list = args['core_rel_list']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        if len(core_rel_list) > 0:
            messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_ss(sen_str, core_rel_list)) )
        else:
            messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_simple(sen_str)) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def zero_shot_with_knp_prompt(cls, args):
        """zero-shot-with-knp prompt
        | KNPの結果を埋めてもらうスタイル。述語の抽出は任せろ
        """
        req_res = []
        
        org_dict = args['org_dict']
        core_rel_list = args['core_rel_list']
        knp_empty_table = args['knp_empty_table']

        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase()) )
        
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_with_knp(sen_str, knp_empty_table)) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def zero_shot_modify_knp_prompt(cls, args):
        """zero-shot-with-knp prompt
        | KNPの結果を修正してもらいます。解析結果まで加えておきます。
        """
        
        req_res = []
        
        org_dict = args['org_dict']
        core_rel_list = args['core_rel_list']
        knp_table = args['knp_table']

        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase()) )
        
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_modify_knp(sen_str, knp_table)) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def order_sequence_prompt(cls, args):
        """zero-shot prompt
        | 手順を説明。インタラクションあり。assistantに突っ込んでみる。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase()) )
        messages.append( prompt_util.ret_role_dict('user', prompt_message.prompt_header(sen_str)) )
        req_res.append(messages)

        for order in prompt_message.zero_shot_order_list():
            messages = []
            messages.append( prompt_util.ret_role_dict('user', order ) )
            req_res.append(messages)
        
        return req_res, 'incremental_assistant'

    @classmethod
    def few_shot_simple_prompt(cls, args):
        """few-shot prompt
        | タスクの説明、例を示す。今度はこの文に対してお願いします。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        
        # train data から 持ってきた 述語項構造解析の例を示す
        cot_sample_dict = args['cot_sample_dict']
        # シンプルに、ランダムで、
        random_id = random.choice(list(cot_sample_dict.keys()))
        few_shot_str = cot_sample_dict[random_id]['few-shot']

        # 後は述語項構造解析を指示
        zero_shot_str = prompt_message.ret_zero_shot_simple(sen_str)
        prompt_str = few_shot_str + '\n' + zero_shot_str
        messages.append( prompt_util.ret_role_dict('user', prompt_str ) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def few_shot_semantic_search_prompt(cls, args):
        """few-shot prompt
        | タスクの説明、例を示す。今度はこの文に対してお願いします。類似文を例に用いる。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        # train data から 持ってきた 述語項構造解析の例を示す
        cot_sample_dict = args['cot_ss_dict']
        
        # 最も類似した文が選ばれている。すでに。
        few_shot_str = cot_sample_dict['few-shot']
        # 後は述語項構造解析を指示
        zero_shot_str = prompt_message.ret_zero_shot_simple(sen_str)
        prompt_str = few_shot_str + '\n' + zero_shot_str
        messages.append( prompt_util.ret_role_dict('user', prompt_str ) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def few_shot_with_cheering_prompt(cls, args):
        """few-shot prompt
        | タスクの説明、例を示す。今度はこの文に対してお願いします。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        cot_sample_dict = args['cot_sample_dict']
        # シンプルに、ランダムで、
        random_id = random.choice(list(cot_sample_dict.keys()))
        few_shot_str = cot_sample_dict[random_id]['few-shot']

        # 後は述語項構造解析を指示
        zero_shot_str = prompt_message.ret_zero_shot_simple(sen_str)
        # 励ます
        cheering_str = prompt_message.add_cheering()
        prompt_str = few_shot_str + '\n' + zero_shot_str + cheering_str
        messages.append( prompt_util.ret_role_dict('user', prompt_str ) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def chain_of_thougth_prompt(cls, args):
        """chain of thought prompt
        | タスクの説明、述語項目構造を解析する例を示す。今度はこの文に対してお願いします。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        
        # train data から 持ってきた 述語項構造解析の例を示す
        cot_sample_dict = args['cot_sample_dict']
        random_id = random.choice(list(cot_sample_dict.keys()))
        cot_str = cot_sample_dict[random_id]['cot']
        # シンプルに、ランダムで、
        # 後は述語項構造解析を指示
        zero_shot_str = prompt_message.ret_zero_shot_simple(sen_str)
        prompt_str = cot_str + '\nでは、次のタスクです。' + zero_shot_str

        messages.append( prompt_util.ret_role_dict('user', prompt_str ) )        
        # 後は述語項構造解析を指示
        # print(["cot prompt", len(prompt_str)])

        req_res.append(messages)

        return req_res, 'no_assistant'

    @classmethod
    def chain_of_thougth_mod_knp_prompt(cls, args):
        """chain of thought modify knp version prompt
        | タスクの説明、KNPの修正を行いながら、述語項目構造を解析する例を示す。今度はこの文に対してお願いします。
        """
        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []

        # train data から 持ってきた 述語項構造解析の例を示す
        cot_sample_dict = args['cot_sample_dict']
        # シンプルに、ランダムで、
        random_id = random.choice(list(cot_sample_dict.keys()))
        cot_str = cot_sample_dict[random_id]['cot_compare_knp']

        zero_shot_str = prompt_message.ret_zero_shot_simple(sen_str)
        prompt_str = cot_str + '\nでは、次のタスクです。' + zero_shot_str

        messages.append( prompt_util.ret_role_dict('user', prompt_str ) ) 
        # print(["cot knp prompt", len(prompt_str)])

        req_res.append(messages)

        return req_res, 'no_assistant'
        # return req_res, 'no_assistant'

    @classmethod
    def prompt_header_template(cls, sen_str):
        messages = []
        # messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase()) )
        messages.append( prompt_util.ret_role_dict('user', prompt_message.prompt_header(sen_str)) )
        return messages

    @classmethod
    def prompt_header_english_template(cls, sen_str):
        messages = []
        # messages.append( prompt_util.ret_role_dict('system', prompt_message.ret_system_phrase_english()) )
        messages.append( prompt_util.ret_role_dict('user', prompt_message.prompt_english_header(sen_str)) )
        return messages

    # 言い換える
    @classmethod
    def paraphrase_prompt(cls, args):
        """ 言い換えする
        | タスクの説明、例文を新聞記事風に言い換えてもらう。responseを保持。
        | その上で、述語項構造解析を行う。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # タスク定義などを設置
        messages = []
        paraphrase_step1 = prompt_message.paraphrase_prompt_step1(sen_str)
        messages.append( prompt_util.ret_role_dict('user', paraphrase_step1) )
        req_res.append(messages)

        messages = []
        paraphrase_step2 = prompt_message.paraphrase_prompt_step2()
        paraphrase_step2 = prompt_message.task_definition()  + paraphrase_step2
        messages.append( prompt_util.ret_role_dict('user', paraphrase_step2) )
        req_res.append(messages)
        
        return req_res, 'incremental_assistant'

        # 言い換える
    @classmethod
    def paraphrase_cont_prompt(cls, args):
        """ 言い換えする
        | タスクの説明、例文を新聞記事風に言い換えてもらう。responseを保持。
        | その上で、述語項構造解析を行う。
        | 途中でresponseを得ずにまとめて答えを得る。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # タスク定義などを設置
        messages = []
        paraphrase_step1 = prompt_message.paraphrase_prompt_step1(sen_str)

        paraphrase_step2 = prompt_message.paraphrase_prompt_step2()
        paraphrase_step2 = prompt_message.task_definition()  + paraphrase_step2
        
        paraphrase_step = paraphrase_step1 + '\n' + paraphrase_step2
        
        messages.append( prompt_util.ret_role_dict('user', paraphrase_step) )
        req_res.append(messages)
        
        return req_res, 'no_assistant'
    
    # 言い換える
    @classmethod
    def paraphrase_cont_prompt2(cls, args):
        """ 言い換えする
        | タスクの説明、例文を新聞記事風に言い換えてもらう。responseを保持。
        | その上で、述語項構造解析を行う。まとめる。listに格納。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # タスク定義などを設置
        messages = []
        paraphrase_step1 = prompt_message.paraphrase_prompt_step1(sen_str)
        messages.append( prompt_util.ret_role_dict('user', paraphrase_step1) )

        paraphrase_step2 = prompt_message.paraphrase_prompt_step2()
        paraphrase_step2 = prompt_message.task_definition()  + paraphrase_step2
        messages.append( prompt_util.ret_role_dict('user', paraphrase_step2) )
        req_res.append(messages)
        
        return req_res, 'incremental_assistant'

    # 読み込んでもらう
    @classmethod
    def reading_prompt(cls, args):
        """ 読み解いてもらう
        | タスクの説明、文を読み解いて内容を列挙してもらう。responseを保持。
        | その上で、述語項構造解析を行う。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        reading_step1 = prompt_message.reading_prompt_step1(sen_str)
        messages.append( prompt_util.ret_role_dict('user', reading_step1) )
        req_res.append(messages)

        messages = []
        
        reading_step2 = prompt_message.reading_prompt_step2()
        reading_step2 = prompt_message.task_definition()  + reading_step2
        messages.append( prompt_util.ret_role_dict('user', reading_step2) )
        req_res.append(messages)
        
        return req_res, 'incremental_assistant'

    # 読み込んでもらう
    @classmethod
    def reading_cont_prompt(cls, args):
        """ 読み解いてもらう
        | タスクの説明、文を読み解いて内容を列挙してもらう。responseを保持。
        | その上で、述語項構造解析を行う。
        | responseを得ずにまとめてやっちゃう
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        reading_step1 = prompt_message.reading_prompt_step1(sen_str)

        reading_step2 = prompt_message.reading_prompt_step2()
        reading_step2 = prompt_message.task_definition()  + reading_step2
        
        # 文字列としてまとめちゃう
        reading_step = reading_step1 + '\n' + reading_step2

        messages.append( prompt_util.ret_role_dict('user', reading_step) )
        req_res.append(messages)
        
        return req_res, 'no_assistant'
    
    # 読み込んでもらう
    @classmethod
    def reading_cont_prompt2(cls, args):
        """ 読み解いてもらう
        | タスクの説明、文を読み解いて内容を列挙してもらう。responseを保持。
        | その上で、述語項構造解析を行う。
        | responseを得ずにまとめてやっちゃう。listに入れてまとめて投げる。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        reading_step1 = prompt_message.reading_prompt_step1(sen_str)
        messages.append( prompt_util.ret_role_dict('user', reading_step1) )

        reading_step2 = prompt_message.reading_prompt_step2()
        reading_step2 = prompt_message.task_definition()  + reading_step2
        messages.append( prompt_util.ret_role_dict('user', reading_step2) )
        
        # まとめちゃう
        req_res.append(messages)
        
        return req_res, 'no_assistant'

    # 翻訳してから解析してもらう
    @classmethod
    def translation_prompt(cls, args):
        """ 翻訳してもらう
        | まずは、翻訳。responseを保持。
        | その上で、述語項構造解析を行う。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        translation_step1 = prompt_message.translation_prompt_step1(sen_str)
        messages.append( prompt_util.ret_role_dict('user', translation_step1) )
        req_res.append(messages)

        messages = []
        translation_step2 = prompt_message.translation_prompt_step2()
        messages.append( prompt_util.ret_role_dict('user', translation_step2) )
        req_res.append(messages)
        
        messages = []
        translation_step3 = prompt_message.translation_prompt_step3()

        messages.append( prompt_util.ret_role_dict('user', translation_step3) )
        req_res.append(messages)

        return req_res, 'incremental_assistant'

            # 翻訳してから解析してもらう
    @classmethod
    def translation_cont_prompt(cls, args):
        """ 翻訳してもらう
        | まずは、翻訳。responseを保持。
        | その上で、述語項構造解析を行う。
        | まとめて行う。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        messages = []
        translation_step1 = prompt_message.translation_prompt_step1(sen_str)
        translation_step2 = prompt_message.translation_prompt_step2()
        translation_step3 = prompt_message.translation_prompt_step3()
        
        translation_step = translation_step1 + '\n' + translation_step2 + '\n' + translation_step3
        
        messages.append( prompt_util.ret_role_dict('user', translation_step) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    # 日本語の結果と翻訳の結果を比較してもらう
    @classmethod
    def compare_translation_prompt(cls, args):
        """ 
        | まずは、zero-shotを行う。ついで、翻訳して、responseを保持。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # 日本語で述語項目構造解析する
        messages = []
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_simple(sen_str)) )
        req_res.append(messages)

        # 英訳をしてもらい、述語項目構造解析してもらう
        messages = []
        translation_step1 = prompt_message.translation_prompt_step1(sen_str)
        translation_step2 = prompt_message.translation_prompt_step2()
        translation_step3 = translation_step1 + '\n' +  translation_step2
        messages.append( prompt_util.ret_role_dict('user', translation_step3) )
        req_res.append(messages)

        # それらの結果を比較してもらう。
        messages = []
        compare_step1 = prompt_message.compare_translation_prompt_step1()
        messages.append( prompt_util.ret_role_dict('user', compare_step1) )
        
        compare_step2 = prompt_message.compare_translation_prompt_step2()
        messages.append( prompt_util.ret_role_dict('user', compare_step2) )
        req_res.append(messages)

        return req_res, 'flow_merge'

    # 日本語の結果と翻訳の結果を比較してもらう
    @classmethod
    def compare_translation_cont_prompt(cls, args):
        """ 
        | まずは、zero-shotを行う。ついで、翻訳して、responseを保持。
        | まとめます。文字列として1つに分けておきます。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # 日本語で述語項目構造解析する
        messages = []
        japanese_step = prompt_message.ret_zero_shot_simple(sen_str)
        
        # 英訳をしてもらい、述語項目構造解析してもらう
        translation_step1 = prompt_message.translation_prompt_step1(sen_str)
        translation_step2 = prompt_message.translation_prompt_step2()
        translation_step3 = translation_step1 + '\n' +  translation_step2
        
        # それらの結果を比較してもらう。
        compare_step1 = prompt_message.compare_translation_prompt_step1()
        compare_step2 = prompt_message.compare_translation_prompt_step2()
        compare_step3 = compare_step1 + '\n' +  compare_step2

        prompt_str = japanese_step + '\n' + translation_step3 + '\n' + compare_step3 
        messages.append( prompt_util.ret_role_dict('user', prompt_str) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'

    # 日本語の結果と翻訳の結果を比較してもらう
    @classmethod
    def compare_translation_cont_prompt2(cls, args):
        """ 
        | まずは、zero-shotを行う。ついで、翻訳して、responseを保持。
        | まとめます2。ひとつにまとめます。辞書に分けておきます。
        """

        req_res = []
        
        org_dict = args['org_dict']
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)

        # 日本語で述語項目構造解析する
        messages = []
        messages.append( prompt_util.ret_role_dict('user', prompt_message.ret_zero_shot_simple(sen_str)) )
        
        # 英訳をしてもらい、述語項目構造解析してもらう
        translation_step1 = prompt_message.translation_prompt_step1(sen_str)
        translation_step2 = prompt_message.translation_prompt_step2()
        translation_step3 = translation_step1 + '\n' +  translation_step2
        messages.append( prompt_util.ret_role_dict('user', translation_step3) )

        # それらの結果を比較してもらう。
        compare_step1 = prompt_message.compare_translation_prompt_step1()
        messages.append( prompt_util.ret_role_dict('user', compare_step1) )
        compare_step2 = prompt_message.compare_translation_prompt_step2()
        messages.append( prompt_util.ret_role_dict('user', compare_step2) )
        
        req_res.append(messages)

        return req_res, 'no_assistant'


    # KNP、正解のテーブルは出力できるようになった。
    def ret_table_line_from_knp(self, knp_sub_pred_dict):
        row_dict, row_rel_dict = self.ret_table_row_dict(knp_sub_pred_dict)
        rline = prompt_util.ret_table_row_lines(row_dict)
        sline = prompt_util.ret_sentence_lines(row_dict)
        return rline, sline

    def ret_empty_knp_line(self, knp_pred_dict):
        a_row_dict, a_row_rel_dict = self.ret_table_row_dict(knp_pred_dict)
        empty_row_dict = prompt_util.ret_pred_row_table_dict(a_row_dict)
        rline = prompt_util.ret_table_row_lines(a_row_dict)
        stline = prompt_util.ret_table_row_lines(empty_row_dict)

        return rline, stline


    def ret_knp_pred_list(self, knp_pred_dict):
        a_row_dict, a_row_rel_dict = self.ret_table_row_dict(knp_pred_dict)
        pred_list = prompt_util.ret_pred_list(a_row_dict)
        return pred_list


    # 正解のKNP結果と、Anaphoraの結果を比較しつつ、promptの文面を検討します。
    def compare_knp_result_dict(self, org_dict, knp_correct_pred_dict, knp_pred_dict):
        
        rlist = []
        a_row_dict, a_row_rel_dict = self.ret_table_row_dict(knp_pred_dict)
        c_row_dict, c_row_rel_dict = self.ret_table_row_dict(knp_correct_pred_dict)

        # タスクの説明をします
        rlist.append(prompt_message.task_definition())

        # 対象文章を示します。
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)
        rlist.append(prompt_message.target_sentences(sen_str))

        # 係り受け解析の結果を示し、修正していく旨、述べる。
        first_tline = prompt_util.ret_table_row_lines(a_row_dict)
        rlist.append(prompt_message.start_chain_of_thought_in_modification_process(first_tline))

        # 述語の不足を検出して表を補います。
        lost_pred_list = []
        for senid, pred_dict in c_row_dict.items():
            for pred, pred_content_dict in pred_dict.items():
                if not pred in a_row_dict[senid]:
                    lost_pred_list.append(pred)
                    a_row_dict[senid][pred] = prompt_util.ret_table_case_dict_value_list()
        str3 = "まず、述語が正しく抽出できているか確認します。"
        rlist.append(str3)

        lost_pred_list = [f'「{element}」' for element in lost_pred_list]
        str4 = ''.join(lost_pred_list)
        str4 = str4 + 'の述語が足りていません。これら表現は何らかの動作を表します。テーブルにそれら述語を追加すると、以下のようになります。\n'
        rlist.append(str4)

        mod_a_tline = prompt_util.ret_table_row_lines(a_row_dict)
        # KNPのdictに追加して継続。
        rlist.append(mod_a_tline + '\n')
        
        # 格要素のチェックを実施。
        str5 = 'では、次に各述語の格解析の結果である格要素をチェックします。'
        rlist.append(str5)

        for senid, pred_dict in a_row_dict.items():
            c_row = c_row_dict[senid]
            for pred, pred_content_dict in pred_dict.items():
                for gr, elem_list in pred_content_dict.items():
                    if pred in c_row:
                        c_elem_list = c_row_dict[senid][pred][gr]
                        c_rel_dict = c_row_rel_dict[senid][pred][gr]
                        check_list = prompt_message.check_case_element_prompt_list(gr, pred, elem_list, c_elem_list, c_rel_dict)
                        for rstr in check_list:
                            rlist.append(rstr)

        str6 = """最後にそれぞれの述語や格要素が矛盾していないか、確認します。"""
        rlist.append(str6)
        c_tline = self.ret_table_row_lines(c_row_dict)
        str7 = f"""OKです。以下が最終的な述語項構造解析の結果です。\n\n{c_tline}"""
        rlist.append(str7)

        prompt_msg = '\n'.join(rlist)
        # print(prompt_msg)
        return prompt_msg

    # スタンダードなCoTのpromptの文面を検討します。
    def chain_of_thought_for_pasa(self, org_dict, knp_correct_pred_dict):
        
        rlist = []
        c_row_dict, c_row_rel_dict = self.ret_table_row_dict(knp_correct_pred_dict)

        # タスクの説明をします
        rlist.append(prompt_message.task_definition())
        
        # 対象文章を示します。
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)
        rlist.append(prompt_message.target_sentences(sen_str))
        
        # Chain of Thought 始まるお 宣言
        rlist.append(prompt_message.start_chain_of_thougth())

        # 1. 述語を抽出します。
        
        a_row_dict = {}
        pred_set = set()
        for senid, pred_dict in c_row_dict.items():
            if not senid in a_row_dict:
                a_row_dict[senid] = {}
            for pred, pred_content_dict in pred_dict.items():
                a_row_dict[senid][pred] = prompt_util.ret_table_case_dict_value_list()
                pred_set.add(pred)
        pred_list = list(pred_set)
        rlist.append(prompt_message.extract_predicate(pred_list))

        # 述語を表にしました。まだ格要素は埋まっていません。
        a_tline = self.ret_table_row_lines(a_row_dict)
        rlist.append(prompt_message.show_init_table(a_tline))

        # 格要素を見つめます
        rlist.append(prompt_message.extract_case_element(a_row_dict, c_row_dict, c_row_rel_dict))
        
        # 確認します。
        rlist.append(prompt_message.check_result() )

        # 結果の表を表示ます。お疲れ様でした。
        c_tline = self.ret_table_row_lines(c_row_dict)
        rlist.append(prompt_message.show_table(c_tline))
        
        prompt_msg = '\n'.join(rlist)
        # print(prompt_msg)
        return prompt_msg

    ## few-shot-simple
    def few_shot_simple(self, org_dict, knp_correct_pred_dict):       
        
        # テーブルの辞書を返す
        c_row_dict, c_row_rel_dict = self.ret_table_row_dict(knp_correct_pred_dict)

        # 対象文章を示します。
        sen_str = prompt_util.ret_sentence_line_simple(org_dict)
        table = self.ret_table_row_lines(c_row_dict)
        msg = prompt_message.few_shot_sample_simple(sen_str, table)
        
        return msg


    def ret_table_row_dict(self, knp_sub_pred_dict):
        row_dict = {}
        row_rel_dict = {}
        for senid, elem_list in knp_sub_pred_dict.items():
            if not senid in row_dict:
                row_dict[senid] = {}
                row_rel_dict[senid] = {}
            
            for tmp_dict in elem_list:
                pred = tmp_dict['pred']
                if not pred in row_dict[senid]:
                    row_dict[senid][pred] = prompt_util.ret_table_case_dict_value_list()
                    row_rel_dict[senid][pred] = prompt_util.ret_table_case_dict_value_dict()
                gr = tmp_dict['gr']
                rel_type = tmp_dict['rel_type']
                rel_dist = tmp_dict['rel_dist']
                target = tmp_dict['target']
                if gr in row_dict[senid][pred]:
                    row_dict[senid][pred][gr].append(f'{target}')
                    row_rel_dict[senid][pred][gr][target] = {'rel_type': rel_type, 'rel_dist': rel_dist}

        return row_dict, row_rel_dict

    def ret_table_row_lines(self, row_dict):
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

    def ret_table_row_lines(self, row_dict):
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


    def ret_sentence_lines(self, row_dict):
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


    def filter_id_dict_by_dist_dict(self, dist_dict, knp_pred_dict):
        target_dict = {}
        for id1, knp_sub_pred_dict in knp_pred_dict.items():
            for senid, tmp_list in knp_sub_pred_dict.items():
                for tmp_dict in tmp_list:
                    rel_type = tmp_dict['rel_type']
                    rel_dist = tmp_dict['rel_dist']
                    if dist_dict['rel_type'] == tmp_dict['rel_type']:
                        if dist_dict['rel_dist'] == tmp_dict['rel_dist']:
                            target_dict[id1] = True
                            break
        return target_dict


    def ret_table_sample(self, phase_list, org_dict, train_test_id_dict):
        correct_table_dict = {}
        ana_table_dict = {}
        for phase in  ['dev']:
            target_id_list = train_test_id_dict[phase]
            
            correct_table_dict[phase] = {}
            ana_table_dict[phase] = {}
            show_count = 0
            for id1 in target_id_list:
                line = self.ret_org_line_simple(org_dict[id1])
                # 正解
                c_tline, c_sline = self.ret_table_line_from_knp(knp_pred_dict[id1])
                correct_table_dict[phase][id1] = {'table': c_tline, 'sentences': c_sline}
                
                # anaphoraで解析した結果
                a_tline, a_sline = self.ret_table_line_from_knp(knp_pred_ana_dict[id1])
                ana_table_dict[phase][id1] = {'table': a_tline, 'sentences': a_sline}

                show_count += 1

                if show_count == 5:
                    break

        JsonReadWrite.write_json('./workplace/prompt/', 'correct_table_dict.json', correct_table_dict)
        JsonReadWrite.write_json('./workplace/prompt', 'ana_table_dict.json', ana_table_dict)


def ret_bun_word(list1):
    rlist1 = []
    for bun in list1:
        bstr = bun.split(' ')[0]
        rlist1.append(bstr)
    rstr = ''.join(rlist1)
    return rstr

def main():

    # 正解データ、†rain_dev_test_id、元文
    knp_pred_dict, train_test_id_dict, org_dict = tfu.ret_experimental_files()
    
    # KNPのanaphoraの結果
    json_open = open('./intermediate_data/knp_pred_ana1.json', 'r')
    knp_pred_ana_dict = json.load(json_open) 

    # KNPのanaphoraの結果
    json_open = open('./intermediate_data/ss.json', 'r')
    ss_dict = json.load(json_open) 

    # KNPのanaphoraの結果
    json_open = open('./intermediate_data/knp1.json', 'r')
    knp_bun_dict = json.load(json_open)

    core_rel_dict = {}
    for id1, sen_dict in knp_bun_dict.items():
        if not id1 in core_rel_dict:
            core_rel_dict[id1] = []
        for sid, dep_dict in sen_dict.items():
            sennum1 = sid.split('-')[-1]
            for bunnum, bun_dict in dep_dict.items():
                word = ret_bun_word(bun_dict['words'])
                
                for rel in bun_dict['rel_list']:
                    if rel['type'] == '=':
                        target = rel['target']
                        if 'sid' in rel:
                            tsid = rel['sid']
                            tsennum1 = tsid.split('-')[-1]
                            pstr = f'文{sennum1}の「{word}」は 文{tsennum1}の「{target}」と同じ内容を指しています。'
                        else:
                            pstr = f'文{sennum1}の「{word}」と「{target}」は同じものを指しています。'
                        core_rel_dict[id1].append(pstr)

    phase = 'train'
    """
    trainのデータからfew-shot や CoT で使うデータを作成する。
    後でハードコードする。ゼロを含むように
    """
    train_list = train_test_id_dict['train']
    # target_id_list = random.sample(train_list, 5)
    target_train_id_list = ['w201106-0000846480', 'w201106-0000899496', 'w201106-0000875771', 'w201106-0000636717', 'w201106-0001111591']

    box = MakePromptJson()
    
    # Few-shot のためのデータを作る。train dataから作る。devやtestデータでのpromptを作る際に呼び出す。
    cot_dict = {}
    for id1 in train_list:
    # for id1 in target_id_list:
        # ID ごとに prompt の jsonとなるように。
        # KNPと比較型の chain of thought/本文と述語項構造解析の過程とテーブルの結果が帰ってくる
        cot_sample_knp = box.compare_knp_result_dict(org_dict[id1], knp_pred_dict[id1], knp_pred_ana_dict[id1])
        # ストレートのChain of thought/本文と述語項構造解析の過程とテーブルの結果が帰ってくる
        cot_sample_straight = box.chain_of_thought_for_pasa(org_dict[id1], knp_pred_ana_dict[id1])
        # few-shot/本文と本文と述語項構造解析の結果が帰ってくる
        few_shot_one = box.few_shot_simple(org_dict[id1], knp_pred_dict[id1])

        cot_dict[id1] = {
            'cot': cot_sample_straight, 
            'cot_compare_knp': cot_sample_knp, 
            'few-shot': few_shot_one
            }

    """
    devデータでpromptのjsonを作成する
    """
    prompt_dict = {}
    knp_empty_dict = {}
    knp_pred_elem_dict = {}
    phase = 'dev'
    # target_id_list = ['w201106-0002000003', 'w201106-0002000000', 'w201106-0002000390', 'w201106-0002000186', 'w201106-0002000002']
    target_id_list = train_test_id_dict['dev']
    for id1 in target_id_list:
    # for id1 in train_test_id_dict[phase]:
        if id1 in ss_dict:
            ss_id = ss_dict[id1]['response'][0]['id_list'][0]
        else:
            print(f"ss {id1} out")
            ss_id = ss_dict['w201106-0000846480']
        cot_ss_dict = cot_dict[ss_id]
        core_rel_list = core_rel_dict[id1]

        knp_line, knp_empty_line =  box.ret_empty_knp_line(knp_pred_ana_dict[id1])
        a_row_dict, a_row_reldict = box.ret_table_row_dict(knp_pred_ana_dict[id1])
        aline, sline = box.ret_table_line_from_knp(knp_pred_ana_dict[id1])
        knp_pred_list = box.ret_knp_pred_list(knp_pred_ana_dict[id1])

        args = {
            'org_dict': org_dict[id1],
            'correct_knp_pred_dict': knp_pred_dict[id1],
            'anaphora_knp_pred_dict': knp_pred_ana_dict[id1], 
            'cot_sample_dict' : cot_dict, 
            'cot_ss_dict' : cot_ss_dict,
            'core_rel_list' : core_rel_list,
            'knp_empty_table': knp_empty_line, 
            'knp_table': knp_line,
            'knp_pred_list': knp_pred_list
        }
        prompt_dict1 = box.ret_prompt_dict(args)
        prompt_dict[id1] = prompt_dict1
        knp_pred_elem_dict[id1] = a_row_dict

    JsonReadWrite.write_json('./workplace/prompt/', 'over_prompt.json', prompt_dict)
    JsonReadWrite.write_json('./workplace/prompt/', 'knp_pred_elem_dict.json', knp_pred_elem_dict)
    

if __name__=="__main__":
    main()

 