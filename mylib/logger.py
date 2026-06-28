# -*- coding: utf-8 -*-

# =====================================================================
# Original: Pi5a:/home/jupyter/work/Oauth/common_lib/logger.py
# 2025-02-04
# 使用方法：
#     sys.path.append('/home/jovyan/work/OAuth/common_lib')
#     from logger import FMT, FMT2, createLogger, clearLogfile, log_init
#
#     初期化
#       os.makedirs("./log", exist_ok=True)
#       LOG_FN = "LOG_JROD.TXT"
#       logger = init_log(LOG_FN)
#
# =====================================================================
import inspect
import os

def location():
    """program名、module, 行番号を返す。【例】「('readWriteXL.py', '<module>', 590)」"""
    frame = inspect.currentframe().f_back
    return os.path.basename(frame.f_code.co_filename), frame.f_code.co_name, frame.f_lineno

def line():
    """Module名と行番号を求める 【例】「<module>: #592:」"""
    frame = inspect.currentframe().f_back
    return f"{frame.f_code.co_name}: #{frame.f_lineno:3}:"


# Logger用： 時刻をJSTにする。
### example format  2024-10-28
from datetime import datetime, timedelta, timezone
from logging import Formatter, LogRecord

class DatetimeFormatter(Formatter):
    def formatTime(self, record: LogRecord, datefmt=None):
        if datefmt is None:
            #datefmt = "%Y-%m-%d %H:%M:%S.%03d" # logging.Formatterのデフォルトと同じ形式
            datefmt = "%Y-%m-%d %H:%M:%S.%f" # for windows
            #datefmt = "%Y-%m-%d %H:%M:%S.%f%z" # 2024-08-15 18:09:17.468103+0900
        TZ_JST = timezone(timedelta(hours=+9), 'JST')
        created_time = datetime.fromtimestamp(record.created, tz=TZ_JST)
        s = created_time.strftime(datefmt)
        return s[:23] # 23桁まで

#fmt = DatetimeFormatter("%(asctime)s %(name)-8s:%(lineno)-3s %(funcName)s [%(levelname)-7s]: %(message)s") # ここでフォーマットを指定する
FMT = DatetimeFormatter("%(asctime)s [%(levelname).3s] %(name)s|%(funcName)s:%(lineno)-3s  %(message)s") # ここでフォーマットを指定する
FMT2 = DatetimeFormatter("%(asctime)s [%(name)s] %(message)s") 

# sh.setFormatter(fmt) で設定する。

#format = "%(levelname)-9s  %(asctime)s [%(filename)s:%(lineno)d] %(message)s"
format = "%(asctime)s - %(name)s - %(message)s"
# ハンドラ自体にフォーマットを設定しておく必要がある。
# format = "%(levelname)-9s  %(asctime)s [%(filename)s:%(lineno)d] %(message)s"
# fl_handler.setFormatter(Formatter(format))

# ------------------
### Logger  2024-10-28
from logging import getLogger, StreamHandler, Formatter, DEBUG, WARNING, handlers
#import pickleshare
import shutil, os

def createLogger(id='log', LOG_FN="LOG_C.TXT", rotate=True,
                    LOG_BASE='.', propagate=True, format=None,
                    LOG_DIR='./log', maxBytes=1024*100, backupCount=5, deb=0):
    # create logger
    if 1: print(f"createLogger: id={id}, LOG_FN={LOG_FN}, rotate={rotate},", 
            f"LOG_BASE='{LOG_BASE}', LOG_DIR='{LOG_DIR}', propagate={propagate}")
    logger = getLogger(id)
    logger.setLevel(DEBUG)
    
    # create console handler and set level to debug
    ch = StreamHandler()
    ch.setLevel(WARNING)
    fmt0 = DatetimeFormatter("%(asctime)s - %(name)s - %(message)s")
    if deb: print("type-fmt0=", type(fmt0))
    ch.setFormatter(fmt0)
    
    # create formatter
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')   
    rot_fn = os.path.join(LOG_BASE, LOG_DIR, LOG_FN)
    print(f"rot_fn='{rot_fn}'")
    fh = handlers.RotatingFileHandler(rot_fn, encoding="utf-8",
                    backupCount=backupCount, maxBytes=maxBytes) # default 100 KB   
    if format is not None:
        if deb: print("   createLogger: fmt: format")
        fh.setFormatter(format)
    else:
        if deb: print("   createLogger: fmt: defaut")
        fh.setFormatter(formatter)
    fh.setLevel(DEBUG)
    if rotate:
        fh.doRollover()
    # add handler to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = propagate
    return logger
    
# --- ファイルを初期化
def clearLogfile(LOG_FN, LOG_DIR='./log', LOG_BASE='.'):
    """LOG_DIRを作成して、そこにあるファイル(LOG*.txt)をすべて削除する。"""
    import glob
    global REC_NO
    LOG_FN = os.path.join(LOG_DIR, LOG_FN)
    print(f"   *** LOG FILE({os.path.abspath(LOG_FN)}) CLEAR ***")
    print(f"   *** LOG_BASE='{os.path.abspath(LOG_BASE)}', LOG_DIR='{os.path.abspath(LOG_DIR)} ***")
    
    log_fn = os.path.join(LOG_BASE, LOG_FN)
    print(f"#111 log_fn = '{log_fn}'")
    if os.path.isfile(log_fn):  
        #os.remove(log_fn)
        # *.txt を削除
        files = glob.glob(LOG_DIR + '/LOG*.txt')
        for fn in files:
            print(f"{fn} was deleted.")
            os.remove(fn)
    
    os.makedirs(os.path.join(LOG_BASE,LOG_DIR), exist_ok=True)
    
    # delete files
    files_to_delete = glob.glob(os.path.join(LOG_BASE, LOG_DIR,
                                             'LOG*.txt'))
    # ファイルごとに削除処理
    for file_path in files_to_delete:
        try:
            # os.remove() でファイルを削除
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            else:
                print(f"Skipped: {file_path} is not a file.")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
            
    print("---")
    print(f"File deletion process completed. ({len(files_to_delete)})")
    REC_NO = 0
    return REC_NO
    
# ============ Logger start =============
def log_init(LOG_FN, LOG_DIR='./log', LOG_BASE='.', 
             maxBytes=1024*100, backupCount=5, deb=0):
    #LOG_FN = 'LOG_C.TXT'
    clearLogfile(LOG_FN, LOG_DIR=LOG_DIR, LOG_BASE=LOG_BASE)
    logger = createLogger("log", LOG_FN, format=FMT, LOG_BASE=LOG_BASE,
                    backupCount=backupCount, LOG_DIR=LOG_DIR, maxBytes=maxBytes)
    
    if deb:
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')
    logger.info("=== logger initialized. ===")
    print("root-log created. END.")
    return logger

import glob
def get_file_info(directory, pattern, show=0):
    """
    指定したディレクトリ内で、パターンに一致するファイルの情報を取得する。

    Args:
        directory (str): ディレクトリのパス。
        pattern (str): ファイル名のパターン。

    Returns:
        list: ファイル情報のリスト。
    """

    file_info_list = []
    file_paths = glob.glob(os.path.join(directory, pattern))  # パターンに一致するファイルパスを取得

    for file_path in file_paths:
        file_name = os.path.basename(file_path) # ファイル名のみ抽出
        file_size = os.path.getsize(file_path)
        file_ctime = os.path.getctime(file_path)  # 作成日時 (Windows)

        file_ctime_datetime = datetime.fromtimestamp(file_ctime)

        file_info = {
            "name": file_name,
            "size": file_size,
            "ctime": file_ctime_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        }
        file_info_list.append(file_info)

    # if show:
    print("-" * 60)  
    for file_info in file_info_list:
        print(f"{file_info['name']:30} {file_info['size']:6} {file_info['ctime']}")
    print("-" * 60)    

    return file_info_list


# ---- for debug
if __name__ == "__main__":
    print("このスクリプトは直接実行されました")
    # logger start
    # logger start
    LOG_BASE = 'C:\\Temp\\QEDm'
    LOG_FN = "LOG_LOGGER.TXT"
    LOG_DIR = './log'
    os.makedirs(os.path.join(LOG_BASE,LOG_DIR), exist_ok=True)
    print(f"log_fn='{os.path.join(LOG_BASE, LOG_FN)}'")
    
    clearLogfile(LOG_FN, LOG_BASE=LOG_BASE, LOG_DIR=LOG_DIR)
    logger = createLogger("log", LOG_FN, LOG_BASE=LOG_BASE,
                          LOG_DIR=LOG_DIR, format=FMT)
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')    

    dir = "."
    pattern = "LOG*"
    fns = get_file_info(dir, pattern, show=1)
    # ファイル情報を表示
    for file_info in fns:
        print(f"Name: {file_info['name']}")
        print(f"Size: {file_info['size']} bytes")
        print(f"Created Time: {file_info['ctime']}")
        print("-" * 20)    