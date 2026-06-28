"""
# Version info

This script shows the version information of TkEasyGUI and system information.
Also Fig. is displayed using column.
"""

import subprocess
import TkEasyGUI as eg
import os

WEB_SITE = "https://github.com/kujirahand/tkeasygui-python/"
S_COPY = eg.get_text("Copy")
S_CLOSE = eg.get_text("Close")


# response = requests() の結果を記録する。
def resRec(title, url, headers, JJJ, fn1, res, sep='-'*70):
    '''response = requests() の結果を記録する。'''    
    with open(fn1, "w", encoding='utf-8') as f9:
        print(f"=== {title} ===", file=f9)
        print(f"url= {url}, headers= {headers}\n{sep}", file=f9)
        print(f"res= {res.text}", file=f9)
        JJJ += 1
    return JJJ


# ファイルを開く
def startFile(filename):
    """指定したファイルをWindowsの紐付けたプログラムで開く"""
    try:
        # ファイルが存在するか確認
        if not os.path.exists(filename):
            # ファイルが存在しない場合は作成（テスト用）
            with open(filename, 'w') as f:
                f.write("ファイルが存在しない.\nこれはテストファイルです。")

        # ファイルを開く
        os.startfile(filename)
        print(f"ファイル '{filename}' を開きました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{filename}' が見つかりません。")
    except Exception as e:
        print(f"ファイルを開く際にエラーが発生しました: {e}")

def help_window(script_name="Ver. 2025-03-30"):
    # define layout
    # col1 - layout
    layout1 = [
            [eg.Text(f"JROD-gui Project: {script_name}", font=("Arial", 13, "bold"), color="darkgreen")],
            [eg.Text(f"{eg.__doc__.strip()}", color="navy")],
            [eg.Frame("Version", expand_x=True,
                    layout=[
                        [   eg.Text("TkEasyGUI: "),
                            eg.Button(f"v{eg.__version__}", key="-b1-"),eg.Text(" "),
                            eg.Button("Web"),  ],
                    ],  ), ],
                ]
    
    layout2 = [[eg.Frame("", layout = [
                    [eg.Image(size=(99, 100), filename="mylib\\img\\Leaf2.png", key="-image-")],])],
              ]      
    col1 = eg.Column(layout1, key="col1", expand_x=True)
    col2 = eg.Column(layout2, key="col2")
    
  
    layout = [ [col1, col2],
        #[main_lay,],
        #[eg.Text(f"JROD-gui Project: {script_name}", font=("Arial", 14, "bold"), color="darkgreen"),],
        #[eg.Text(f"{eg.__doc__.strip()}", color="navy"),],
        #[eg.Frame("Version",
        #        expand_x=True,
        #        layout=[
        #            [   eg.Text("TkEasyGUI: "),
        #                eg.Button(f"v{eg.__version__}", key="-b1-"),eg.Text(" "),
        #                eg.Button("Web"),  ],
        #        ],  )
        #],
        [eg.Frame("System info:",
                layout=[
                    [   eg.Multiline( f"{eg.get_system_info()}",
                            key="-sys-info-",
                            size=(60, 8),
                            expand_x=True,
                        )
                    ],
                    [eg.Button(S_COPY), eg.Button("Copy as Markdown")],
                ], expand_x=True,
            )
        ],
        [eg.Column(
                layout=[[eg.Button("OK"), eg.Button(S_CLOSE)]],
                text_align="right",
                expand_x=True,
            ),
        ],
    ]
    # window create
    window = eg.Window("Version info", layout=layout, font=("Arial", 13 if eg.is_mac() else 11, "bold"), 
                    row_padding=3, modal = True)
    # image set
    imgs = ["Leaf2.png", "YellowBall.png", "Universe.png",
            "a.jpg", "Ball-orange.png", "Daiz.png",
            "GolfBall.png", "GreenBall.png","Leaf.png", "setting.jpeg",
            "Person2.png","PinkBall.png","Untitled.jpg", "images.png"]
    src = "mylib\\img\\"
    ptr = 0
    window['-image-'].update(filename=src+imgs[ptr])
    # event loop
    for event, values in window.event_iter(timeout=5000): # mSec
        if event == "-TIMEOUT-":
            ptr += 1
            i = ptr % len(imgs)
            window['-image-'].update(filename=src+imgs[i])
            if ptr <= len(imgs): print(f"file: {imgs[i]}")
            continue
        print(f"# event = {event}, values = {values}")
        if event == "OK":
            #eg.popup("Thank you.")
            break
        if event == S_CLOSE:
            break
        if event in ["-b1-", "-b2-", "-b3-"]:
            btn: eg.Button = window[event]
            label = btn.get_text()
            eg.set_clipboard(label)
            eg.popup(f"Copied to clipboard:\n{label}")
        if event == S_COPY:
            text = window["-sys-info-"].get_text()
            eg.set_clipboard(text)
            eg.popup("Copied to clipboard.")
        if event == "Copy as Markdown":
            text = window["-sys-info-"].get_text()
            text = f"```\n{text}\n```\n"
            eg.set_clipboard(text)
            eg.popup("Copied markdown to clipboard.")
        if event == "Web":
            if eg.is_mac():
                subprocess.call(f"open {WEB_SITE}", shell=True)
            else:
                subprocess.call(f"start {WEB_SITE}", shell=True)
    return window

# -------------
if __name__ == "__main__":
    print("このスクリプトは直接実行されました")

    startFile("log.txt")
    print("finished.")
    if 0:
        win = help_window("このスクリプトは直接実行されました")
        win.close()

