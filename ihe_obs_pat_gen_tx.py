# -*- coding: utf-8 -*-

### uv 環境
# uv init [project]
# cd [project]
# uv python pin 3.1x
# uv add [library]
# uv sync
# 仮想環境に入る。  .venv\Scripts\Activate.bat (ps1)
# uv run (python) aaa.py 
# VS-code内：　ctrl+shft+P (.venv/python.exe)を選択
#             ctrl+@  terminal で ([project 名]) が表示される。

### 2026-06-24
r"""
###  FHIR Serverの設定により、Observationを Uploadする。


〇GUIは、IHE-IPS-gui3.py を元に作成する。
+ lay_info サーバーのURL、機能：PUT,POST を決める。
+ lay_patient サーバー上のリソースIDを指定する。
    (1) Patient, (2)Performer, (3)
    "reference": "Practitioner/jp-practitioner-example-male-1",
    "reference": "Device/ecg-monitor"
    "reference": "Specimen/jp-specimen-example-1"
+ lay_address
+ lay_command (1)Create, (2)Tx

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

【例】  PUT /Patient/1001
HTTP/1.1 405 Method Not Allowed
Content-Type: application/fhir+json

{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "not-supported",
      "diagnostics": "Update operation is not supported."
    }
  ]
}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
HTTP/1.1 403 Forbidden  になる実装もあります。

{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "forbidden",
      "diagnostics": "Update on Patient is not permitted."
    }
  ]
}

ケース3：Patient/1001 が存在しない
Updateが許可されている場合には、

404 Not Found
  or
201 Created

FHIRではPUTは Update-as-Create をサポートしているサーバもあるためです。

{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity":"error",
      "code":"processing",
      "diagnostics":"HTTP 405 Method Not Allowed"
    }
  ]
}

〇 CapabilityStatementとの関係

Updateを禁止するのであれば、サーバの CapabilityStatement (GET /metadata) においても、

<resource>
    <type value="Patient"/>
    <interaction>
        <code value="read"/>
    </interaction>
    <interaction>
        <code value="search-type"/>
    </interaction>
    <interaction>
        <code value="create"/>
    </interaction>
</resource>

IHE のプロファイルでも、サーバがサポートしないFHIR操作に対しては、

HTTP 405 Method Not Allowed
OperationOutcomeを返す

"""


### 2026-03-06
# Observation 生成
# Patient: Patient-25-IHE1, Patient-24-sakaeda
# Obs: obs-4-respiratory-rate
#      obs-25-body-weight
#      obs-17-BMI
#      osb-44-body-temp
# date: 2026-03-03, 2026-04-04, 2026-05-05


### 変数名の方針
# layout: lay_xxx
# wedget: key="-(略語)-"
# Button 処理関数： if event == '(Button名)'
#                        Button名の関数で処理する。
# 変数名：重要な変数は省略しない。
#         例：Patient, Observation


### IHE-Obs-gui3.py from IHE-SVCM-gui3.py 2026-01-15
### MS VS-Code Himt
# 1. ターミナルを開く  ctrl + @, clear: cls,  Ctrl+Shift+P
# 2. GitHUB commitの方法
# 3. module のSub-folder を mylib に変更。2025-02-21
# 4. main へ subscribe する。
# 5. Branch logfunc を追加する。
# 6. acubic-PE Document\my-IHE-client に local repositoryを作成
#    PRO4: document\GitHub\
#　------------------------------------------------------------
r"""
  > uv --version
  uv 0.9.24 (0fda1525e 2026-01-09)
  
  使い方
  uv self update --> v0.9.26
  
  uv python install 3.13   --- 3.13.11
  
  〇project の作り方
    mkdir xxx
    cd xxx
    uv init --python 3.13
    uv python pin 3.13
    
    .python-version
    main.py
    pyproject.toml
    README.md
    .gitignore   (自分で作成し、内容は、 .venv/ )
    
  2. project 実行

    > uv run main.py
      uv run --python 3.10 hello.py
      
    vs code を使う場合。
    > code .
    
    (1) 環境の選択：main.py を開いて、
    画面右下の 「Python 3.x.x」 と表示されている部分をクリック
    リストの中から 「Python 3.13.x ('.venv': uv)」を選択
    
    (2) プログラムの編集
    
    (3) 実行：
         1. [三角] アイコン
         2. ctrl + @ でターミナルを開き、uv run main.py
    
    (4) ライブラリを追加
        ターミナル： uv add requests
                     uv add TkEasyGUI FreeSimpleGUI
    
          uv pip install -r requirements.txt

=============================================================================
<<< IHE-Obs-JP-Gen.py >>>

Closed Issues:
    1) Patient Resouorce の読み込み。
    2) Template-Observation resource の読み込み
    3) 各値：
           EffectiveDateTime
           Status
           Value
           Subject (Patient resourceの選択)
    4) 新しい Observation resource の生成・保存
           Directory: ./log/Observation- ... .json
    5) HELP表示 from wyWin import myPop()
    6) vType: valueString,
    7) 生成OBS_DIR： DIR_GENERATED_OBS = 'GEN_OBS/Obs_[today]'
    8) Observation 生成には、mylib.generate_obs main() を使用
    
    
Open Issues:
    1) Valueの値によっては、生成不能となる。

      
    
ref: get_clipboard(), set_clipboard(), screenshot(),
     load_json_file(fn), save_json_file(fn, dat)




OPTION:
(1) Status: final, preliminary, amended 改訂版, corrected 訂正済み, 
    cancelled 取消し, entered-in-error 誤入力
(2) Effective:
(3) value:
(4) Subject:
(5) Cotegory:
(6) code:

"""
import requests
from typing import Optional
import TkEasyGUI as eg
import json, os, sys, datetime, random
#import pytz
from mylib.readWriteXL import (openXl, getRow, setRow, search3, JST, createLogWs,
                               j_map, trans2, logHeaderSet, JSTfn, trans )
#from mylib.db_access import query, DBtrans, db_init
from mylib.logger import (FMT, FMT2, createLogger, 
            clearLogfile, log_init, get_file_info)
import glob
from mylib.version_info2 import help_window, startFile
#from mylib.daycheck import dayCheckM, pred
#from mylib.queryRepo import (marital_status_get, name_use_get, create_patRes,
#                             marital_change, gender_get, fQuery )
#from mylib.postRes import postRes
from mylib.http_code import HTTP2S

from mylib.generate_pat import build_patient, read_para
from mylib.generate_obs import gen_obs_main, stats, days, mess

import socket, platform
from mylib.get_item import wrapGet, get_item, dotItem2
import traceback
import subprocess
from mylib.hostname_os import get_hostname, get_os, get_env

env = get_env()

if get_hostname() == "X1Pro" and get_os() == "Windows":
    #cwd = 'c:/home/github/my-IHE-client'
    cwd = env["script_dir"]
    print(f"   os.chdir = {os.chdir(cwd)}")
    print(f"   os.getcwd() = {os.getcwd()}")

# ---
DIR_GENERATED_OBS = f'GEN_OBS\\Obs_{JST()[:10]}'
os.makedirs(DIR_GENERATED_OBS, exist_ok=True)

PAT_ID = f"{random.randint(10000, 99999)}"
WEB_SITE = "https://cloud-gazelle-ihej.net/"
VERSION = 'Ver. 1.0 YA'

# logger start
os.makedirs("./log", exist_ok=True)
LOG_FN = "LOG_OBS-TX.TXT"


logger = log_init(LOG_FN, backupCount=10)
get_file_info(".", "LOG*", show=1)

"""
script_path = os.path.abspath(sys.argv[0])
script_name = os.path.basename(script_path)
logger.debug(f"=== Start: {script_name} ===")
logger.debug(f"スクリプトのパス: {script_path}")
logger.debug(f"スクリプト名: {script_name}")
"""


    
fn_conf = "OBS-TX_conf.json"
print(f"fn_conf = {os.path.abspath(fn_conf)}")
if os.path.isfile(fn_conf):
    with open(fn_conf, "r", encoding='utf-8-sig') as f:
        conf_dic = json.load(f)
else:
    print(f"{fn_conf} not found. Default value enable.")
    conf_dic = {
          "version": "V0.9",
            "day": "2026-01-19 21:14:37 (JST)",
            "f_size": 12,
            "sel_font": "BIZ UDPゴシック",
            "ResSvr_URL": "http://192.168.16.206:8080/fhir",
            "TermRepo_URL": "null"
    }
TermRepo_URL = conf_dic.get("TermRepo_URL", "")
ResSvr_URL = conf_dic.get("ResSvr_URL", "")

# font
f_size = conf_dic.get("f_size", 12)
sel_font = conf_dic.get("sel_font","BIZ UDPゴシック")

status_list = ["final 最終", "registered 登録済み", "preliminary 暫定",
    "amended 改訂版", "corrected 訂正済み", "cancelled 取消し",
    "entered-in-error 誤入力", "unknown 不明"]

gender_list = [""]
value_analysis = {"Program": "IHE-Obs-gui3.py"}

# 定数　ーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
# FONT 定数
F11 = ("BIZ UDPゴシック", 11, "bold")
F12 = ("BIZ UDPゴシック", 12, "bold")

FA10 = ("Arial", 10, )
FA10B = ("Arial", 10, "bold")
FA10BI = ("Arial", 10, "bold italic")

FA11 = ("Arial", 11, )
FA11B = ("Arial", 11, "bold")
FA11BI = ("Arial",11,'bold italic')

FA12 = ("Arial", 12, )
FA12B = ("Arial", 12, "bold")
FA12BI = ("Arial", 12, "bold italic")

FA13 = ("Arial", 13, )
FA13B = ("Arial", 13, "bold")
FA13BI = ("Arial", 13, "bold italic")

b_color="#FEE0B3" # button bg_color
# test data
PTR=10
fns=["aaa", "bbb", "ccc"]
pat_list = ["#newborn", "Patient/infant", "Patient/example", "Patient/f001",
          "null", "Patient/f201", "Patient/ch-example", "Patient/pat2",
          "unknown", ]

# 定数 END　ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

#!/usr/bin/env python3
"""
CapabilityStatement から各リソースの CREATE / UPDATE サポートを表示する
"""

import requests

FHIR_SERVER = "http://192.168.16.206:8080/fhir"

TARGET_RESOURCES = [
    "Patient",
    "Device",
    "Observation",
    "Practitioner",
    "Specimen",
]


def get_capability_statement(server):
    url = server.rstrip("/") + "/metadata"

    r = requests.get(
        url,
        headers={"Accept": "application/fhir+json"},
        timeout=30,
    )
    r.raise_for_status()

    return r.json()


def get_interactions(capability, resource_name):
    """
    指定リソースの interaction(code) の一覧を返す
    """

    for rest in capability.get("rest", []):

        for resource in rest.get("resource", []):

            if resource["type"] == resource_name:

                return {
                    x["code"]
                    for x in resource.get("interaction", [])
                }

    return set()


def check_server(FHIR_SERVER: str, win=None): 
    capability = get_capability_statement(FHIR_SERVER)

    print(f"FHIR Server : {FHIR_SERVER}")
    print()
    print(f"{'Resource':15} {'Create':8} {'Update':8}")
    print("-" * 35)

    if win:
        win["-body-"].print(f"\n   FHIR Server : {FHIR_SERVER}")
        win["-body-"].print(f"   <<< capability >>>")
        win["-body-"].print("-" * 35,)
        win["-body-"].print(f" {'Resource':14} {'Create':8} {'Update':8}")
        win["-body-"].print("-" * 35,)
        
    for resource in TARGET_RESOURCES:
        interactions = get_interactions(capability, resource)
        create = "Yes" if "create" in interactions else "No"
        update = "Yes" if "update" in interactions else "No"

        print(f"{resource:15} {create:8} {update:8}")
        if win:
            win["-body-"].print(f" {resource:15} {create:8} {update:8}")



####################### Layout 作成 ######################################
# MAIN: lay_main
# Information: lay_info
# patient: lay_pat
# Observation: lay_obs
# save: lay_save
# control area: lay_cont
####################### Layout 作成 ######################################
from pathlib import Path
from typing import List
import re

pattern = re.compile(r"Observation-(\d+)-")

def gen_list(dir: str, filter: str) -> List[str]:
    """ 
    dir 内の filter にマッチするファイルを、
    ファイル名のみ抽出し、Observation-<番号>-... の番号順にソートして返す。
    """
    p = Path(dir)
    # ファイル一覧取得
    files = list(p.glob(filter))
    # ファイル名だけに変換
    names = [f.name for f in files]
    # ソート（Observation-<num>- をキーに）
    def sort_key(name: str):
        m = pattern.search(name)
        if m:
            return int(m.group(1))
        return float("inf")  # マッチしないものは後ろへ
    return sorted(names, key=sort_key)
    
pattern_pat = re.compile(r"Patient-(\d+)-")

def gen_pat_list(dir: str, filter: str) -> List[str]:
    """
    dir 内の filter にマッチするファイルを、
    ファイル名からIDのみ抽出し、ID順にソートして返す。
    """
    p = Path(dir)
    # ファイル一覧取得
    files = list(p.glob(filter))
    # ファイル名だけに変換
    names = [f.name for f in files]
    # ソート（Observation-<num>- をキーに）
    def sort_key(name: str):
        m = pattern_pat.search(name)
        if m:
            return int(m.group(1))
        return float("inf")  # マッチしないものは後ろへ
    return sorted(names, key=sort_key)


def lay_svr():
    global fns
    # font=("arial", 10,'bold')
    svr_color="#B8DFF1"
    layout = [
        [eg.Text("FHIR server:",background_color=svr_color),
         eg.Input(ResSvr_URL, key="-server-", 
                  font=FA11B, width=40),
         eg.Button("check_server", background_color=b_color),],
        [eg.Text(f"Output directory: '{DIR_GENERATED_OBS}'", 
                 font=FA11BI, background_color=svr_color),
         eg.Text("    ", background_color=svr_color),
         eg.Button("OBS-DIR", font=FA11BI)]
    ]
    return eg.Frame("resSvr", layout=layout, expand_x=True, color="blue",
              key="-info-", background_color=svr_color,
              font=("arial", 11, "bold italic"))

def lay_info():
    global fns
    # font=("arial", 10,'bold')
    layout = [
        [eg.Text("Practioner :"),
         eg.Input("jp-practitioner-example-female-1", key="-pract-", 
                  font=FA11B,width=40),
         eg.Button("test(2)", background_color=b_color),],
        [eg.Text("Device 　　　:"),
         eg.Input("ecg-monitor", key="-device-", font=FA11B, 
                  width=40, ),
         eg.Button("test(3)", background_color=b_color)],
        [eg.Text("Specimen  :"),
         eg.Input("jp-specimen-example-1", 
                  key="-speci-", font=FA11B, width=40, ),
         eg.Button("test(4)", background_color=b_color),
         eg.Text(" ", expand_x=True, background_color="#BCE2D0"),
         eg.Button("HELP", font=FA10B, color="green",background_color="lightyellow"),
         #eg.Text(" ", ), 
         eg.Button("clear", font=FA10B,color="brown",background_color="lightyellow"),
         ]
        ]
    return eg.Frame("Information", layout=layout, expand_x=True, color="blue",
              key="-info-", background_color="#BCE2D0",
              font=("arial", 11, "bold italic"))

   


def lay_pat(): 
    button_bg="#EFB6A7"
    layout = [
    [eg.Button("Method(0)", key="Method(0)",
               background_color=b_color),
     eg.Text(" ==> "), 
     eg.Combo(["PUT (update)","POST (create)"], key="-method-", readonly=True,
                font=F11, width=15, enable_events=True,
                default_value='PUT (update)'  ),
     eg.Button("Set", key="Set",
               background_color=b_color)],
    [eg.Text("Patient 1:", ), 
     eg.Input("IHE-J-CTN-001", width=30, key="-pat1-"),
     eg.Button("Tx(1)", background_color=b_color),
     eg.Text(" ",background_color="#F1C8F0",),
     eg.Checkbox("On", default=True, background_color="#F1C8F0",
                 key="pat1-on")],
    [eg.Text("Patient 2:", ), 
     eg.Input("IHE-J-CTN-002", width=30, key="-pat2-"),
     eg.Button("Tx(2)", background_color=b_color),
     eg.Text(" ", background_color="#F1C8F0",),
     eg.Checkbox("On", default=True, background_color="#F1C8F0",
                 key="pat2-on")],
    [eg.Text("Patient 3:", ), 
     eg.Input("IHE-J-CTN-003", width=30, key="-pat3-"),
     eg.Button("Tx(3)", background_color=b_color),
     eg.Text(" ",background_color="#F1C8F0",),
     eg.Checkbox("On", default=True, background_color="#F1C8F0",
                 key="pat3-on")],
    [eg.Text("Patient 4:", ), 
     eg.Input("IHE-J-CTN-004", width=30, key="-pat4-"),
     eg.Button("Tx(4)", background_color=b_color),
     eg.Text(" ",background_color="#F1C8F0",),
     eg.Checkbox("On", default=True, background_color="#F1C8F0",
                 key="pat4-on")],
    ]
    return eg.Frame("Patient", layout=layout, expand_x=True, color="blue",
              background_color="#F1C8F0",
              font=("arial", 11, "bold italic"))


    

# Main layout
def lay_cont():
    bg_color="#DBE8FC"
    layout = [
    [eg.Button("GenObs",color="#7B147C",background_color="lightyellow",font=FA12B),
     #eg.Text(" "),
     eg.Button("Transfer",color="#7B147C",background_color="lightyellow"
               ,font=FA12B),
     eg.Text(" "),
     eg.Button("Save-Conf", color="#2222A0",background_color="lightyellow",font=FA12B),
     #eg.Text(" "),
     eg.Button("Exit", color="#FF2222",background_color="lightyellow",font=FA12B),
     eg.Text(" "),
     eg.Button("Gazelle-Web", color="#2222A0",background_color="lightyellow",
               font=FA10B), #eg.Text(" "),
     eg.Button("LOG", color="#165A62",background_color="lightyellow",
               font=FA10B), #eg.Text(" "),
     eg.Button("LOG-DIR", color="#165A62",background_color="lightyellow",
               font=FA10B),eg.Text(""),
     eg.Button("test", font=FA10B),
     ],
    
    [eg.Multiline(text="message:\n", size=(40, 16), key="-body-",
            #font=("メイリオ", 11, "bold"), 
            font=("BIZ UDゴシック", 11, "bold"),
            #font=("Cascadia Mono SemiBold", 11, "bold"),
            expand_y=True, expand_x=True, autoscroll=True)],
    [eg.Text("2025-03-28 18:17:45 (JST)", key="-now-", font=FA10BI),
     eg.Text(f'', expand_x=True), 
     eg.Text(f"Observation Transfer Project: {VERSION}  ", font=FA10BI) ]
    ]
    return eg.Frame("Control", layout=layout, expand_x=True)
    
    
def selection_check(val, key, item, win):
    print(f"selection_check: {val[key]}")
    val = val[key]
    if "実行" in val or "選択" in val:
        win["-body-"].print(f"Selection error: [{item}]   {val}",
                            text_color="red")
        win[f"-{item}-"].update(color="red")
        return "NG"
    else:
        win[f"-{item}-"].update(color="green")
        return "OK"



def extEnt(bund: dict, win):
    ents = wrapGet(bund, ["entry"])
    fnames = []
    total = wrapGet(bund, ["total"])
    if type(total) is str and "null" in total:
        win['-body-'].print(f"   extEnt: #669 total not found.", text_color="red")
        return []
    for n in range(int(total)):
        ent = ents[n]
        family = wrapGet(ent, ["resource","name","family"])
        given = wrapGet(ent,["resource","name","given"])
        fnames.append((family, given))
    #print(f"#678 fnames= {fnames}")
    return fnames 

def getPatList(val, win, count):
    url = val['-ResSvr-']  # 'http://192.168.16.206:8080/fhir']
    url += f'/Patient?_count={count}'
    print(f"#672 url= {url}, type= {type(url)}")
    win['-body-'].print(f"\n   List patient   url= {url}", text_color="blue")
    _ids, res = fQuery(url) # fhir-query
    
    # res.json() から、family name を抽出
    fnames = extEnt(res.json(), win)
    if fnames == []:
        return
    win["-body-"].print(f"   === Patient List ===")
    for n, (_id, (fnam, given)) in enumerate(zip(_ids,fnames),  start=1):
        win['-body-'].print(f"   {n:3}) {_id} - {fnam} - {given}")
        #if n>=10: break
    return


from  mylib.myWin import myPop
# ---            
mes_manual = "\n〇使い方 (IHE-Obs&Pat-Gen-Tx.py)\n" + \
    "1. FHIR server欄に Base-URLをセットする。\n"  + \
    "2. [check_server] ボタンをクリック。Put機能を調べて、\n" + \
    "3. Method：PUT/POST を選択し、[Set]を押す。\n" + \
    "4. Patient (1から4), Practioner, Device, Specimen\n" + \
    "   を押して、resource_id がセットされる。\n" + \
    "5. Patient の Check-boxで使用する患者を選択する。\n" + \
    "   （IHE-J-CTN-001 から 015まで使用可能。）\n" + \
    "6. Control 欄で、[GenObs]で Observation が生成。\n"+ \
    "7. [Transfer]で作成したリソースを転送（PUT/POST) \n" + \
    "   する。\n"+\
    "8. 設定を保存するには、[Save-Conf]ボタンを使用。\n\n"

def put_resource(win, event, _id, RESOURCE, RES, url, key):
    """
    作成したリソースをサーバーへ（PUT, POST)して、結果のリソースを保存する。
    Args:
        win (eg.window): _description_
        event (str): _description_
        _id (str): _description_
        RESOURCE (dict): resource
        RES (str): ressource type
        url (str): FHIR server [BaseURL]
        key (str): 設定する eg.Input の key

    Returns:
        http_code (int): 転送結果のHTTP CODE
        resource_id: 作成されたリソースID
    """
    #_id = "jp-practitioner-example-male-1"
    #RESOURCE = build_practitioner(_id)
    mes = json.dumps(RESOURCE, indent=2, ensure_ascii=False)[:100]+ \
        " ...(trimmed.)"
    win["-body-"].print(f"{RES}: {mes}")
    method = "PUT" if values["-method-"].split()[0].upper() == "PUT" else "POST"
    win["-body-"].print(f"method: {method}")
    
    http_code, resource_id = tx_put(win, RES, method, url,
                        RESOURCE,  _id)
    
    win["-body-"].print(f"http_code: {http_code}, resource_id: {resource_id}",
                        text_color="purple")

    # check result
    if resource_id == _id:
        win["-body-"].print(f"resource_id: {resource_id} --- OK",
                            text_color="green")        
        win[key].update(f"{resource_id} --- OK")
    else:
        win[key].update(resource_id)
        win["-body-"].print(f"resource_id: {resource_id} --- Changed",
                            text_color="red") 

    return http_code, resource_id


### dispatcher
def put_test(win, event):
    url = values["-server-"]
    # tx
    print(f"#633 put_test: {event}")
    if event == 'test(2)':
        #put_resource(win, event, _id, RESOURCE, RES, url):
        key = "-pract-"
        _id = values[key].split()[0]
        RESOURCE = build_practitioner(_id)
        #win["-body-"].print(f"Practioner: {RESOURCE}")
        RES = "Practitioner"
        put_resource(win, event, _id, RESOURCE, RES, url, key)
       
    elif event == "test(3)":# Device
        key = '-device-'
        _id = values[key].split()[0]
        RESOURCE = build_device(_id)
        RES = "Device"
        win["-body-"].print(f"{RES}: {RESOURCE}")
        put_resource(win, event, _id, RESOURCE, RES, url, key)
        
    elif event == "test(4)": # Specimen
        key = '-speci-'
        _id = values[key].split()[0]
        RESOURCE = build_specimen(_id)
        RES = "Specimen"
        put_resource(win, event, _id, RESOURCE, RES, url, key)
    
    elif event in ["Tx(1)", "Tx(2)", "Tx(3)", "Tx(4)"]:
        n = event[3:4]
        logger.debug(f"n = {n}")
        key = f"-pat{n}-"
        _id = values[key]
        RESOURCE = build_patient(pat_para[n])
        logger.info(f"pat= {json.dumps(RESOURCE, indent=2, ensure_ascii=False)}")
        RES = "Patient"
        
        put_resource(win, event, _id, RESOURCE, RES, url, key)
        
    else:
        win["-body-"].print(f"put_test ERROR: {event}")
    
    return
    
    
def build_practitioner(resource_id: str) -> dict:
    """
    PUT するための Practitioner リソースを組み立てる。
    id フィールドは URL のリソースIDと一致させる必要がある。
    """
    return {
        "resourceType": "Practitioner",
        "id": resource_id,
        "meta": {
            "profile": [
                "http://hl7.org/fhir/StructureDefinition/Practitioner"
            ]  },
        "active": True,
        "name": [
            {
                "use": "official",
                "family": "山田",
                "given": ["由紀"],
                "prefix": ["Dr."]
            } ],
        "telecom": [
            {
                "system": "phone",
                "value": "03-1234-5678",
                "use": "work"
            },
            {
                "system": "email",
                "value": "yamada.yuuki@hospital.example.jp",
                "use": "work"
            }  ],
        "gender": "male",
        "birthDate": "1975-06-15",
        "qualification": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                            "code": "MD",
                            "display": "Doctor of Medicine"
                        }   ]
                }   }  ]
    }
 

def build_device(resource_id: str) -> dict:
    """
    PUT するための Device リソース（FHIR R4）を組み立てる。
    主要フィールド:
        identifier      - UDI やシリアル番号などの識別子
        udiCarrier      - UDI キャリア情報（バーコード / RFID）
        status          - active | inactive | entered-in-error | unknown
        deviceName      - デバイス名称（udi-label-name / user-friendly-name 等）
        modelNumber     - モデル番号
        type            - デバイス種別（SNOMED CT 等）
        manufacturer    - 製造業者名
        manufactureDate - 製造日
        expirationDate  - 有効期限
        serialNumber    - シリアル番号
        patient         - 紐付く患者（任意）
        owner           - 管理組織（任意）
        location        - 設置場所（任意）
        note            - メモ
 
    Parameters
    ----------
    resource_id : str
        FHIR リソース ID（PUT URL の末尾と一致させること）
 
    Returns
    -------
    dict
        FHIR R4 準拠の Device リソース辞書
    """
    return {
        "resourceType": "Device",
        "id": resource_id,
        "meta": {
            "profile": [
                "http://hl7.org/fhir/StructureDefinition/Device"
            ]   },
        # ── インスタンス識別子（シリアル番号など） ─────────────────────
        "identifier": [
            {
                "system": "http://hospital.example.jp/device-serial",
                "value": "ECG-2024-00123"
            }
        ],
        # ── 稼働状態 ────────────────────────────────────────────────────
        "status": "active",
        # ── デバイス名称 ─────────────────────────────────────────────────
        "deviceName": [
            {
                "name": "心電計 Model-X",
                "type": "user-friendly-name"
            }, {
                "name": "BPM-X100",
                "type": "manufacturer-name"
            }    ],
        # ── モデル番号 ───────────────────────────────────────────────────
        "modelNumber": "BPM-X100",
        # ── シリアル番号 ─────────────────────────────────────────────────
        "serialNumber": "ECG-2024-00123",
        # ── デバイス種別（SNOMED CT） ─────────────────────────────────────
        "type": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "86184003",
                    "display": "Electrocardiographic monitor and recorder"
                }    ],
            "text": "12誘導心電計"
        },
        # ── 製造情報 ─────────────────────────────────────────────────────
        "manufacturer": "CardioTech Japan Co. Ltd.",
        "manufactureDate": "2024-01-15",
        "expirationDate": "2029-01-14",
        # ── 管理組織（Reference） ─────────────────────────────────────────
        #"owner": {
        #    "reference": "Organization/org-001",
        #    "display": "〇〇病院 医療機器管理部"
        #},
        # ── 設置場所（Reference） ─────────────────────────────────────────
        #"location": {
        #    "reference": "Location/loc-ward3",
        #    "display": "3階病棟ナースステーション"
        #},
        # ── メモ ─────────────────────────────────────────────────────────
        "note": [
            {
                "text": "12誘導・安静時・負荷心電図検査の用途"
            }
        ]
    }
 
from datetime import datetime, timezone


def build_specimen(resource_id):
    """
    JP Core R4 Specimen Resource
    採血した血液検体
    """
    now = datetime.now(timezone.utc).astimezone().isoformat()

    specimen = {
        "resourceType": "Specimen",
        "id": resource_id,
        "meta": {
            "profile": [
                "http://jpfhir.jp/fhir/core/StructureDefinition/JP_Specimen"
            ]
        },
        "status": "available",
        "type": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "122555007",
                    "display": "Venous blood specimen"
                }
            ],
            "text": "静脈血"
        },
        #"subject": {
        #    "reference": "Patient/patient-001"
        #},
        #"receivedTime": now,
        "collection": {
            #"collectedDateTime": now,
            #"collector": {
            #    "reference": "Practitioner/practitioner-001"
            #},
            "bodySite": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "368208006",
                        "display": "Left cubital vein"
                    }
                ],
                "text": "左肘正中皮静脈"
            },
            "fastingStatusCodeableConcept": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0916",
                        "code": "F",
                        "display": "Fasting"
                    }
                ],
                "text": "空腹時"
            }
        },
        "container": [
            {
                "type": {
                    "text": "EDTA採血管"
                }
            }
        ]
    }
    return specimen 


#FHIR リソース をサーバーに転送して、結果を調べる
#python で、FHIR Serverへ、Practioner リソースをPUT
# （update）するプログラム（def tx_put():）を作成して、
# 戻り値は、（１）http_code と（２） 作成したリソースID
def tx_put(win, RES,  method: str = "PUT", base_url: str = ResSvr_URL,
    RESOURCE: Optional[dict] = None, resource_id: str = "",
    headers: Optional[dict] = None, timeout: int = 10,
    save: int = 1, deb=0
) -> tuple[int, Optional[str]]:
    """
    FHIR Server の Practitioner リソースを PUT（更新）/POST（Create）する。
    ----------
    win, 
    RES: リソースの種別（Patient, Practioner, Device)
    method: str 送信手段（post/put)
    resource_id : str,  更新対象のリソース ID（URL: {base_url}/{RES}/{resource_id}）
    RESOURCE : dict, optional  PUT するリソース本体。
    base_url : str,         FHIR サーバーのベース URL
    headers : dict, optional,         HTTPヘッダー。省略時はデフォルトを使用。
    timeout : int,         タイムアウト秒数
    save : int, 結果のリソースを保存する
    -------
    Returns
        http_code   : int           HTTPステータスコード
        resource_id : str | None    作成・更新されたリソースID（取得失敗時は None）
    """
    if RESOURCE is None:
        RESOURCE = build_practitioner(resource_id)
 
    if headers is None:
        headers = HEADERS = {
            "Content-Type": "application/fhir+json",
            "Accept":       "application/fhir+json",
        }
    if method == "PUT":
        url = f"{base_url}/{RES}/{resource_id}"
    else:
        url = f"{base_url}/{RES}"
        
    if deb: win["-body-"].print(f"   url = {url}")
    
    try:
        if method == "PUT":
            response = requests.put(
                url,
                headers=headers,
                data=json.dumps(RESOURCE, ensure_ascii=False),
                timeout=timeout,
            )
        else:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(RESOURCE, ensure_ascii=False),
                timeout=timeout,
            )
        
        http_code = response.status_code
        returned_id: Optional[str] = None
 
        # ── レスポンスボディからリソースIDを取得 ──────────────────────
        if response.content:
            try:
                body = response.json()
                logger.debug(f"#971 body= {body}")
                # 方法①: ボディの id フィールド
                returned_id = body.get("id")
 
                # 方法②: Location ヘッダーからも取得を試みる
                if not returned_id:
                    location = response.headers.get("Location", "")
                    # 例: http://...../Practitioner/123/_history/1
                    parts = [p for p in location.split("/") if p]
                    if RES in parts:
                        idx = parts.index(RES)
                        if idx + 1 < len(parts):
                            returned_id = parts[idx + 1]
                # save resource
                if save and returned_id:
                    fn = f"GEN_OBS/{RES}_{returned_id}.json"
                    with open(fn, "w", encoding='utf-8') as f:
                        json.dump(body, f, indent=2, ensure_ascii=False)
                    window["-body-"].print(f"{RES} was saved in '{fn}'." )
                    
            except (ValueError, KeyError):
                # JSON でない場合でも Location ヘッダーを試みる
                location = response.headers.get("Location", "")
                parts = [p for p in location.split("/") if p]
                if "Practitioner" in parts:
                    idx = parts.index("Practitioner")
                    if idx + 1 < len(parts):
                        returned_id = parts[idx + 1]
 
        # 成功ステータス (200 / 201) かつ ID 未取得の場合はリクエストの ID を使う
        if http_code in (200, 201) and not returned_id:
            returned_id = resource_id
 
        # ── ログ出力 ────────────────────────────────────────────────
        print(f"[tx_put] URL        : {url}")
        print(f"[tx_put] HTTP Code  : {http_code}")
        print(f"[tx_put] Resource ID: {returned_id}")
 
        return http_code, returned_id
 
    except requests.exceptions.ConnectionError as e:
        print(f"[tx_put] 接続エラー: {e}")
        return 503, None
    except requests.exceptions.Timeout as e:
        print(f"[tx_put] タイムアウト: {e}")
        return 408, None
    except requests.exceptions.RequestException as e:
        print(f"[tx_put] リクエストエラー: {e}")
        return 500, None
 
     
    
def set_pat(Patient, win):
    """Patient resource の情報を更新"""
    # --- set pat information 
    print(f"#573 id = {dotItem2('id', Patient)}")
    family = dotItem2("name.family", Patient)
    name = dotItem2("name.given", Patient)
    print(f"#575 family = {family}")
    win["-family_IDE-"].update(family)
    win["-given_IDE-"].update(name)
    win["-gender-"].update(dotItem2("gender", Patient))
    win["-use-"].update(dotItem2("name.use", Patient))
    win["-birthDate-"].update(dotItem2("birthDate", Patient))

def read_fn(p, win, output_enable=True):
    print(f"p = {p}")
    if os.path.exists(p):
        window['-body-'].print(f"\nfile: {p} found.")
        print(f"file: {p} found.")
        logger.debug(f"file: {p} was loaded.")
    else:
        window['-body-'].print(f"ERROR - file: {p} is not found.",
              text_color="red")
        print(f"ERROR - file: {p} is not found.")
        logger.debug(f"ERROR - file: {p} is not found.")
        return None
    
    with open(p, "r", encoding='utf-8') as f:
        obj = json.load(f)
    if output_enable:
        for i in obj.keys():
            o = f"{obj.get(i)}"[:60]+' ...'
            win['-body-'].print(f"{i:10}: {o}", text_color="blue") 
    return obj


def set_obs(Observation, win):
    """Observation resource の情報を更新"""
    # --- set pat information 
    _id = dotItem2("id", Observation)
    value_analysis[_id] = ""
    print(f"#575 _id = {_id}")
    effect = dotItem2("effectiveDateTime", Observation)
    
    # category
    cat = dotItem2("category.coding.code", Observation)
    print(F"#567 cat = [{cat}]")
    
    # code
    code = dotItem2("code.coding.code", Observation)
    code1 = dotItem2("code.coding.display", Observation)
    code = f"{code} - " + f"{code1}"
    
    # value
    vType = "Not found"
    for i in Observation.keys():
        if "value" in i:
            vType = i
            break
    win["-vtype-"].update(vType)
    
    if vType == "Not found":
        win["-vtype-"].update(color="red")
    else:
        win["-vtype-"].update(color="black")

    if vType == "valueQuantity":
        v = dotItem2(f"{vType}.value", Observation)
        v1 = dotItem2(f"{vType}.unit", Observation)
        value_analysis[_id] = {"v": v, "v1": v1}
        v = f"{v} " + f"{v1}"
    elif vType == "valueBoolean":
        v = "true" if dotItem2(f"{vType}", Observation) else "false"
        value_analysis[_id] = {"v": v}
    elif vType == "valueString":
        v = dotItem2(f"{vType}", Observation)
        value_analysis[_id] = {"v": v}
    elif vType == "valueCodeableConcept":
        v = dotItem2(f"{vType}.coding.code", Observation)
        v1 = dotItem2(f"{vType}.coding.display", Observation)
        value_analysis[_id] = {"v": v, "v1": v1}
        v = f"{v} " + f"{v1}"
    elif vType == "valueDateTime":
        v = dotItem2(f"{vType}", Observation)
    else:
        v = None
    print(f"#627 v = {v}, vType={vType}")
    logger.debug(f"#627 v = {v}, vType={vType}")
    win["-value-"].update(f"{v}")
    win["-obs-id-"].update(f"{_id}")
    win["-effect-"].update(f"{effect}")
    win["-status-"].update(f"{dotItem2('status', Observation)}")
    win["-cat-"].update(f"{cat}")
    win["-code-"].update(f"{code}")
    win["-subject-"].update(f"{dotItem2('subject.reference', Observation)}")
    win["-subject-"].update(color="purple")
    
    
def copy_from_pat(Patient, win):
    ref = dotItem2('id', Patient)
    print(f"#548 ref={ref}")
    win["-subject-"].update(f"Patient/{ref}")
    win["-subject-"].update(color="red")

# Observation resource set を作成する。
def GenObs(win, event, values):
    
    try:
        pats = []
        for n in ["1","2","3","4"]:
            if values[f"pat{n}-on"]:
                pats.append(values[f"-pat{n}-"].split()[0]) 
        
        win["-body-"].print(f"\npats: {pats}",
                            text_color="blue")
        
        DIR_GENERATED_OBS, total = gen_obs_main(pats, stats, days, mess, 
                                        values, win)
        
        win["-body-"].print(f"total = {total}",)
        logger.debug(f"Obs was saved in {DIR_GENERATED_OBS}",)
        win["-body-"].print(f"Observation resources were saved in '{DIR_GENERATED_OBS}'.",)
        #aaa = json.dumps(Obs, indent=2)[:300]+" ...(trimmed.)"
        #logger.debug(f"Obs = {aaa}")
        win["-body-"].print(f"   ==> GenObs: Successfully end.\n"
                            f"   ==> total Obs: {total}",
                            text_color="Green")
        return True
    
    except Exception as e:
        traceback.print_exc()
        logger.debug(f"GenObs: Error occured: {e}")
        win["-body-"].print(f"GenObs: Error occured: {e}", 
                            text_color="red")

def read_para2():
    return {
        "1": {
            "id": "1234567801",
            "kana": "オオゾネ　ジン",
            "kanji": "大曽根　仁",
            "romaji": "JIN OZONE",
            "gender": "M",
            "birthday": "19810101",
            "zip": "105-0004",
            "address": "東京都港区新橋２丁目５番５号",
            "tel": "03-3506-8010",
            "res_id": "IHE-J-CTN-001"
        },
        "2": {
            "id": "1234567802",
            "kana": "クロカワ　ケイジ",
            "kanji": "黒川　慶二",
            "romaji": "KEIJI KUROKAWA",
            "gender": "M",
            "birthday": "19820202",
            "zip": "460-0004",
            "address": "愛知県名古屋市中区新栄町一丁目１番",
            "tel": "052-228-8181",
            "res_id": "IHE-J-CTN-002"
        },
        "3": {
            "id": "1234567803",
            "kana": "メイジョウ　エリカ",
            "kanji": "名城　恵梨香",
            "romaji": "ERIKA MEIJO",
            "gender": "F",
            "birthday": "19830303",
            "zip": "182-0025",
            "address": "東京都調布市多摩川３－３５－４",
            "tel": "042-485-7111",
            "res_id": "IHE-J-CTN-003"
        },
        "4": {
            "id": "1234567804",
            "kana": "ヒサヤ　キョウコ",
            "kanji": "久屋　恭子",
            "romaji": "KYOKO HISAYA",
            "gender": "F",
            "birthday": "19840404",
            "zip": "161-8560",
            "address": "東京都新宿区西落合１丁目３１番４号",
            "tel": "03-5996-8000",
            "res_id": "IHE-J-CTN-004"
        },
        "5": {
            "id": "1234567805",
            "kana": "サカエ　カツミ",
            "kanji": "栄　克実",
            "romaji": "KATSUMI SAKAE",
            "gender": "M",
            "birthday": "19800101",
            "zip": "113-8483",
            "address": "東京都文京区本郷３－３９－４",
            "tel": "03-3815-2121",
            "res_id": "IHE-J-CTN-005"
        },
        "6": {
            "id": "1234567806",
            "kana": "ヤバ　ミツル",
            "kanji": "矢場　満",
            "romaji": "MITSURU YABA",
            "gender": "M",
            "birthday": "19800101",
            "zip": "103-0028",
            "address": "東京都中央区八重洲１－５－３",
            "tel": "03-3231-8755",
            "res_id": "IHE-J-CTN-006"
        },
        "7": {
            "id": "1234567807",
            "kana": "カミマエヅ　ナオ",
            "kanji": "上前津　奈央",
            "romaji": "NAO KAMIMAEZU",
            "gender": "F",
            "birthday": "19870707",
            "zip": "108-8001",
            "address": "東京都港区芝５－７－１",
            "tel": "03-3454-1111",
            "res_id": "IHE-J-CTN-007"
        },
        "8": {
            "id": "1234567808",
            "kana": "ヒガシベツイン　ミチコ",
            "kanji": "東別院　美智子",
            "romaji": "MICHIKO HIGASHIBETSUIN",
            "gender": "F",
            "birthday": "19880808",
            "zip": "103-8510",
            "address": "東京都中央 区日本橋箱崎町１９－２１",
            "tel": "03-6667-1111",
            "res_id": "IHE-J-CTN-008"
        },
        "9": {
            "id": "1234567809",
            "kana": "カナヤマ　ケンジ",
            "kanji": "金山　憲史",
            "romaji": "KENJI KANAYAMA",
            "gender": "M",
            "birthday": "19890909",
            "zip": "324-8550",
            "address": "栃木県大田原市下石上１３８５番地",
            "tel": "0287-26-6211",
            "res_id": "IHE-J-CTN-009"
        },
        "10": {
            "id": "1234567810",
            "kana": "ヒビノ　ミサト",
            "kanji": "日比野　美里",
            "romaji": "MISATO HIBINO",
            "gender": "F",
            "birthday": "19901010",
            "zip": "105-7123",
            "address": "東京都港区東新橋１－５－２",
            "tel": "03-6252-2220",
            "res_id": "IHE-J-CTN-010"
        },
        "11": {
            "id": "1234567811",
            "kana": "サカエダ　ハルコ",
            "kanji": "栄田　春子",
            "romaji": "HARUKO SAKAEDA",
            "gender": "F",
            "birthday": "19891111",
            "zip": "105-1234",
            "address": "東京都江戸川区南葛西１－２－３",
            "tel": "03-5674-1234",
            "res_id": "IHE-J-CTN-011"
        },
        "12": {
            "id": "1234567812",
            "kana": "カネダ　ミツコ",
            "kanji": "金田　満子",
            "romaji": "MITSUKO KANEDA",
            "gender": "F",
            "birthday": "19891212",
            "zip": "105-2345",
            "address": "東京都中央区八重洲２－３－４",
            "tel": "03-3231-2345",
            "res_id": "IHE-J-CTN-012"
        },
        "13": {
            "id": "1234567813",
            "kana": "タシロ　ケイジ",
            "kanji": "田代　慶仁",
            "romaji": "KEIJI TASHIRO",
            "gender": "M",
            "birthday": "19900303",
            "zip": "105-3456",
            "address": "東京都港区芝３－４－５",
            "tel": "03-3454-3456",
            "res_id": "IHE-J-CTN-013"
        },
        "14": {
            "id": "1234567814",
            "kana": "カネダ　ミツハル",
            "kanji": "金田　光春",
            "romaji": "MITSUHARU KANEDA",
            "gender": "M",
            "birthday": "19340627",
            "zip": "799-2340",
            "address": "愛媛県松山市北条１３５－５",
            "tel": "089-993-1000",
            "res_id": "IHE-J-CTN-014"
        },
        "15": {
            "id": "1234567890",
            "kana": "フクオカ　チヒロ",
            "kanji": "福岡　千尋",
            "romaji": "CHIHIRO FUKUOKA",
            "gender": "F",
            "birthday": "19901010",
            "zip": "105-7123",
            "address": "東京都港区東新橋１－５－２",
            "tel": "03-6252-2220"
        }
    }



from pathlib import Path

def get_obs_filenames(directory="GEN_OBS", filter="obs*.json"):
    """
    directory内の 'obs*.json' のファイル名をソートして返す。
    Returns:
        list[str]
    """
    path = Path(directory)
    return sorted(f.name for f in path.glob(filter))

def Transfer(win, event, values, deb=0):
    """
    GEN_OBS/[today] にある "obs_*.json" をすべて Serverへ転送（PUT/POST)する
    Args:
        win (_type_): _description_
        event (_type_): _description_
        values (_type_): _description_
    """
    wp = win["-body-"].print

    wp("   === tx_res ===")
    total = 0
    try:
        pats = []
        for n in ["1","2","3","4"]:
            if values[f"pat{n}-on"]:
                pats.append(values[f"-pat{n}-"]) 
        
        wp(f"\npats: {pats}", text_color="blue")
        method = "PUT" if values["-method-"].split()[0].upper() == "PUT" else "POST"
        RES = "Observation"
        url = values["-server-"]
        wp(f"method: {method}, RES: {RES}")
        
        # get file list
        filter = "obs*.*"
        wp(f"DIR_GENERATED_OSB: {DIR_GENERATED_OBS}, filter: {filter}")
        fns = get_obs_filenames(DIR_GENERATED_OBS, filter)
        wp(f"fns - len = {len(fns)}")
        for n, fn in enumerate(fns,1):
            if deb: wp(f"{n:3}) fn: {fn}")
        
            # put/post 
            # tx_put(win, RES,  method, url, RESOURCE, resource_id,
            #        headers, timeout: int = 10,save: int = 1)
            fn = os.path.join(DIR_GENERATED_OBS, fn)
            with open(fn, "r", encoding='utf-8') as f:
                RESOURCE = json.load(f)   
            resource_id = RESOURCE.get("id","null")
            
            http_code, resource_id = tx_put(win, RES, method, url,
                                            RESOURCE, resource_id, save=0)

            wp(f"{n:3}) fn: {fn}, code: {http_code}")
            if http_code in [200, 201]:
                total += 1
                wp(f"{n:3}) fn: {fn} --- OK", text_color="green")
            else:
                wp(f"{n:3}) fn: {fn} --- NG", text_color="red")   
            
            if deb and n>=10: break
        
        
        
        win["-body-"].print(f"----",)
        win["-body-"].print(f"   ==> Transfer: Successfully end.\n"
                            f"   ==> total Obs: {total}",
                            text_color="Green")
        return True
    
    except Exception as e:
        traceback.print_exc()
        logger.debug(f"GenObs: Error occured: {e}")
        win["-body-"].print(f"GenObs: Error occured: {e}", 
                            text_color="red")


### START MAIN
def main():
    """
    script_path = os.path.abspath(sys.argv[0])
    script_name = os.path.basename(script_path)
    print(f"スクリプトのパス: {script_path}")
    print(f"スクリプト名: {script_name}")
    # ---
    hostname = socket.gethostname()
    os_name = platform.system()
    print(f"#620 os_name={os_name}, hostname={hostname}")
    
    #local_ip = get_local_ip_address()
    local_ip = env["ip"]
    if local_ip:
        print(f"自ホストのローカルIPアドレス: {local_ip}")
    else:
        print("ローカルIPアドレスを取得できませんでした。")
    """
    script_name = env["script_name"]
    ### create Window
    flag = 1 # メイリオ,"Arial"
    win_font = ("BIZ UDPゴシック", 11, )
    default_font = (sel_font, f_size)

    ### ファイル名の拡張管理用 
    fn_count = {} # fn_count[fn] = (同じfilenameの作成回数)

    # for debug
    if 0:
        fn = 'mylib\\C.QEDm患者一覧.txt'
        
        pat_para = read_para(fn)
        for i in range(1,15):
            pat_para[f"{i}"]["res_id"] = f"IHE-J-CTN-{i:03}"
    else:
        pat_para = read_para2()
        
    logger.debug(f"\npat_para = \n{json.dumps(pat_para, indent=2, ensure_ascii=False)}")

    logger.debug(f"#1139 stats={stats}")
    logger.debug(f"days={days}")
    logger.debug(f"mess={mess}")
    
    ### window loop for layout update
    for loop in range(10):
        lay_main = [
            # Title
            [eg.Text("", expand_x=True),
            eg.Text("Observation res. Create & Transfer  ", 
                    font=("BIZ UDPゴシック",14,'bold'),text_color="gray"),
            eg.Text("v1.0 (2026-06-26)", font=FA10B, color="purple",
                    pad=(0,0,0,20),), # pad: x,y
            eg.Text("", expand_x=True),
            eg.Button("使い方", background_color=b_color)],
            [lay_svr()], # template
            [lay_pat()], # patient
            [lay_info()], # Observation
            #[lay_val()], # value type etc.
            [lay_cont()], # # control
            ]
            
        with eg.Window(f"IHE-GUI:  {script_name}", layout=lay_main, 
                    show_scrollbar=True,
                    font=win_font, finalize=True, resizable=True, 
                    center_window=False, location=(10,10)) as window:
            if flag:
                flag = 0
                logger.debug(f"get_center_location= {window.get_center_location()}")
                logger.debug(f"get_screen_size= {window.get_screen_size()}")
                aaa = 0.98
                logger.debug(f"set_alpha_channel= {aaa}")
                window.set_alpha_channel(aaa)
                w_size = (720,750) # Width, Height
                logger.debug(f"set_size= {w_size}")
                window.set_size(w_size)
                logger.debug(f"get_size= {window.get_size()}")
                theme = eg.get_current_theme()
                logger.debug(f"theme= {theme}")
                #setByMap(j_map, ws, PTR, window)
                #window["-body-"].print(f"\nname_use= {name_use}", text_color="purple")
                #window["-body-"].print(f"\ngender_list= {gender_list}", text_color="purple")
                #window["-body-"].print(f"\nmarital_list= {marital_list}", text_color="purple")

                ### for notePC
                print(f"get_screen_size={window.get_screen_size()}")
                (Width, Height) = window.get_screen_size()
                if Height < 850:
                    w_size = (720,Height-70) # Width, Height
                    print(f"set_size={w_size}")
                    window.set_size(w_size)
                    #window.update(show_scrollbar=True)
                    window.set_grab_anywhere(True)

            # event loop
            for event, values in window.event_iter(timeout=1000): # 1000 = 1 sec.
                if event == "-TIMEOUT-":
                    window["-now-"].update(f"  {JST()}")
                    continue
                
                if event in ["test", "test(1)", "test(2)",
                    "test(3)", "test(4)", "Tx(1)", "Tx(2)",
                    "Tx(3)", "Tx(4)"]:
                    put_test(window, event)
                    continue
                
                if event in ["Exit", eg.WINDOW_CLOSED, "REDRAW"] :
                    break
                
                if event in ["使い方"]:
                    myPop(mes_manual, script_name, 
                          font=("メイリオ", 13, "bold italic"),)
                    continue
                
                if event in ["check_server","Method(0)"]:
                    check_server(values["-server-"], window)
                    continue
                
                if event in ["Set"]:
                    method = values["-method-"].split()[0].upper()
                    window["-body-"].print(f"method: {method}")
                    if method == "PUT":
                        for n,i in enumerate(["IHE-J-CTN-001","IHE-J-CTN-002",
                               "IHE-J-CTN-003","IHE-J-CTN-004",],1):
                            window[f"-pat{n}-"].update(i)
                    else:
                        for n in range(1,5):
                            window[f"-pat{n}-"].update("---")
                    continue
                        
                                                    
                if  event in ["GenObs"]:
                    GenObs(window, event, values)
                    continue
                
                if event in ["Transfer"]:
                    Transfer(window, event, values)
                    continue
                
                if event in ["Gazelle-Web"]:
                    if eg.is_mac():
                        subprocess.call(f"open {WEB_SITE}", shell=True)
                    else:
                        subprocess.call(f"start {WEB_SITE}", shell=True)
                    break
                
                if event in ["LOG-DIR", "OBS-DIR"]:
                    abspath =  os.path.split(os.path.abspath(sys.argv[0]))
                    dir = abspath[0]
                    dir = dir.replace("mylib", "")
                    subdir = "log" if "LOG" in event else "GEN_OBS"
                    dir = os.path.join(dir, subdir)
                    print(f"path= {dir}")
                    os.startfile(dir)

                if event in ["LOG"]:
                    logger.debug(f"{os.path.abspath('./log/')}")
                    startFile("log\\LOG_OBS-TX.TXT")
                
                if event in ["test"]:
                    window["-body-"].print(f"   ===> {event}")
                                
                if event in ["Gender_Get"]:
                    G_no, gender_list, G_exp = gender_get(TermRepo_URL, save="G_json.txt")
                    window["-body-"].print(f"gender_get= {G_no},  {gender_list}")
                    logger.info(f"gender_get= {G_no},  {gender_list}")
                    window["-gender-"].set_values(gender_list)
                    window["-gender-"].update("- 選択して下さい。 -")
                    continue
                
                if event in ["MS_Get"]:
                    MS_no, marital_list, MS_exp = marital_status_get(TermRepo_URL, save="MS_json.txt")
                    window["-body-"].print(f"marital_status_get= {MS_no},  {marital_list}")
                    logger.info(f"MS_get= {MS_no},  {marital_list}")
                    window["-marital_s-"].set_values(marital_list)
                    window["-marital_s-"].update("- 選択して下さい。 -")
                    continue
                
                if event == "List patient":
                    ### res-server から patient のリストを取得する。
                    ans = eg.input("表示する最大数を入力\n_count: [50] >", )
                    print(f"ans= {ans}")
                    if ans is None or ans =='':
                        ans = '50'
                    getPatList(values, window, count=ans)
                    continue
                
                
                if event == "Patient edit":
                    eg.print("List patient 未実装", font=("arial", 14, "bold"))
                    continue

                if event == 'Save-Conf':
                    conf_dic["values"] = values
                    conf_dic["day"] = JST()
                    # save config 
                    with open(fn_conf, "w", encoding='utf-8') as f:
                        json.dump(conf_dic, f, indent=2, ensure_ascii=False)
                    window['-body-'].print(f" conf_dic was saved in '{fn_conf}'.")
                    continue
                
                if event == "ID paste":
                    eg.set_clipboard(id)
                    eg.print("Copied to clipboard:\n" + f"[{id}]" )
                    continue

                if event == "clear":
                    window["-body-"].update("=== cleared. ===\n")
                    continue

                if event in ["HELP", "HELP1"]:
                    win = help_window(script_name)
                    win.close()
                    continueoutput_dir="fhir_resources"
                    continue
                
                if event in ["SVCM_test95"]:
                    logger.debug(f"SVCM_test95")
                    win = test_window95(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event in ["SVCM_test96"]:
                    logger.debug(f"SVCM_test96")
                    win = test_window96(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event in ["SVCM_test97"]:
                    logger.debug(f"SVCM_test97")
                    win = test_window97(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event in ["SVCM_test98"]:
                    logger.debug(f"SVCM_test98")
                    win = test_window98(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event in ["SVCM_test99"]:
                    logger.debug(f"SVCM_test99")
                    win = test_window99(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event in ["SVCM_test100"]:
                    logger.debug(f"SVCM_test100")
                    win = test_window100(window, values, logger=logger, script_name=VERSION)
                    win.close()
                    continue
                
                if event == "-DBconnect-":
                    DB_CONNECT = values["-DBconnect-"]
                    window["-body-"].print(f'DB_CONNECT = {DB_CONNECT}')
                    continue

                values.pop("-body-")
                print(f"\n#845 event: [{event}], values: [{values}]")

                # LOG
                text = f"#event: [{event}], "
                
                window["-body-"].print(text, text_color="darkblue", ) # background_color="lightpink"
                #window["-body-"].update(text)
        # loop end
        print(f"#982 loop end event = {event}")
        if event in ["Exit", eg.WINDOW_CLOSED]:
            break
    # ---
    print("    ==> NORMAL END.")
    # --- main() end.
    
if __name__ == '__main__':
    main()
    