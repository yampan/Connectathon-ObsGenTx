### generate_pat.py
# 2026-06-26
#
# IHE-J CTN QEDm 用のPatient リソースを生成。
#---------------------------------------------------------
r"""
〇FHIR SERVERがPUT （update)をサポートしていない時の対策  2026-06-24
0. Patientリソースの詳細は、
   C.QEDm患者一覧.pdf 参照。
   
1. Patient リソースを PUT
   http codeを調べる。
   200： update がOK 
   そのまま、IHEJ-CTN-001 でObservationリソースを生成
   
2. NGならば、
   Patientリソースを POST
   生成されたリソースのリソースIDを調べて、このIDを使用する。

3. resource-id は、
    pats=["IHE-J-CTN-001",
        "IHE-J-CTN-002",
        "IHE-J-CTN-003",
        "IHE-J-CTN-004",]   
    を使用する。

4. C.QEDm患者一覧.txt の 1～4 番を使用する。

"""
 

import json
import os, sys
import random

random.seed(123)


# valueQuantity: ex. 体重
def quant_obs(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", _id=None, v=None):
    
    # counter
    if not hasattr(quant_obs, "N"):
        quant_obs.N = 0
    quant_obs.N += 1

    if _id is None:
        _id = f"obs-body-weight-{quant_obs.N:03}"
    
    if v is None:
        v = random.randint(380, 900) / 10
        
    obs = {
        "resourceType": "Observation",
        "id": _id,
        "meta": {
            "profile": [
            "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_BodyMeasurement"
            ]
        },
        "status": status,
        "category": [
            {
            "coding": [
                {
                "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS",
                "code" : "body-measurement",
                "display" : "Body Measurement"
                },
                {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
                }
            ]
            },
            {
            "coding" : [
                {
                "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_ObservationBodyMeasurementCategory_CS",
                "code" : "weight",
                "display" : "体重"
                }
            ]
            }
        ],
        "code": {
            "coding": [
            {
                "system": "http://loinc.org",
                "code": "29463-7",
                "display": "Body weight"
            },
            {
                "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_ObservationBodyMeasurementCode_CS",
                "code" : "31000296"
            }
            ],
            "text": "体重"
        },
        "subject": {
            "reference": pat
        },
        "effectiveDateTime": day,
        "valueQuantity": {
            "value": v,
            "unit": "kg",
            "system": "http://unitsofmeasure.org",
            "code": "kg"
        }
    }
    return obs



### -----------------------------------------------------------

# 複数のObservationを生成する。
def multi_gen(func, name, pats, stats, days):
    """
    Observation resourceを生成する。
    パラメータは、
    Args:
        func (func): Obs 生成 関数
        name (_type_): _description_
        pats (list): 患者リスト
        stats (list): Statusリスト
        days (list): dateリスト
        
    """
    n=1
    for np, pat in enumerate(pats, start=1):
        pat = f"Patient/{pat}"
        for status in stats:
            for nd, day in enumerate(days, start=1):
                mark = f"P{np}{status[0:2]}D{nd}"
                d = func(pat, status, day=day)
                #print(json.dumps(d, indent=2, ensure_ascii=False))
                fn = f"obs_{name}_{n:02}_{mark}.json"
                fn = os.path.join(DIR_GENERATED_OBS, fn)
                with open(fn,"w", encoding='utf-8') as f:
                    json.dump(d, f, indent=2, ensure_ascii=False)

                print(f"n={n} [{os.path.abspath(fn)}]")
                n += 1
    print("mult_gen finised.")

def JST():
    import datetime
    dt_now = datetime.datetime.now()  # datetime オブジェクト UTC
    jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    #now=jst.strftime("%Y-%m-%d(%a) %H:%M:%S (JST)")
    now=jst.strftime("%Y-%m-%d")
    return now


# --- 定数
pats=["IHE-J-CTN-001",
      "IHE-J-CTN-002",
      "IHE-J-CTN-003",
      "IHE-J-CTN-004",]

stats=["final","preliminary","cancelled"]

days=["2026-04-01T10:10:00+09:00","2026-04-08T10:10:00+09:00",
        "2026-04-15T10:10:00+09:00"]
# --- 定数 END


def read_para(fn):
    pat_para = {}

    HEADER_SKIP = 2
    TITLE_SKIP = 10
    print(f"#176 fn = {os.path.abspath(fn)}")
    with open(fn, "r", encoding="utf-8") as f:

        for _ in range(HEADER_SKIP + TITLE_SKIP):
            next(f)

        while True:
            no = f.readline().strip()
            if no in ("", "=END="):
                break

            values = [f.readline().strip() for _ in range(10)]

            pat_para[no] = {
                "id": values[0],
                "kana": values[1],
                "kanji": values[2],
                "romaji": f"{values[3]} {values[4]}",
                "gender": values[5],
                "birthday": values[6],
                "zip": values[7],
                "address": values[8],
                "tel": values[9],
            }

    return pat_para


def build_patient(para):
    """
    JP Core R4 Patient Resource を生成する
    para : pat_para["1"] など
    """
    gender_map = {
        "M": "male",
        "F": "female",
        "O": "other",
        "U": "unknown"
    }

    patient = {
        "resourceType": "Patient",
        "id": para.get("res_id", f"IHE-J-CTN-{random.randint(100,9999):04}"),
        "meta": {
            "profile": [
                "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Patient"
            ]
        },

        "identifier": [
            {
                #"system": "urn:oid:1.2.392.100495.20.3.51",
                "system": "urn:oid:1.2.392.200036.9169.1.9.20.20",
                "value": para["id"]
            }
        ],

        "name": [

            # 漢字（正式名）
            {
                "use": "official",
                "text": para["kanji"],
                "family": para["kanji"].split("　")[0],
                "given": [para["kanji"].split("　")[1]],
                "extension": [
                    {
                        "url": "http://jpfhir.jp/fhir/core/StructureDefinition/JP_HumanName_Kana",
                        "valueString": para["kana"]
                    }
                ]
            },

            # ローマ字
            {
                "use": "usual",
                "text": para["romaji"],
                "family": para["romaji"].split()[-1],
                "given": [" ".join(para["romaji"].split()[:-1])]
            }
        ],

        "gender": gender_map.get(
            para["gender"],
            "unknown"
        ),

        "birthDate":
            f"{para['birthday'][0:4]}-"
            f"{para['birthday'][4:6]}-"
            f"{para['birthday'][6:8]}",

        "address": [
            {
                "use": "home",
                "postalCode": para["zip"],
                "text": para["address"]
            }
        ],

        "telecom": [
            {
                "system": "phone",
                "value": para["tel"],
                "use": "home"
            }
        ],

        "active": True
    }
    return patient


# ---

if __name__ == "__main__":
    script_path = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(script_path)
    dir = os.path.dirname(script_path)
    os.chdir(dir)
    print(f"script_path: {script_path}\ndir: {dir}")
    
    DIR_GENERATED_OBS = os.path.join(dir, f'GEN_OBS/Obs_{JST()}')
    print(f"DIR_GENERATED_OBS: {DIR_GENERATED_OBS}")
    #stop_proc()
    os.makedirs(DIR_GENERATED_OBS, exist_ok = True)
    
    # for debug
    fn = 'c:\home\github\my-IHE-client\mylib\C.QEDm患者一覧.txt'
    pat_para = read_para(fn)
    for i in range(1,15):
        pat_para[f"{i}"]["res_id"] = f"IHE-J-CTN-{i:03}"
    
    print(f"{json.dumps(pat_para, indent=2, ensure_ascii=False)}")
    
    ### build_patient(_id, para)    
    res = build_patient(pat_para["10"]) 
    print(f"{"="*60}")
    print(f"{json.dumps(res, indent=2, ensure_ascii=False)}")
    