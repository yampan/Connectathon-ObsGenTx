### generate_obs.py
# 2026-04-09
#
# ref: ITI\QEDm\Obs-sample_body-tempture.txt
#               Obs-sample_20種類.txt
#               Obs-sample_value[x].txt
#
# 作成されたOBSは、 ./GEN_OBS/Obs_YYYY-MM-DD/ に保存される。
#      １セット 189個
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


Observation resource を作成する。
1. 参照リソース：
    "Practitioner/jp-practitioner-example-female-1"
    "Patient/xxxx"
    "Specimen/jp-specimen-example-1"
    "Device/ecg-monitor"
    
2. 生成Obs リソース数：
    OBSERVATION(7) x Patient(4) x status(3) x day(3) = 252 個

1. value type
    (1) str 主訴, (valueString)
    (2) codeableConcept コロナ検査, (valueCodeableConcept)
    (3) sampleData ECG, (valueSampledData)
    (4) compornet 血圧  (component.valueQuantity)
    (5) quantigy 体重   (valueQuantity)
    (6) social_history 喫煙歴  (valueQuantity)
    (7) lab_result 尿酸（血清） (valueQuantity) specimenあり
     
2. status
    (1) final
    (2) preliminary
    (3) cancelled
    
3. day （effectivedate）
    (1) 2026-04-01T10:10:00+09:00
    (2) 2026-04-08T10:10:00+09:00
    (3) 2026-04-15T10:10:00+09:00

4. patient
    (1) IHE-J-CTN-001
    (2) IHE-J-CTN-002
    (3) IHE-J-CTN-003
    (4) IHE-J-CTN-004

5. 主訴はランダムに以下の症状
mess = ["軽い頭痛を訴えている",
        "さすような心窩部痛を訴えている",
        "左手にしびれを訴えている",
        "右ひざの痛みを訴えている",
        "下痢を訴えている",
        "強い頭痛を訴えている"]


"""
 

import json
import os, sys
import random

random.seed(123)

# valueString: ex. 主訴
def str_obs(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", _id=None, mess=None):
    # counter
    if not hasattr(str_obs, "N"):
        str_obs.N = 0
    str_obs.N += 1
    
    if mess is None:
        mes = "軽い頭痛を訴えている"
    else:
        i = random.randint(0, 5)
        mes = mess[i]
        print(f"#17 mes = {mes}")
    
    if _id is None:
        _id = f"obs-CC-{str_obs.N:03}"
        
    obs = {
        "resourceType": "Observation",
        "id": _id,
        "meta": {
            "profile": [
            "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_Common"
            ]
        },
        "status": status,
        "category": [
            {
            "coding": [
                {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "exam" ### survey もあり得る。
                },
                {
                "system": "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS", ###
                "code": "exam" ### survey もあり得る。
                }
            ]
            }
        ],
        "code": {
            "coding": [
            {
                "system": "http://loinc.org",
                #"code": "75325-1", ### "Symptom"
                #"code": "75322-8", #### 変更　Complaint
                "code": "8661-1",
                "display": "Chief complaint"
            }
            ],
            "text": "主訴"
        },
        "subject": {
            "reference": pat
        },
        "effectiveDateTime": day,
        "valueString": mes
    }
    return obs

# valueCodeableConcept: ex. COVID-19検査
def vCC_obs(pat="Patient/IHE-01", status="final", 
             day="2026-04-01T10:10:00+09:00", _id=None, mess=None):
    
    # counter
    if not hasattr(vCC_obs, "N"):
        vCC_obs.N = 0
    vCC_obs.N += 1

    if _id is None:
        _id = f"obs-covid-{vCC_obs.N:03}"

    obs = {
    "resourceType": "Observation",
    "id": _id,
    "meta": {
        "profile": [
        "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_Common"
        ]
    },
    "status": status,
    "category": [
        {
        "coding": [
            {
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "laboratory"
            },
            {
            "system": "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS", ###
            "code": "laboratory"
            }
        ]
        }
    ],
    "code": {
        "coding": [
        {
            "system": "http://loinc.org",
            "code": "94500-6",
            "display": "SARS-CoV-2 RNA [Presence] in Respiratory specimen"
        }
        ],
        "text": "COVID-19検査"
    },
    "subject": {
        "reference": pat
    },
    "effectiveDateTime": day,
    "valueCodeableConcept": {
        "coding": [
        {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
            "code": "POS",
            "display": "Positive"
        }
        ],
        "text": "コロナ陽性"
    }
    }
    return obs

# valueSampleData: ex. 心電図
def vSD_obs(pat="Patient/IHE-01", status="final", 
             day="2026-04-01T10:10:00+09:00", _id=None, mess=None):
    global performer, device
    
    # counter
    if not hasattr(vSD_obs, "N"):
        vSD_obs.N = 0
    vSD_obs.N += 1

    if _id is None:
        _id = f"obs-ecg-{vSD_obs.N:03}"

    obs = {
        "resourceType": "Observation",
        "id": _id,
        "meta": {
            "profile": [
            "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_Common"
            ]
        },
        "status": status,
        "category": [
            {
            "coding": [
                {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "procedure"
                },
                {
                "system": "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS", ####
                "code": "procedure"
                }
            ]
            }
        ],
        "code": {
            "coding": [
            {
                #"system": "http://loinc.org",
                #"code": "131328",
                #"display": "Electrocardiogram"
                
                #"system": "urn:iso:std:iso:11073:10101", #### IEEE 11073-MDC（Medical Device Communication）
                "system": "urn:oid:2.16.840.1.113883.6.24",
                "code": "131328",
                "display": "Cardio-vascular device attachment"
            }
            ],
            "text": "心電図"
        },
        "subject": {
            "reference": pat
        },
        "effectiveDateTime": day,

        "performer": [
            {
            "reference": f"Practitioner/{performer}",
            "display": "山田 ＊＊"
            }
        ],
        "device": {
            "display": "12 lead EKG Device Metric",
            "reference": f"Device/{device}",
        },
        "component": [
            {
            "code": {
                "coding": [
                {
                    "system": "urn:oid:2.16.840.1.113883.6.24",
                    "code": "131329",
                    "display": "MDC_ECG_ELEC_POTL_I"
                }
                ]
            },
            "valueSampledData": {
                "origin": {
                "value": 2048
                },
                "period": 10,
                "factor": 1.612,
                "lowerLimit": -3300,
                "upperLimit": 3300,
                "dimensions": 1,
                "data": "2041 2043 2037 2047 2060 2062 2051 2023 2014 2027 2034 2033 2040 2047 2047 2053 2058 2064 2059 2063 2061 2052 2053 2038 1966 1885 1884 2009 2129 2166 2137 2102 2086 2077 2067 2067 2060 2059 2062 2062 2060 2057 2045 2047 2057 2054 2042 2029 2027 2018 2007 1995 2001 2012 2024 2039 2068 2092 2111 2125 2131 2148 2137 2138 2128 2128 2115 2099 2097 2096 2101 2101 2091 2073 2076 2077 2084 2081 2088 2092 2070 2069 2074 2077 2075 2068 2064 2060 2062 2074 2075 2074 2075 2063 2058 2058 2064 2064 2070 2074 2067 2060 2062 2063 2061 2059 2048 2052 2049 2048 2051 2059 2059 2066 2077 2073"
            }
            },
            {
            "code": {
                "coding": [
                {
                    "system": "urn:oid:2.16.840.1.113883.6.24",
                    "code": "131330",
                    "display": "MDC_ECG_ELEC_POTL_II"
                }
                ]
            },
            "valueSampledData": {
                "origin": {
                "value": 2048
                },
                "period": 10,
                "factor": 1.612,
                "lowerLimit": -3300,
                "upperLimit": 3300,
                "dimensions": 1,
                "data": "2041 2043 2037 2047 2060 2062 2051 2023 2014 2027 2034 2033 2040 2047 2047 2053 2058 2064 2059 2063 2061 2052 2053 2038 1966 1885 1884 2009 2129 2166 2137 2102 2086 2077 2067 2067 2060 2059 2062 2062 2060 2057 2045 2047 2057 2054 2042 2029 2027 2018 2007 1995 2001 2012 2024 2039 2068 2092 2111 2125 2131 2148 2137 2138 2128 2128 2115 2099 2097 2096 2101 2101 2091 2073 2076 2077 2084 2081 2088 2092 2070 2069 2074 2077 2075 2068 2064 2060 2062 2074 2075 2074 2075 2063 2058 2058 2064 2064 2070 2074 2067 2060 2062 2063 2061 2059 2048 2052 2049 2048 2051 2059 2059 2066 2077 2073"
            }
            },
            {
            "code": {
                "coding": [
                {
                    "system": "urn:oid:2.16.840.1.113883.6.24",
                    "code": "131389",
                    "display": "MDC_ECG_ELEC_POTL_III"
                }
                ]
            },
            "valueSampledData": {
                "origin": {
                "value": 2048
                },
                "period": 10,
                "factor": 1.612,
                "lowerLimit": -3300,
                "upperLimit": 3300,
                "dimensions": 1,
                "data": "2041 2043 2037 2047 2060 2062 2051 2023 2014 2027 2034 2033 2040 2047 2047 2053 2058 2064 2059 2063 2061 2052 2053 2038 1966 1885 1884 2009 2129 2166 2137 2102 2086 2077 2067 2067 2060 2059 2062 2062 2060 2057 2045 2047 2057 2054 2042 2029 2027 2018 2007 1995 2001 2012 2024 2039 2068 2092 2111 2125 2131 2148 2137 2138 2128 2128 2115 2099 2097 2096 2101 2101 2091 2073 2076 2077 2084 2081 2088 2092 2070 2069 2074 2077 2075 2068 2064 2060 2062 2074 2075 2074 2075 2063 2058 2058 2064 2064 2070 2074 2067 2060 2062 2063 2061 2059 2048 2052 2049 2048 2051 2059 2059 2066 2077 2073"
            }
            }
        ]

    }
    return obs



# valueQuantity+compornent: ex. 血圧（収縮期、拡張期）
def blood_presure(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", _id=None, 
            v_sys=None, v_dia=None, mess=None):

    # counter
    if not hasattr(blood_presure, "N"):
        blood_presure.N = 0
    blood_presure.N += 1

    if _id is None:
        _id = f"obs-bp-{blood_presure.N:03}"

    if v_sys is None or v_dia is None:
        v_sys = random.randint(100, 150)
        v_dia = random.randint(50, 95)
        
    obs = {
        "resourceType": "Observation",
        "id": _id,
        "meta": {
            "profile": [
            #"http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_Common"
            "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_VitalSigns" ###
            "http://hl7.org/fhir/StructureDefinition/vitalsigns" # 併記
            ]
        },
        "status": status,
        "category": [
            {
            "coding": [
                {
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs"
                },
                {
                "system": "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS",
                "code": "vital-signs"
                }
            ]
            }
        ],
        "code": {
            "coding": [
            {
                "system": "http://loinc.org",
                "code": "85354-9",
                "display": "Blood pressure panel with all children optional"
            }
            ],
            "text": "血圧（Blood pressure）"
        },
        "subject": {
            "reference": pat
        },
        "effectiveDateTime": day,
        "component": [
            {
            "code": {
                "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure"
                }
                ],
                "text": "収縮期血圧"
            },
            "valueQuantity": {
                "value": v_sys,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            }
            },
            {
            "code": {
                "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8462-4",
                    "display": "Diastolic blood pressure"
                }
                ],
                "text": "拡張期血圧"
            },
            "valueQuantity": {
                "value": v_dia,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            }
            }
        ]
    }   
    return obs


# valueQuantity: ex. 体重
def quant_obs(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", 
            _id=None, v=None, mess=None):
    
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
            #"http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_Common"
            #"http://hl7.org/fhir/StructureDefinition/vitalsigns"　# 併記すべきか？
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

# 喫煙歴
def social_history(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", _id=None, v=None, mess=None):
    # counter
    if not hasattr(social_history, "N"):
        social_history.N = 0
    social_history.N += 1
    
    if v is None:
        year = random.randint(30, 50)
        hon = random.randint(10, 30)
    else:
        year, hon = v
                
    if _id is None:
        _id = f"jp-observation-socialhistory-example-{social_history.N:03}"
    
    return {
        "resourceType" : "Observation",
        "id" : _id,
        "meta" : {
            "profile" : [
            "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_SocialHistory"
            ]
        },
        "status" : status,
        "category" : [
            {
            "coding" : [
                {
                "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS",
                "code" : "social-history",
                "display" : "Social History"
                }
            ]
            }
        ],
        "code" : {
            "coding" : [
            {
                "system" : "http://abc-hospital.local/fhir/Observation/localcode",
                "code" : "abc-local-456",
                "display" : "ブリンクマン指数"
            },
            {
                "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_ObservationSocialHistoryCode_CS",
                "code" : "MD0012920",
                "display" : "喫煙指数"
            }
            ]
        },
        "subject" : {
            "reference" : pat
        },
        "effectiveDateTime" : day,
        "valueQuantity" : {
            "value" : year*hon
        },
        "component" : [
            {
            "code" : {
                "coding" : [
                {
                    "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_ObservationSocialHistoryCode_CS",
                    "code" : "MD0012910",
                    "display" : "通算喫煙年数"
                }
                ],
                "text" : "通算喫煙年数"
            },
            "valueQuantity" : {
                "value" : year,
                "unit" : "年"
            }
            },
            {
            "code" : {
                "coding" : [
                {
                    "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_ObservationSocialHistoryCode_CS",
                    "code" : "MD0012900",
                    "display" : "１日の喫煙本数"
                }
                ],
                "text" : "１日の喫煙本数"
            },
            "valueQuantity" : {
                "value" : hon,
                "unit" : "本"
            }
            }
        ]
    }

# 尿酸
def lab_result(pat="Patient/IHE-01", status="final", 
            day="2026-04-01T10:10:00+09:00", _id=None, v=None, mess=None):
    global performer, specimen
    
    # counter
    if not hasattr(lab_result, "N"):
        lab_result.N = 0
    lab_result.N += 1
    
    if _id is None:
        _id = f"jp-observation-labresult-example-{lab_result.N:03}"
    
    if v is None:
        v = 7 + random.randint(1,30)/10
    
    return {
    "resourceType" : "Observation",
    "id" : _id,
    "meta" : {
        "profile" : ["http://jpfhir.jp/fhir/core/StructureDefinition/JP_Observation_LabResult"]
    },
    "status" : "final",
    "category" : [{
        "coding" : [{
        "system" : "http://jpfhir.jp/fhir/core/CodeSystem/JP_SimpleObservationCategory_CS",
        "code" : "laboratory"
        }]
    }],
    "code" : {
        "coding" : [{
        "system" : "http://abc-hospital.local/fhir/Observation/localcode",
        "code" : "05104",
        "display" : "尿酸"
        },
        {
        "system" : "urn:oid:1.2.392.200119.4.504",
        "code" : "3C020000002327101"
        }],
        "text" : "尿酸"
    },
    "subject" : {
        "reference" : pat
    },
    "effectiveDateTime" : day,
    "performer" : [{
        "reference": f"Practitioner/{performer}"
    }],
    "valueQuantity" : {
        "value" : v,
        "unit" : "mg/dL"
    },
    "interpretation" : [{
        "coding" : [{
        "system" : "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "code" : "H",
        "display" : "High"
        }],
        "text" : "H"
    }],
    "specimen" : {
        "reference": f"Specimen/{specimen}"
    },
    "referenceRange" : [{
        "low" : {
        "value" : 2.1
        },
        "high" : {
        "value" : 7
        },
        "type" : {
        "coding" : [{
            "system" : "http://terminology.hl7.org/CodeSystem/referencerange-meaning",
            "code" : "normal",
            "display" : "Normal Range"
        }]
        }
    }]
    }
    

### -----------------------------------------------------------

# 複数のObservationを生成する。
def multi_gen(func, name, pats, stats, days, mess,
              DIR_GENERATED_OBS):
    global total, performer, specimen, device
    
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
    print(f"#706 performer = {performer}, specimen = {specimen}, device = {device}")
    n=1
    for np, pat in enumerate(pats, start=1):
        pat = f"Patient/{pat}"
        for status in stats:
            for nd, day in enumerate(days, start=1):
                mark = f"P{np}{status[0:2]}D{nd}"
                d = func(pat, status, day=day, mess=mess)
                #print(json.dumps(d, indent=2, ensure_ascii=False))
                fn = f"obs_{name}_{n:02}_{mark}.json"
                fn = os.path.join(DIR_GENERATED_OBS, fn)
                with open(fn,"w", encoding='utf-8') as f:
                    json.dump(d, f, indent=2, ensure_ascii=False)

                print(f"n={n} [{os.path.abspath(fn)}]")
                n += 1
                total += 1
    print(f"mult_gen finised. n = {n}")

def JST():
    import datetime
    dt_now = datetime.datetime.now()  # datetime オブジェクト UTC
    jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    #now=jst.strftime("%Y-%m-%d(%a) %H:%M:%S (JST)")
    now=jst.strftime("%Y-%m-%d")
    return now


def gen_obs_main(pats, stats, days, mess, values, win=None):
    global total, performer, specimen, device
    
    performer = values.get("-pract-").split()[0]
    specimen = values.get("-speci-").split()[0]
    device = values.get("-device-").split()[0]
    
    # #pats=["IHE1","IHE2","IHE3"]
    script_path = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(script_path)
    dir = os.path.dirname(script_path)
    os.chdir(dir)
    print(f"script_path: {script_path}\ndir: {dir}")
    
    DIR_GENERATED_OBS = os.path.join(dir, f'GEN_OBS/Obs_{JST()}')
    print(f"DIR_GENERATED_OBS: {DIR_GENERATED_OBS}")
    #stop_proc()
    os.makedirs(DIR_GENERATED_OBS, exist_ok = True)
    
    total = 0
    
    # for debug
    if 0:
        pats=pats[:1]
        stats=stats[:1]    
        days=days[:1]

    funcs = [(vCC_obs, "C19"), (str_obs, "CCT"), (vSD_obs, "ECG"),
                     (blood_presure, "BPR"), (quant_obs, "BWT"),
                     (social_history, "SOH"), (lab_result, "URE")]
    
    for (func,name) in funcs[:]:
        
        multi_gen(func, name, pats, stats, days, mess, DIR_GENERATED_OBS)
        pass
    
    return DIR_GENERATED_OBS, total

# --- 定数
pats=[ "IHE-J-CTN-001", "IHE-J-CTN-002", "IHE-J-CTN-003",
        "IHE-J-CTN-004"]

stats=["final","preliminary","cancelled"]

days=["2026-04-01T10:10:00+09:00","2026-04-08T10:10:00+09:00",
        "2026-04-15T10:10:00+09:00"]

mess = ["軽い頭痛を訴えている",
        "さすような心窩部痛を訴えている",
        "左手にしびれを訴えている",
        "右ひざの痛みを訴えている",
        "下痢を訴えている",
        "強い頭痛を訴えている"]
# ---

    
if __name__ == '__main__':
    gen_obs_main(pats, stats, days, mess)
    