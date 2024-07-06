import json
# JSON形式に変換する際に、インデントと文字コードを指定します

class JsonReadWrite(object):

    @classmethod
    def  write_json(cls, BASE_DIR, orgjsonfile, org_dict):
        json_data = json.dumps(org_dict, indent=4, ensure_ascii=False)
        filename = BASE_DIR + orgjsonfile
        # JSONデータをファイルに保存します
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_data)

if __name__=="__main__":
    BASE_DIR = '/content/drive/My Drive/data/'
    orgjsonfile = 'KWDLC/org.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile)