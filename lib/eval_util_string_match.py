import re

def startswith(str1, str2, length=1):
    for i in range(len(str1), 0, -1):
        substring = str1[:i]
        if len(substring) > length:
            if str2.startswith(substring) == True:
                return True
        else:
            break
    return False

def head_kanji_match(str1, str2, hiragana_length=1):

    match1 = re.findall(r'^([\u4e00-\u9faf]+)([\u3040-\u309fー]*)', str1)
    match2 = re.findall(r'^([\u4e00-\u9faf]+)([\u3040-\u309fー]*)', str2)

    if len(match1) > 0 and len(match2):
        if match1[0][0] == match2[0][0]:
            if len(match1[0][1]) >= hiragana_length and len(match2[0][1]) >= hiragana_length:
                return True
    return False

def partmatch(str1, str2, length=1):
    """片方の文字列の先頭と末尾を削っていき2文字以上の場合にもう一方の文字列に一致がある場合を検出する"""
    l = list(str1)
    cursor1 = 0
    cursor2 = len(l)
    while cursor1 < cursor2:
        cursor1 += 1
        cstr1 = l[cursor1:cursor2]
        if len(cstr1) > length:
            if ''.join(cstr1) in str2:
                return True
        cursor2 = cursor2 - 1
        cstr2 = l[cursor1:cursor2]
        if len(cstr2) > length:
            if ''.join(cstr1) in str2:
                return True
    return False

def ret_match_type(crr_str, gpt_str):
        
    if crr_str == '筆者' and gpt_str == '著者':
        return 'author'
    elif crr_str == '著者' and gpt_str == '筆者':
        return 'author'

    mstr = 'not_match'
    if gpt_str == '-' or gpt_str == '':
        return mstr

    if crr_str == gpt_str:
        return 'match'
    
    if gpt_str.startswith(crr_str) == True:   
        mstr = "gpt_start_with_crr"
    elif crr_str.startswith(gpt_str) == True:   
        mstr =  "crr_start_with_gpt"
    elif crr_str in gpt_str:
        mstr =  "gpt_long"
    elif gpt_str in crr_str:
        mstr = "crr_long"
    elif startswith(gpt_str, crr_str, length=1):
        mstr = "head_match"
    elif startswith(crr_str, gpt_str, length=1):
        mstr = "head_match"
    elif partmatch(gpt_str, crr_str, length=1):
        mstr = "part_match"
    elif partmatch(crr_str, gpt_str, length=1):
        mstr = "part_match"
    elif head_kanji_match(crr_str, gpt_str, hiragana_length=1):
        mstr = "head_kanji_match"
    
    return mstr
