# -*- coding: utf-8 -*-

# =====================================================================
# Original: Pi5a:/home/jupyter/work/Oauth/common_lib/get_item.py
# 2025-02-04
# 使用方法：
"""
import sys
LIB_PATH = '/home/jovyan/common_lib'
if LIB_PATH in sys.path:
    print("path OK")
else:
    sys.path.append(LIB_PATH)

from get_item import get_item, wrapGet
"""
# =====================================================================
# <NEW> List リソース(実際にはDICT）の項目値を再帰的に取得する関数
# get_item2(lst:dict, itemName:list):
#   lst: 対象のリソース：DICT
#   itemName: 値を取得する項目名　[level1 項目名, level2 項目名, ... levelN 項目名]
# dotItem2(dot:str, obj, deb=0):
# =====================================================================  

### new get_item2 2026-01-14
def dotItem2(dot:str, obj, deb=0):
    """ dot: str 例："name.family" で get_itemsを実行する。 
    dot: str それ以外は、ERROR """
    try:
        assert type(dot) is str, f"dotItem2: ERROR dot is not str ({type(dot),{f'{dot}'}}"
    except Exception as e:
        print(f"   --- 予期しないエラーが発生しました: {e}")
        return 
    arg = dot.split(".")
    if deb: print(f"arg = {arg}")
    ret = get_item2(obj, arg,)
    if deb: print(f"#9 ret = {ret}")
    return ret

def get_item2(obj, itemNames, deb=0):
    """get_item20の結果を整形する
    itemNames == [] ERROR
    res が[[[]]] とネストする場合は、nest を解除.
    res == [] は None とする。"""
    
    # itemNames == [] ERRORとする。
    try:
        assert itemNames != [], f"get_item2: ERROR - itemNames is []"
    except Exception as e:
        print(f"   --- 予期しないエラーが発生しました: {e}")
        return 
    #assert itemNames != [], f"get_item2: ERROR - itemNames is []"
    res = get_item20(obj, itemNames, deb=deb)
    
    # 無意味なlistのNestを削除。
    while type(res) is list and len(res) ==1:
        res = res[0]
    
    # 最終的に res == [] の時には、 Noneとする。
    if res == []:
        res = None
    return res
    
def get_item20(obj, itemNames, level=None, deb=0):
    r"""obj: dict or list の要素を探索して、該当するデータを返す。
    str, bool, float, int の要素は、そこで探索が中止され、(null) を返す。
    最後のレベルまで探索して、見つからないときには None を返す。
    (null) と None　は、無視されて結果には出力されない。
      
      DEBUG FLAG： deb:0, 1:small log, 2:再帰を表示、3:最大Log　"""

    if level is None:
        level = len(itemNames) # 最初に Level をセット。
    if deb:print(f"{'='*level}> #start: obj:{type(obj)},{obj} iN:{len(itemNames)}, l:{level}, deb:{deb}")

    # 終了判定
    if itemNames ==[]: 
        if deb>2:print(f"   #09 Normal return: {obj}, level={level}")
        return obj
        
    if obj is None: 
        if deb>2:print(f"   #12 None return: {obj}, level={level}")
        #return obj
        return
        
    if type(obj) is str or type(obj) is bool or type(obj) is float or \
             type(obj) is int: 
        if deb>2:print(f"   #15 str, bool, float, int: {obj}, level={level}")
        if level == 0:
            mes = "Normal"
            if deb>2:print(f"   #20 {mes} return: {obj}, level={level}")
            return obj
        else:
            mes = "(null) 打ち切り"
            obj = mes
            if deb>2:print(f"   #20 {mes} return: {obj}, level={level}")
            return
        
    # --- next step
    if type(obj) is dict:
        if deb>1: print(f"{'='*level}> 再帰　{obj.get(itemNames[0])}, {itemNames[1:]}")
        return get_item20(obj.get(itemNames[0]), itemNames[1:], level=level-1, deb=deb)
    
    if type(obj) is list:
        # listを分解して、処理する。len(obj) == 1 のときは、リストを深くしない。
        result = []
        length = len(obj)
        if length == 1:
            i = obj[0]
            if deb>1:print(f"{'='*level}> 再帰　{i}, {itemNames}")
            get_item20(i, itemNames, level=level, deb=deb)
            
        for i in obj:
            if deb>2:print(f"list: for loop: i = {i}")
            if deb>1:print(f"{'='*level}> 再帰　{i}, {itemNames}")
            res = get_item20(i, itemNames, level=level, deb=deb)
            if deb>2:print(f"#22 res = {res}")
            if res is not None:
                result.append(res)
        return result
    # ---
    print(f"unknown type: {obj}, {type(obj)}, level={level}")
    return None



# =====================================================================
# List リソース(実際にはDICT）の項目値を再帰的に取得する関数
# get_item(lst:dict, itemName:list):
#   lst: 対象のリソース：DICT
#   itemName: 値を取得する項目名　[level1 項目名, level2 項目名, ... levelN 項目名]

def get_item(lst, itemName, level=0, deb=0): # deb -- 9:max ... 0:off
    if(deb>1):print(f"  get_item: lst-{type(lst)}, itemName len= {len(itemName)}, level:{level}")
    if type(lst) is str:
        if deb>2: print(f"#24 type(lst) is str ==> return '{level}:{lst}'")
        if itemName != []:
            return f"error:{lst}"
        else:
            return f"{level}:{lst}"
    if (itemName == []) :
        if deb>1:print(f'#11 itemName==[] ==> return lst, lst={type(lst)}')
        return lst
    if type(lst) is list:
        if(deb):print("  ---> LIST, lst len=", len(lst))
        for nnn, jjj in enumerate(lst):
            if(deb>1):print(f"{nnn}) {jjj}")
        results=[]
        for n,i in enumerate(lst):
            if(deb>2):print(f"--- #24 listで分解 n={n+1}/{len(lst)}: i={i}")
            if len(lst) ==1:
                if deb>1:print(f"--- #25 list len=0 再帰呼び出し get_item2(lst[0])")
                #return get_item2(i, itemName, level, deb)
                return get_item(i, itemName, level, deb)
            else:    
                #print(f"--- #26 list len>0 return get_item2(lst[{n}])")
                #res=get_item2(i, itemName, level,deb)
                res=get_item(i, itemName, level,deb)
                if deb>1:print(f"--- #27 list  再帰呼び出し{n+1}/{len(lst)} i={i} get_item2(lst[{n}])= {res}")
                if "error" in res:
                    if deb>2:print("error skip")
                else: results.append(res)
        if len(results) ==1: results= results[0]
        if deb>0:print("#28  LIST: return :", results)
        return results    
    
    if (lst.get(itemName[0], None) is None ) :
        return f"{level}:null"
    lst = lst[itemName[0]]
    itemName = itemName[1:]
    if deb>1:print("#59 再帰関数呼び出し type=", type(lst), itemName, level+1)
    return get_item(lst, itemName, level+1, deb)

# item_get() を wrapして、"2:null" などの "2:"をとり、整形する。
def wrapGet2(aaa, pos, level=0, deb=0):
    depth = len(pos)
    if deb:print("#100 wrapGet2: aaa=", aaa)
    if type(aaa) is list:
        if deb:print("#102 len=", len(aaa))
        # list を分解して、再帰する。
        if len(aaa) ==1: return aaa[0]
        bbb = []
        if deb:print("#104 リストを分解して FOR loop aaa=",aaa)
        for j,i in enumerate(aaa):
            if deb>1:print("#106 j,i=",j,i)
            res = wrapGet2(i, pos, level, deb)
            if deb:print("#108 res=", res)
            if res != "":bbb.append(res)
        return bbb
    # string
    if deb:print("#109 aaa=",aaa)
    ### 2025-06-28
    #print(f"#80 aaa= {aaa}")
    if type(aaa) is dict:
        return aaa
    ### 2025-06-28
    if len(aaa)>1: bbb = aaa.split(":")
    else: bbb = aaa
    if len(bbb) >1:
        aaa = aaa[2:]
        if deb>1:print("#110 bbb[0]=", bbb[0], depth)
        if depth != int(bbb[0]):
            aaa += " (not found)"
    return aaa

def wrapGet(dic, pos, level=0, deb=0):
    if deb: print(f"   wrapGet: pos= {pos}, level= {level}")
    aaa = get_item(dic, pos, level, deb)
    if deb: print(f"wrapGet: #90 type-aaa= {type(aaa)}, aaa= {aaa}")
    if type(aaa) is int or type(aaa) is float:
        return aaa
    #if type(aaa) is str:
    #    return aaa
    return wrapGet2(aaa, pos, level=level, deb=deb)


# ===
if __name__ == "__main__":
    # get_item debug
    res1 = [{"a":["AAA", {"b":["BBB", {"c":{"d":"DDD"}}, {"c":{"d":"DDD2"}}]}]},{"a":"AAA2"}]
    pos1=["a","b","c","d"]
   
    if 0:
        res1 = [{"a":["AAA", {"b":["BBB", {"c":{"d":"DDD"}}, {"c":{"d":"DDD2"}}]}]},{"a":"AAA2"}]
        pos1=["a","b","c","d"]
        print("=============================== TEST")
        print(f"  get_item={get_item(res1,pos1, deb=9)}")
        print(f"  wrapGet={wrapGet(res1,pos1, deb=9)}")
        print("=============================== TEST END")

    # wrapGet debug 2025-06-28
    if 0:
        i_res= {'resourceType': 'Patient', 'id': '81', 'meta': {'versionId': '1', 'lastUpdated': '2025-06-02T22:43:14.439+09:00', 'source': '#jcLu1Q1XtAKX73VM', 'profile': ['http://jpfhir.jp/fhir/eCheckup/StructureDefinition/JP_Composition_eCheckupGeneral']}, 'identifier': [{'system': 'urn:oid:1.2.392.200036.9169.1.9.20.20', 'value': '12345'}], 'name': [{'extension': [{'url': 'http://hl7.org/fhir/StructureDefinition/iso21090-EN-representation', 'valueCode': 'IDE'}], 'use': 'official', 'text': '慶應 太郎', 'family': '慶應', 'given': ['太郎']}, {'extension': [{'url': 'http://hl7.org/fhir/StructureDefinition/iso21090-EN-representation', 'valueCode': 'SYL'}], 'use': 'official', 'text': 'ケイオウ タロウ', 'family': 'ケイオウ', 'given': ['タロウ']}], 'telecom': [{'system': 'phone', 'value': '03-1234-5678', 'use': 'home'}], 'gender': 'male', 'birthDate': '2025-05-29', 'address': [{'use': 'home', 'type': 'postal', 'text': '東京都新宿区信濃町３５', 'line': ['豪徳寺 1-1-1'], 'city': '世田谷区', 'state': '東京都', 'postalCode': '160-0001', 'country': 'JP'}], 'maritalStatus': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'version': '2018-08-12', 'code': 'UNK', 'display': 'unknown'}], 'text': '不明'}}
    
        pos= ['name']
        print(f"\nwrapGet = {wrapGet(i_res, pos, deb=1)}")

    d = {
  "resourceType": "Patient",
  "id": "IHE-tmp",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2024-03-23T11:46:27.079+09:00",
    "source": "#QugUw73uBb8kdc7w",
    "profile": [
      "http://jpfhir.jp/fhir/eCheckup/StructureDefinition/JP_Composition_eCheckupGeneral"
    ]
  },
  "identifier": [
    {
      "system": "urn:oid:1.2.392.200119.6.102.11110101337",
      "value": "Unknown"
    }
  ],
  "name": [
    {
      "extension": [
        {
          "url": "http://hl7.org/fhir/StructureDefinition/iso21090-EN-representation",
          "valueCode": "IDE"
        }
      ],
      "use": "official",
      "text": "愛栄一 太郎",
      "family": "愛栄一",
      "given": [
        "太郎"
      ]
    },
    {
      "extension": [
        {
          "url": "http://hl7.org/fhir/StructureDefinition/iso21090-EN-representation",
          "valueCode": "SYL"
        }
      ],
      "use": "official",
      "text": "アイエイチ タロウ",
      "family": "アイエイチ",
      "given": [
        "タロウ"
      ]
    }
  ],
  "gender": "male",
  "birthDate": "2023-12-13",
  "text": {
    "status": "generated",
    "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p style=\"border:2px #661aff solid; background-color: #e6e6ff; padding: 10px;\"><b>愛栄一 太郎 (official,IDE) アイエイチ タロウ (official,SYL) 　male、生年月日: 2023-12-13</b> (Medical number: Unknown (urn:oid:1.2.392.200119.6.102.11110101337))<br/>住所：(not found)</p></div>"
  }
}
    # wrapGet: test 2
    if 0:
        resName = wrapGet(d, ["resourceType"], deb=9)
        #resName += "/"+wrapGet(d, ["id"])
        print(f"\n     #22 resName= {resName}")
    
    # get_item2: test
    if 1:
        res1 = [{'a': ['AAA', {'b': ['BBB', {'c': {'d': 'DDD'}},
                 {'c': {'d': 'DDD2'}}]}]}, {'a': 'AAA2'}]
        
        pos1 = ["a", "b", "c", "d"]
        print(res1, pos1)
        ret = get_item2(res1, pos1)
        print(f"ret = {ret}")
        ret1 = get_item20(res1, pos1)
        print(f"res1 = {ret1}," )
        res2 = [{"a": {"code": {"coding":123}}}]
        ret2 = get_item2(res2, ["a","code", "coding"])
        print(f"ret2 = {ret2}")

        # Patient
        ret0 = dotItem2("name.extension.valueCode",d)
        print(f"ret0 = {ret0}")
        zz = []
        for i in ["name.use", "name.family", "name.given",
                  "name.extension.valueCode"]:
            ret3 = dotItem2(i, d)
            print(f"i = {i}, ret3 = {ret3}")
            zz.append(ret3)
        for (u,f,g,e) in zip(zz[0], zz[1], zz[2], zz[3]):
            print(f"{u:10}: {f} - {g} ({e})")



    # test 3
    # XML ==> DICT
    # pip install xmltodict
    




    def xml2dic():
        import xmltodict
        import json # 辞書を見やすく表示するために使用

        # XMLファイルを読み込む（バイト文字列として）
        #with open('mylib/sample.xml', 'rb') as fd: # 'rb' (read binary) mode is often recommended for xmltodict
        with open('sample_res/ForSVCM_res/administrative-gender.xml', "rb") as fd:
            xml_content = fd.read()

        # XMLを辞書に変換   attr_prefix='' がないと、要素名に'@'がつく。
        xml_dict = xmltodict.parse(xml_content, attr_prefix='')

        print("--- xmltodict を使用した結果 ---")
        print(json.dumps(xml_dict, indent=4, ensure_ascii=False))

        # 特定の要素にアクセスする例
        if 'root' in xml_dict and 'book' in xml_dict['root']:
            # xmltodict は同じタグ名を自動的にリストにしてくれる
            first_book = xml_dict['root']['book'][0]
            print(f"\n最初の本のタイトル: {first_book['title']}")

            # 属性へのアクセス
            print(f"最初の本のID: {first_book['@id']}") # 属性は '@' プレフィックスでアクセス
    
    # ---
    # xml to dict: debug
    if 0:
        xml2dic()

print("get_item:   === Normal END. ===")