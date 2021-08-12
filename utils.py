#helper functions to read and extract UMLS from the JSON files

import json

def read_JSON_file(filename):
    '''read JSON files
    input: filename of JSON file
    output: the output string, if file not found, return {}'''
    try:
        with open(filename) as json_file:
            json_file.seek(0)
            json_output_str = json_file.read()
            #print(json_output_str)
    except FileNotFoundError:
        print(filename, 'not found')
        json_output_str = '{}'
    return json_output_str
    
def get_umls_MedCAT(json_output_str):
    '''get the list of UMLS, i.e. CUI and preferred terms from the JSON output
    input: the JSON string of the sequence processed by *SemEHR*
    output: the list of umls, each is a tuple of CUI and its perferred term'''
    json_output = json.loads(json_output_str)
    dict_ent = json_output['entities'] if json_output.get('entities', None) != None else [] # list of unique entities matched to the sequence # if there is no mentions detected, then set it as an empty list [].
    list_umls_desc = []
    for ent_unique in dict_ent.values():
        list_umls_desc.append((ent_unique['cui'],ent_unique['pretty_name']))
    return list_umls_desc

def get_umls_SemEHR(json_output_str):
    '''get the list of UMLS, i.e. CUI and preferred terms from the JSON output
    input: the JSON string of the sequence processed by *SemEHR*
    output: the list of umls, each is a tuple of CUI and its perferred term'''
    
    json_output = json.loads(json_output_str)
    anns_umls = json_output['annotations'][0] # get the UMLS annotations, which is the first part of all 'annotations', the rest two parts are gazeteer-based phenotypes and the sentence splits
    list_umls_desc = []
    for ann in anns_umls:
        ann_features = ann["features"]
        # filtering based on the annotation features - based on negation, semantic type, experiencer, and temporality
        # *you can add your own filters here*
        if ann_features["Negation"] == "Affirmed" and ann_features["STY"] == "Disease or Syndrome" and ann_features["Experiencer"] == "Patient" and ann_features["Temporality"] == "Recent":
            in_text_ann = ann_features["string_orig"]
            umls_code = ann_features["inst"]
            umls_label = ann_features["PREF"]
            list_umls_desc.append((umls_code,umls_label))
    return list_umls_desc
    
def get_sentences_offset_from_SemEHR(json_output_str):
    '''get the sentence offsets from SemEHR
    input: the JSON string of the sequence processed by *SemEHR*
    output: the list of offsets for the sentences, each offset is a tuple of starting and ending positions'''
    json_output = json.loads(json_output_str)
    anns_sents = json_output['annotations'][2] # get the sentence annotations
    list_sent_offsets = []
    for ann in anns_sents:
        pos_start = ann["startNode"]["offset"]
        pos_end = ann["endNode"]["offset"]        
        list_sent_offsets.append((pos_start,pos_end))
    return list_sent_offsets
    
if __name__ == '__main__': 
    subj_id = '0'
    row_id = '0'
    json_doc_file_name = 'doc-%s-%s.json' % (subj_id, row_id)
    print('MedCAT results:')
    print(get_umls_MedCAT(read_JSON_file('./MedCAT_processed_jsons/%s' % json_doc_file_name)))
    print()
    print('SemEHR results - with negation, experiencer, and temporality filters:')
    print(get_umls_SemEHR(read_JSON_file('./SemEHR_processed_jsons/%s' % json_doc_file_name)))
    
    print('\nNB: there are repeated UMLS in the lists, since there are many mentions of the same disease!')
    
    print(get_sentences_offset_from_SemEHR(read_JSON_file('./SemEHR_processed_jsons/%s' % json_doc_file_name)))