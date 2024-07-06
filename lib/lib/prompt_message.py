def ret_system_phrase():
  str4 = """あなたは日本語の文法に堪能な日本語教師です。日本語テキストの名詞や動詞といった品詞や主語や動詞が理解できて、生徒に指導ができます。
  """
  return str4

def ret_system_phrase_english():
  str4 = """You are a proficient linguist in the grammars of both English and Japanese languages. You possess the ability to understand parts of speech, such as nouns and verbs, as well as subjects and verbs, in English and Japanese texts. This enables you to provide guidance to students.
  """
  return str4

def task_definition():
  str1 = """述語項構造解析とは、文中の動詞や述語とそれに関連する要素（項）の関係を抽出するタスクです。
述語項構造解析では、文の中で主語、目的語、補語（ニ格）などの要素がどの動詞や述語に関連しているかを特定します。
  """
  return str1

def add_cheering():
  str1 = """あなたは絶対に述語項構造解析ができます。自信を持ってください。絶対に述語項目構造解析のテーブルを出力してください。"""
  return str1


def task_definition_english():
  str4 = """Predicate-argument structure analysis is a task that involves extracting the relationships between verbs or predicates and their associated case elements (arguments) in a sentence. In predicate-argument structure analysis, the goal is to identify case elements such as subjects, objects, and complements (indirect objects) in a sentence and determine how they relate to specific verbs or predicates.
  """
  return str4

def target_sentences(sen_str):
  str2 = f"""以下は述語項目構造解析の対象の文です。これらの文はブログ記事の冒頭3文を抜粋したものです。

{sen_str} 
"""
  return str2

def show_target_sentences(sen_str):
  str2 = f"""以下の文をご覧ください。これらの文はブログ記事の冒頭3文を抜粋したものです。

{sen_str} 
"""
  return str2

def target_english_sentences(sen_str):
  str2 = f"""The following are Japanese sentences targeted for predicate-argument structure analysis. These sentences are excerpts from the opening three sentences of a blog article.
{sen_str}

  """
  return str2

def few_shot_sample_simple(sen_str, table):
  
  str1 = task_definition()
  str2 = f"""以下に述語項構造解析のサンプル事例を示します。ブログ記事の冒頭3文を抜粋したものです。これら文を述語項構造解析してテーブルにまとめた結果を示します。

{sen_str}

これに対する述語項目構造解析の結果は以下のテーブルのようにテーブルされます。

{table}

  """
  return str1 + str2

def prompt_header(sen_str):
  rlist = []

  # タスク 定義
  rlist.append(task_definition())
  
  # 対象文書セット
  rlist.append(target_sentences(sen_str))

  return ''.join(rlist)

def prompt_english_header(sen_str):
  rlist = []

  # タスク 定義
  rlist.append(task_definition_english())
  
  # 対象文書セット
  rlist.append(target_english_sentences(sen_str))

  return ''.join(rlist)

## Zero Shot Simple
def ret_zero_shot_simple(sen_str):
  rlist = []
  
  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))

  # Zero shot 指示
  rlist.append( zero_shot_simple() )
  rstr = ''.join(rlist)
  return rstr

## Zero Shot Simple
def ret_zero_shot_ss(sen_str, core_rel_list):
  rlist = []
  
  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))
  rlist.append('文中の同参照の表現について補足します。\n')
  for cstr in core_rel_list:
    rlist.append(cstr + '\n')

  # Zero shot 指示
  rlist.append( zero_shot_simple() )
  rstr = ''.join(rlist)
  return rstr

## Zero Shot With KNP
def ret_zero_shot_with_knp(sen_str, knp_empty_line):
  rlist = []
  
  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))

  # Zero shot 指示
  rlist.append( knp_empty_table(knp_empty_line) )
  rstr = ''.join(rlist)
  return rstr

def knp_empty_table(knp_empty_line):
  str2 = f"""こちらは先にあげたブログ記事からの文から述語を抽出してテーブルにまとめたものです。
  {knp_empty_line}
  
  先に挙げたブログ記事の冒頭3文を読んで述語項構造解析を行い、テーブルの述語に対する主語、目的語、補語（ニ格）を見つけてきてテーブルに追加してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。
  """
  return str2

## Zero Shot With KNP
def ret_zero_shot_modify_knp(sen_str, knp_line):
  rlist = []
  
  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))

  # Zero shot 指示
  rlist.append( knp_modify_table(knp_line) )
  rstr = ''.join(rlist)
  return rstr

def knp_modify_table(knp_line):
  str2 = f"""以下のテーブルは先にあげたブログ記事の文に対して述語項構造解析を行い、テーブルにまとめたものです。
  {knp_line}
  
  テーブルの述語項構造解析の主語、目的語、補語（ニ格）の結果に矛盾や不足があるようでしたら、テーブルを修正してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。
  """
  return str2

def zero_shot_simple():
  str2 = """先に挙げたブログ記事の冒頭3文に対して述語項構造解析を行い、文番号、述語、主語、目的語、補語（ニ格）を1つの行とするテーブル形式で出力してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。
  """
  return str2

## Zero Shot Standard
def ret_zero_shot_standard(sen_str):
  rlist = []
  
  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))

  # Zero shot 指示
  rlist.append( zero_shot_standard() )
  rstr = ''.join(rlist)
  return rstr

def zero_shot_standard():
  str2 = """以下に述語項目構造の手順を示します。以下の手順に従って述語項目構造解析を行なってください。
  述語の抽出：各文に含まれる述語を抽出してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。連体修飾節の述語、サ変名詞、語尾の述語含めて、全て列挙してください。
  構文意味解析処理：述語ごとに、述語と同文内にある「主語（ガ格）」と「目的語（ヲ格）」と「斜格の要素（ニ格）」を抽出してください。
  省略された格要素の検討：「主語（ガ格）」と「目的語（ヲ格）」と「斜格の要素（ニ格）」の候補は、その文中では省略されている格要素も含めて列挙してください。 省略されている格要素には「著者」や「人一般」といった文に明示的に書かれていない要素も含めてください。
  述語ごとの格要素のまとめあげ: 述語、主語（ガ格）、目的語（ヲ格）、斜格の要素（ニ格）の候補の4つ組を作ってください。
  出力形式: 文の番号、述語、主語（ガ格）の候補、目的語（ヲ格）の候補、斜格の要素（ニ格）の5列を1つの行とするテーブル形式で出力してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。
  """
  return str2

def zero_shot_order_list():
  rlist = ['以下に述語項目構造の手順を示します。以下の手順に従って述語項目構造解析を行なってください。', 
  '述語の抽出：各文に含まれる述語を抽出してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。連体修飾節の述語、サ変名詞、語尾の述語含めて、全て列挙してください。', 
  '構文意味解析処理：述語ごとに、述語と同文内にある「主語（ガ格）」と「目的語（ヲ格）」と「斜格の要素（ニ格）」を抽出してください。', 
  '省略された格要素の検討：「主語（ガ格）」と「目的語（ヲ格）」と「斜格の要素（ニ格）」の候補は、その文中では省略されている格要素も含めて列挙してください。 省略されている格要素には「著者」や「人一般」といった文に明示的に書かれていない要素も含めてください。', 
  '述語ごとの格要素のまとめあげ: 述語、主語（ガ格）、目的語（ヲ格）、斜格の要素（ニ格）の候補の4つ組を作ってください。', 
  '出力形式: 文の番号、述語、主語（ガ格）の候補、目的語（ヲ格）の候補、斜格の要素（ニ格）の5列を1つの行とするテーブル形式で出力してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。'
  ]
  return rlist

def start_chain_of_thougth():
  str2 = '以下に述語項目構造解析の手順を示します。'
  return str2

def start_chain_of_thought_in_modification_process(table_line):
  knp_read = f"""日本語係り受け解析器の述語述語項構造解析の結果を手がかりに、述語項構造解析をしていきます。係り受け解析器による述語項構造解析の結果をテーブルにまとめると以下のようになります。
  
{table_line}

このテーブルの結果を確認し、必要であれば修正していきます。"""
  return knp_read

def extract_predicate(pred_list):

  pred_series = '、'.join(pred_list)
  pred_list = [f'「{element}」' for element in pred_list]
  pred_list_str = '、'.join(pred_list)
  str3 = f"""文から述語を見つけます。以下の述語がありました。\n{pred_list_str}
  """
  return str3

def show_init_table(init_table_line):
  str3 = f"""これら述語と述語の主語、目的語、補語（ニ格）などの格要素をテーブルにまとめました。まだ格要素は埋まっていません。\n
{init_table_line}
  """
  return str3

def extract_case_element(a_row_dict, c_row_dict, c_row_rel_dict):
    rlist = []
    str5 = '文を読んで述語ごとの格要素を見つけます。'
    rlist.append(str5)
    for senid, pred_dict in a_row_dict.items():
        c_row = c_row_dict[senid]
        for pred, pred_content_dict in pred_dict.items():
            for gr, elem_list in pred_content_dict.items():
                if pred in c_row:
                    c_elem_list = c_row_dict[senid][pred][gr]
                    c_rel_dict = c_row_rel_dict[senid][pred][gr]
                    check_list = check_case_element_prompt_list(gr, pred, elem_list, c_elem_list, c_rel_dict)
                    for rstr in check_list:
                        rlist.append(rstr)

    return '\n'.join(rlist)

def ret_find_case_elem_comment(gr, pred, elem, c_rel_dict):
  rel_dist = c_rel_dict['rel_dist']
  rel_type = c_rel_dict['rel_type']
  rstr = ''
  rstr = rel_dist + ' ' + rel_type + ' ' + elem
  if rel_type == 'zero':
      if rel_dist == 'outer':
          rstr = f'文中に格要素のテーブル現は見つからないが、述語「{pred}」に{gr}が必要です。文外の「{elem}」を想定して格要素と解釈します。'
      elif rel_dist == 'inter_sentence':
          rstr = f'述語「{pred}」に{gr}が必要です。前文の「{elem}」 が省略された解釈します。'
      elif rel_dist == 'intra_sentence':
          rstr = f'述語「{pred}」に{gr}が必要です。同文内の「{elem} 」が省略されたと解釈します。'
  elif rel_type == 'dep':
      rstr = f'述語「{pred}」に{gr}が必要です。同文内の「{elem}」が述語「{pred}」に係ると解釈します。'
  elif rel_type == 'rentai':
      rstr = f'述語「{pred}」に{gr}が必要です。述語「{pred}」の直後の「{elem}」 が連体修飾節として格要素になると解釈します。'
  else:
      rstr = f'述語「{pred}」に{gr}が必要です。「{elem}」 が {pred} に関係していそうです。'
  
  return rstr

def ret_not_found_requreid_case_element_message(pred, gr):
  str1 = "述語「{pred}」に必要な {gr} の格要素ないです。テキスト中に{gr}に相応しいものテキスト外に不特定:人、不特定:物、不特定:事で埋めます。"

def delete_not_required_element(pred, gr, elem_list, c_elem_list):
  rlist = []
  for elem in elem_list:
    if not elem in c_elem_list:
      rlist.append(f'「{elem} 」は「{pred}」の {gr} として間違っていますね。テーブルから除きます。')
    else:
      rlist.append(f'「{elem} 」は「{pred}」の {gr} としてOKです。')

  rstr = ''.join(rlist)
  return rstr

def check_case_element_prompt_list(gr, pred, elem_list, c_elem_list, c_rel_dict):
  """
  正解の格要素が存在し、KNPの格要素がない場合。格要素ないですね。テキスト中かテキストの外から何らかの格要素を埋める。不特定:人、不特定:物、不特定:事で埋めます。
  正解の格要素が存在し、KNPの格要素があり、正解の格要素に含まれない場合、この格要素は適切ではないので、テーブルから削除します、とする。
  正解の格要素が存在せず、KNPの格要素がない場合、OK。
  正解の格要素が存在せず、KNPの格要素がある場合、正解の格要素に含まれない場合、この格要素は適切ではないので、テーブルから削除します、とする。
  """
  rlist = []
  mod_flag = False
  # 格要素確認宣言
  
  # 正解の格要素がある
  if len(c_elem_list) > 0:
    # 必要なものが足りない
    if len(elem_list) == 0: 
        
        str5 = f'述語「{pred}」には {gr}が必要なのですが、テーブルにありません。{gr}を見つけましょう。'
        rlist.append(str5)
        for celem in c_elem_list:
            str2 = ret_find_case_elem_comment(gr, pred, celem, c_rel_dict[celem])
            rlist.append(str2)
        
        csubj = '、'.join(c_elem_list)
        str5 = f'以上より、「{pred}」の {gr} として「{csubj}」 をテーブルに設定します。\n' 
        rlist.append(str5)
        mod_flag = True
    
    elif len(elem_list) > 0:
        # 出力が、間違っていないかチェック
        # 間違ってる格要素を除く
        new_cstr_list = []
        rstr = delete_not_required_element(pred, gr, elem_list, c_elem_list)
        if len(rstr) > 0:
          new_cstr_list.append('delete')
          rlist.append(rstr)
        
        # 正しい 格要素を 列挙する。
        new_cstr_list = []
        for elem in c_elem_list:
          if not elem in elem_list:
            new_cstr_list.append(elem)
            str6 = f'述語「{pred}」の {gr}として「{elem}」 が正しいです。'
            rlist.append(str6)
        
        # 格要素 をまとめる
        csubj = '、'.join(c_elem_list)
        if len(new_cstr_list) == 0:
            str5 = f'テーブルの通り、「{pred} 」の {gr} は「{csubj} 」が正しいです。このままでOKです。\n' 
        elif len(new_cstr_list) > 0:
            str5 = f'以上より、「{pred}」 の {gr} として「{csubj} 」が 正しいです。 テーブルを修正しましょう。\n' 
        rlist.append(str5)
        mod_flag = True

    if mod_flag == True:
      rlist.insert(0, f'述語「{pred}」の{gr}について確認していきます。')
    elif mod_flag == False:
      rlist.insert(0, f'述語「{pred}」の{gr}についても問題なさそうです。')

  
  return rlist


def check_result():
  str5 = """最後にそれぞれの述語や格要素が矛盾していないか、検証します。確認します。何か矛盾が見つかったらその内容を書き出しましょう。

OKですね。
"""
  return str5

def show_table(c_tline):
  rlist = []
  str4 = f"""最終的な述語項構解析の結果のテーブルを示します。

{c_tline}
  """
  return str4
  rlist.append(str5)


# Zero-Shot Prompt Message

## Zero Shot Simple
def ret_zero_shot_simple(sen_str):
  rlist = []

  # タスク 定義 / 対象文書セット
  rlist.append(prompt_header(sen_str))

  # Zero shot 指示
  rlist.append(zero_shot_simple() )

  rstr = '\n'.join(rlist)
  return rstr


def show_few_shot_sample(fs_dict):

  import random
  # キーのリストを取得
  keys = list(fs_dict.keys())

  # ランダムに1つのキーを選ぶ
  random_key = random.choice(keys)

  # 対応する値を取得
  random_dict = fs_dict[random_key]

  sen_str = random_dict['sentenses']
  table = random_dict['table']
  str1 = f"""以下の文を述語項目構造解析したいと思います。これらの文はブログ記事の冒頭3文を抜粋したものです。
  
  {sen_str}
  
  述語項目構造解析の結果は以下のテーブルのようにテーブルされます。

  {table}
  """
  return str1

# 言い換え	言い換えてもらう。言い換えた上で述語項目構造してもらう
def paraphrase_prompt_step1():
  str4 = """この文を新聞記事風に言い換えてください。新聞記者になったつもりで、文中に書かれている物事に関連する人物、事物、時刻などをまとめてださい。新聞記事の例としては以下のように まずは読解内容を列挙してみてください。
  """
  return str4

def paraphrase_prompt_step1(sen_str):
  sentences = show_target_sentences(sen_str)
  str4 = f"""{sentences}
  これらの文を報道記事風に言い換えてください。新聞記者になったつもりで、文1、文2、文3中に書かれている物事に関連する人物、時刻、人物の行動、事実をまとめてださい。新聞記者になったつもりで、文に書かれている事実と、背景について述べてください。

  """
  return str4

def paraphrase_prompt_step2():
  zero_shot_prompt = zero_shot_simple()
  str4 = f"""言い換えした新聞記事風の内容を踏まえつつ、{zero_shot_prompt}
  """
  return str4


# 解釈してもらう	何が読み取れますか？　読みとれた内容を述語ごとにまとめてもらう	未着手
def reading_prompt_step1(sen_str):
  sentences = show_target_sentences(sen_str)
  str4 = f"""{sentences}
この文から何が読み取れますか？ まずは読解内容を列挙してみてください。
  """
  return str4

# 言い換え	言い換えてもらう。言い換えた上で述語項目構造してもらう
def reading_prompt_step2():
  zero_shot_prompt = zero_shot_simple()
  str4 = f"""これまでの読解内容を踏まえつつ、{zero_shot_prompt}
  """
  return str4

# 英訳してもらう
# 解釈してもらう	何が読み取れますか？　読みとれた内容を述語ごとにまとめてもらう	未着手
def translation_prompt_step1(sen_str):
  str4 = f"""Please translate these sentences into English.

  {sen_str}
  """
  return str4

def translation_prompt_step2():
  str2 = task_definition_english()
  str4 = f"""{str2}. Perform predicate-argument structure analysis on the above translated English sentences. 
  Output the results in a tabular format with columns for sentence number, predicate, subject, object, 
  and complement (indirect object), each represented in a single row. 
  """
  return str4

def translation_prompt_step3():
  str4 = """Please translate the above table into Japanese. 
  When translating, be sure to choose phrases from the original Japanese sentences before they are translated into English. 
  Be sure to enclose the table with "|" characters at the leftmost and rightmost ends.
  """
  return str4

def translation_prompt_step4():
  str4 = """Compare the results of predicate-argument structure analysis tables for Japanese and English, 
  and if there are any semantic differences between the analysis results in Japanese and English, 
  please highlight those differences.
  """
  return str4

def translation_prompt_step5():
  str4 = """If the analysis results in English are correct, 
  please incorporate those findings into the results of the Japanese predicate-argument structure analysis, 
  creating a final table of predicate-argument structure analysis results.
  Be sure to enclose the table with "|" characters at the leftmost and rightmost ends.
  """
  return str4

def compare_translation_prompt_step1():
  str2 = """日本語と英語の述語項構造解析の結果を比較してください。日英の結果に何か差はありますか？
  """
  return str2

def compare_translation_prompt_step2():
  str2 = """日本語と英語の述語項構造解析の結果を矛盾なく1つのテーブルに統合してください。英語の述語項構造の結果を日本語に翻訳した上で（日本語に翻訳する際はブログ記事の3文内のテーブル現を用いてください）、述語項構造解析のテーブルは、文番号、述語、主語、目的語、補語（ニ格）を1つの行とするテーブル形式で出力してください。述語は1文に複数ある場合があり、全ての述語を抽出してください。テーブルにはヘッダーをつけてください。テーブルは必ず「|」文字で左端と右端とを閉じておいてください。
  """
  return str2

def ret_summary_prompt(sen_str, knp_pred_list): 
  str2 =  f"""文章を読み、こちらから指定された述語に関しての要約を行ってください。要約は、与えられた述語に対して、「〜が、〜が、〜を、〜に、指定された述語」の形式で行います。要約で使える格助詞は「が、を、に」以外は認められません。「〜も、「〜は、」「〜で、」といった「が、を、に」以外の助詞からは述語に係らないようにしてください。なるべく簡潔な表現を文中から抽出してください。テキスト中に述語に先行する表現が見つからない場合は、「不特定:人」「不特定:物」「筆者」といった表現を用いて要約に含めてください。要約結果は文として成り立つことが絶対に必要です。以下に実施例を示します。
---- 実施例 ----
例文:
文1 「太郎は本屋に行きました。」　
文2 「本を買いました。」
文3 「よく売れた本です。」
要約対象述語：「行きました」、「書いました」、「売れた」。
要約結果：太郎が、本屋に、行きました。太郎が、本を、買いました。本が、不特定:人、に売れた。
---- 実施例ここまで ----

では、要約の対象となる文を示します。これら文はブログ記事の冒頭3文です。以下の要約対象述語に対して要約を作成してください。
例文：
{sen_str} 
要約対象述語: {'、'.join(knp_pred_list)} 
要約結果：
"""
  return str2

