import glob
import re
import os
import pprint as pp
# KWDLC/id/split_for_pas/
from json_read_write import JsonReadWrite

class KWDLCDataLoader(object):

    def ret_train_test_id_dict(self, glob_pattern):
        id_dict = { 'train':[], 'dev': [], 'test':[] }
        id_list1 = glob.glob(glob_pattern)

        for filename in id_list1:
            with open(filename, "r", encoding='utf-8') as f:
                filekey = os.path.basename(filename).split('.')[0]
                lines = f.readlines()
                id_dict[filekey] = [line.rstrip("\n") for line in lines]

        return id_dict
    
    def ret_org_dict(self, glob_pattern):

        org_list1 = glob.glob(glob_pattern)

        print(len(org_list1))
        org_size = len(org_list1)

        org_dict = {}
        count = 0
        for filename in org_list1:
            with open(filename, "r", encoding='utf-8') as f:
                filekey = os.path.basename(filename).split('.')[0]
                lines = f.readlines()
                # print(lines)
                if not filekey in org_dict:
                    org_dict[filekey] = {}
                if count % 100 == 0:
                    print([filekey, count, (count/org_size) * 100.0])
                
                sid = 'dummy'
                for line in lines:
                    line0 = line.rstrip()
                    if '# S-ID:' in line0:
                        line1 = line0.split(' ')[1]
                        sid = line1
                    else:
                        org_dict[filekey][sid] = line0

                count += 1
        
        return org_dict
      # id_dict[filekey] = [line.rstrip("\n") for line in lines]

if __name__=="__main__":
    box = KWDLCDataLoader()
    # '/content/drive/My Drive/data/KWDLC/id/split_for_pas/*.id'
    glob_pattern = './KWDLC/id/split_for_pas/*.id'
    id_dict = box.ret_train_test_id_dict(glob_pattern)   

    BASE_DIR = './'
    orgjsonfile = 'train_test_id.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, id_dict)

    org_glob_pattern2 = './KWDLC/org/*/*.org'
    org_dict = box.ret_org_dict(org_glob_pattern2)
    orgjsonfile = 'org.json'
    JsonReadWrite.write_json(BASE_DIR, orgjsonfile, org_dict)