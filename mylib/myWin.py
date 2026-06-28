import TkEasyGUI as eg

if __name__ == '__main__':
    from readWriteXL import JST
else:
    from mylib.readWriteXL import JST
    
FA11B = ("Arial", 11, "bold")
FA12B = ("Arial", 12, "bold")
FA12BI = ("Arial", 12, "bold italic")

class myWin(eg.Window):   
    flag = True
    size=(470,500)
    FONT = ("BIZ UDPゴシック", 13, "bold italic")
    
    def __init__(self, title, layout, size=(450,600), 
                 **kwargs):
        if kwargs.get("font"):
            FONT = kwargs.get("font")
            print(f"#21 FONT= {FONT}")
        else:
            #FONT = ("BIZ UDPゴシック", 14, "bold")
            FONT = ("メイリオ", 14, "bold italic"),
        FONT = ("メイリオ", FONT[1], FONT[2])
        self.default_font = FONT
        print(f"#22 myWin: FONT = {FONT}")
        # 共通の初期設定をここでまとめる
        self.default_size = self.size
        if kwargs.get("message"):
            message = kwargs.get("message")
            kwargs.pop("message")
        else:
            message = "test messages ..."
            
        # レイアウトに共通のフッターボタンを追加する例
        layout = layout + [
            [eg.Label("Popup:", color="purple",
                      font = ("BIZ UDPゴシック", 16, "bold italic"))],
            [eg.Multiline(message, size=(42, 20), key='-body-',
                    font=self.FONT, expand_y=True, expand_x=True,
                    pad=(1,0,0,10), background_color="#FBF5B6",
                    
                    color="blue") ],
            [eg.Button("Close", key="Exit", color="red", font=FA12B),
             eg.Text("text", font=FA12BI, key='-now-'),
             eg.Text("", expand_x=True),
             eg.Text("  resize ...▶", font=FA11B),
             ]]

        # 親クラス Window の初期化
        super().__init__(title, layout, **kwargs)
    
    # 独自メソッドを追加
    def log(self, message):
        self['-body-'].print(f"[myWin LOG] {message}",
                text_color="green")

### test myWin 
def myPop(mes='null message', script_name="", 
          font=("メイリオ", 14, "bold italic"),
          **kwargs):
    
        
    print(f"#56 myPop: font = {font}")
    with myWin(f"IHE-GUI:  {script_name}", layout=[[]], 
                finalize=True, resizable=True, 
                center_window=False, location=(10,10),
                font=font,
                message=mes, **kwargs) as window:
        first = True
        if first:
            #window["-body-"].print("\ntest test")
            window["-body-"].update(font=font)
            window["-body-"].print(f"{font}")
        # event loop
        for event, values in window.event_iter(timeout=1000): # 1000 = 1 sec.
            if event == "-TIMEOUT-":
                window["-now-"].update(f"  {JST()}")
                #window.log("test...")
                continue
            if event in ["Exit", eg.WINDOW_CLOSED, "REDRAW"] :
                break
# --- 
if __name__ == '__main__':   
    mes_manual = "\n〇使い方\n\n準備： IHE-TX-Res-gui3.py\n" + \
    "   templateとなる Patient, Observation をDLする。\n" + \
    "1. template欄で、[Folder], [Filter] をセットして、\n" + \
    "   [GenList]を実行し、[Filename]を選択し、[Load]で\n" + \
    "   テンプレートの Observation resource を読み込む。\n" + \
    "2. Patient欄で、Observationに紐づける[ID]を選択する。\n"+ \
    "3. Observation欄で、[Value]、[Date]などを編集して、\n" + \
    "   保存する。"        
    w = myPop(mes_manual)
