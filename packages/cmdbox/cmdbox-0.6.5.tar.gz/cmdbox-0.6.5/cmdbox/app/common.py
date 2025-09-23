from cmdbox import version
from cmdbox.app import feature, options
from cmdbox.app.commons import convert, module, loghandler
from cryptography.fernet import Fernet
from pathlib import Path
from rich.console import Console
from tabulate import tabulate
from typing import List, Tuple, Dict, Any
import argparse
import asyncio
import datetime
import logging
import logging.config
import locale
import hashlib
import inspect
import json
import numpy as np
import os
import random
import shutil
import string
import re
import requests
import subprocess
import tempfile
import time
import yaml
import sys
import threading


HOME_DIR = Path(os.path.expanduser("~"))
def copy_sample(data:Path, ver=version):
    """
    サンプルデータをコピーします。

    Args:
        data (Path): データディレクトリ
        ver (version, optional): バージョン. Defaults to version
    """
    dst_sample = Path(data) / '.samples' if data is not None else HOME_DIR / '.samples'
    #if dst.exists():
    #    return
    src = Path(ver.__file__).parent / 'extensions'
    def copy(src:str, dst:str):
        p = Path(dst)
        if not p.exists():
            shutil.copy2(src, dst)
    shutil.copytree(src, dst_sample, dirs_exist_ok=True, copy_function=copy)
    dst_config = Path(data) / f'.{ver.__appid__}' if data is not None else HOME_DIR / f'.{ver.__appid__}'
    dst_config.mkdir(parents=True, exist_ok=True)
    if not (dst_config / 'features.yml').exists():
        shutil.copy2(src / 'features.yml', dst_config / 'features.yml')
    if not (dst_config / 'user_list.yml').exists():
        shutil.copy2(src / 'user_list.yml', dst_config / 'user_list.yml')

def mklogdir(data:Path) -> Path:
    """
    ログディレクトリを作成します。

    Args:
        logdir (Path, optional): ログディレクトリのパス. Defaults to Path.cwd()/'log'.

    Returns:
        作成したログディレ作成したログディレクトリのパス
    """
    logdir = Path(data) / '.logs' if data is not None else HOME_DIR / '.logs'
    if not logdir.exists():
        return mkdirs(logdir)
    return logdir

def load_yml(yml_path:Path) -> dict:
    """
    YAMLファイルを読み込みます。

    Args:
        yml_path (Path): YAMLファイルのパス

    Returns:
        dict: 読み込んだYAMLファイルの内容
    """
    def _r(f):
        return yaml.safe_load(f)
    return load_file(yml_path, _r)

def save_yml(yml_path:Path, data:dict) -> None:
    """
    YAMLファイルに書き込みます。

    Args:
        yml_path (Path): YAMLファイルのパス
        data (dict): 書き込むデータ
    """
    def _w(f):
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    save_file(yml_path, _w)

def load_file(file_path:Path, func, mode='r', encoding='utf-8') -> None:
    """
    ファイルを読み込みます。読み込み時に排他ロックします。

    Args:
        file_path (Path): ファイルのパス
        func: 読み込んだデータを処理する関数
        mode (str, optional): ファイルモード. Defaults to 'r'.
        encoding (str, optional): エンコーディング. Defaults to 'utf-8'.
    """
    lock_file = f'{file_path}.lock'
    try:
        with open(lock_file, 'w') as fd:
            try:
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(fd.fileno(), msvcrt.LK_LOCK, 0)
                else:
                    import fcntl
                    fcntl.lockf(fd, fcntl.LOCK_EX)
                if 'b' in mode:
                    with open(file_path, mode) as f:
                        return func(f)
                else:
                    with open(file_path, mode, encoding=encoding) as f:
                        return func(f)
            finally:
                if sys.platform == 'win32':
                    msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 0)
                else:
                    fcntl.lockf(fd, fcntl.LOCK_UN)
    finally:
        try:
            os.remove(lock_file)
        except:
            pass

def save_file(file_path:Path, func, mode='w', encoding='utf-8') -> None:
    """
    ファイルに書き込みます。書き込み時に排他ロックします。

    Args:
        file_path (Path): ファイルのパス
        func: 書き込む関数
        mode (str, optional): ファイルモード. Defaults to 'w'.
        encoding (str, optional): エンコーディング. Defaults to 'utf-8'.
    """
    lock_file = f'{file_path}.lock'
    try:
        with open(lock_file, 'w') as fd:
            try:
                if sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(fd.fileno(), msvcrt.LK_LOCK, 0)
                else:
                    import fcntl
                    fcntl.lockf(fd, fcntl.LOCK_EX)
                if 'b' in mode:
                    with open(file_path, mode) as f:
                        func(f)
                else:
                    with open(file_path, mode, encoding=encoding) as f:
                        func(f)
            finally:
                if sys.platform == 'win32':
                    msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, 0)
                else:
                    fcntl.lockf(fd, fcntl.LOCK_UN)
    finally:
        try:
            os.remove(lock_file)
        except:
            pass

class CommonValue:
    _map = dict()

def set_common_value(key:str, value:Any) -> None:
    """
    共通の値を設定します。

    Args:
        key (str): キー
        value (Any): 値
    """
    CommonValue._map[key] = value

def get_common_value(key:str, default:Any=None) -> Any:
    """
    共通の値を取得します。

    Args:
        key (str): キー
        default (Any, optional): デフォルト値. Defaults to None.

    Returns:
        Any: 取得した値。存在しない場合はdefault値を返します。
    """
    return CommonValue._map.get(key, default)

def reset_logger(name:str, stderr:bool=False, fmt:str='[%(asctime)s] %(levelname)s - %(message)s', datefmt:str='%Y-%m-%d %H:%M:%S', level:int=logging.INFO) -> None:
    """
    指定されたロガーのハンドラをクリアし、新しいハンドラを追加します。
    Args:
        name (str): ロガーの名前
        stderr (bool, optional): 標準エラー出力を使用するかどうか. Defaults to False.
        fmt (str, optional): ログフォーマット. Defaults to '[%(asctime)s] %(levelname)s - %(message)s'.
        datefmt (str, optional): 日時フォーマット. Defaults to '%Y-%m-%d %H:%M:%S'.
        level (int, optional): ログレベル. Defaults to logging.INFO.
    """
    logger = logging.getLogger(name)
    #colorful = [h for h in logger.handlers if isinstance(h, loghandler.ColorfulStreamHandler) or isinstance(h, RichHandler)]
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(create_log_handler(stderr, fmt, datefmt, level, colorful=True))
    if get_common_value('webcall', False):
        # webcallの場合はStreamHandlerを削除
        for handler in logger.handlers:
            hc = handler.__class__
            if issubclass(hc, logging.StreamHandler) and not issubclass(hc, logging.FileHandler):
                logger.removeHandler(handler)

def create_log_handler(stderr:bool=False, fmt:str='[%(asctime)s] %(levelname)s - %(message)s', datefmt:str='%Y-%m-%d %H:%M:%S', level:int=logging.INFO, colorful:bool=True) -> logging.Handler:
    """
    ログハンドラを生成します。

    Args:
        stderr (bool, optional): 標準エラー出力を使用するかどうか. Defaults to False.
        fmt (str, optional): ログフォーマット. Defaults to '[%(asctime)s] %(levelname)s - %(message)s'.
        datefmt (str, optional): 日時フォーマット. Defaults to '%Y-%m-%d %H:%M:%S'.
        level (int, optional): ログレベル. Defaults to logging.INFO.
        colorful (bool, optional): カラフルなログを使用するかどうか. Defaults to True.
    Returns:
        logging.Handler: ログハンドラ
    """
    formatter = logging.Formatter(fmt, datefmt)
    #handler = RichHandler(console=Console(stderr=stderr), show_path=False, omit_repeated_times=False,
    #                      tracebacks_word_wrap=False, log_time_format='[%Y-%m-%d %H:%M]')
    if colorful:
        handler = loghandler.ColorfulStreamHandler(sys.stdout if not stderr else sys.stderr)
    else:
        handler = logging.StreamHandler(sys.stdout if not stderr else sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler

def create_console(stderr:bool=False, file=None) -> Console:
    """
    コンソールを生成します。

    Args:
        stderr (bool, optional): 標準エラー出力を使用するかどうか. Defaults to False.
        file (file, optional): 出力先のファイル. Defaults to None.
    Returns:
        Console: コンソール
    """
    #console = Console(soft_wrap=True, height=True, highlighter=loghandler.LogLevelHighlighter(), theme=loghandler.theme,
    #                  stderr=stderr, file=file)
    console = Console(height=False, highlighter=loghandler.LogLevelHighlighter(), theme=loghandler.theme,
                      soft_wrap=False, stderr=stderr, file=file, log_time=True, log_path=False, log_time_format='[%Y-%m-%d %H:%M:%S]')
    #console = Console(soft_wrap=True, stderr=stderr, file=file, log_time=True, log_path=False, log_time_format='[%Y-%m-%d %H:%M:%S]')
    return console

def console_log(console:Console, message:Any, highlight:bool=True, **kwargs) -> None:
    """
    コンソールにログを出力します。

    Args:
        console (Console): コンソール
        message (Any): 出力するメッセージ
        **kwargs: その他のキーワード引数
    """
    dtstr = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    console.print(f"{dtstr} {message}", highlight=highlight, crop=False, soft_wrap=True, **kwargs)

def default_logger(debug:bool=False, ver=version, webcall:bool=False) -> logging.Logger:
    """
    デフォルトのロガーを生成します。

    Args:
        debug (bool, optional): デバッグモード. Defaults to False.
        ver (version, optional): バージョン. Defaults to version.
        webcall (bool, optional): WebAPIからの呼出しの場合はTrue. setHandlerを削除します。. Defaults to False.

    Returns:
        logging.Logger: ロガー
    """
    logger = logging.getLogger(ver.__appid__)
    set_common_value('webcall', webcall)
    if not webcall:
        handler = create_log_handler()
        handler.setLevel(logging.DEBUG if debug else logging.INFO)
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    return logger

def load_config(mode:str, debug:bool=False, data=HOME_DIR, webcall:bool=False, ver=version) -> Tuple[logging.Logger, dict]:
    """
    指定されたモードのロガーと設定を読み込みます。

    Args:
        mode (str): モード名
        debug (bool, optional): デバッグモード. Defaults to False
        data (Path, optional): データディレクトリ. Defaults to HOME_DIR.
        webcall (bool, optional): WebAPIからの呼出しの場合はTrue. setHandlerを削除します。. Defaults to False.
        appid (str, optional): アプリケーションID. Defaults to version.__appid__.

    Returns:
        logger (logging.Logger): ロガー
        config (dict): 設定
    """
    data = Path(data) if data is not None else HOME_DIR
    log_conf_path = Path(f"logconf_{mode}.yml")
    log_name = mode
    if not log_conf_path.exists():
        log_conf_path = Path(f"logconf_{ver.__appid__}.yml")
        log_name = ver.__appid__
    if not log_conf_path.exists():
        log_conf_path = Path(ver.__file__).parent / f"logconf_{mode}.yml"
        log_name = mode
    if not log_conf_path.exists():
        log_conf_path = Path(ver.__file__).parent / f"logconf_{ver.__appid__}.yml"
        log_name = mode
    if not log_conf_path.exists():
        log_conf_path = Path(version.__file__).parent / f"logconf_{mode}.yml"
        log_name = mode
    if not log_conf_path.exists():
        log_conf_path = Path(version.__file__).parent / f"logconf_{ver.__appid__}.yml"
        log_name = mode
    log_config = load_yml(log_conf_path)
    std_key = None
    set_common_value('webcall', webcall)
    for k, h in log_config['handlers'].items():
        if 'filename' in h:
            h['filename'] = data / h['filename']
            mkdirs(h['filename'].parent)
        if 'class' in h:
            hc = module.class_for_name(h['class'])
            if issubclass(hc, logging.StreamHandler) and not issubclass(hc, logging.FileHandler):
                std_key = k
    if webcall and std_key is not None:
        for k, l in log_config['loggers'].items():
            if 'handlers' in l and std_key in l['handlers']:
                l['handlers'].remove(std_key)
    if 'loggers' not in log_config:
        raise BaseException(f"Loggers not found at log_conf_path={log_conf_path}")
    if log_name not in log_config['loggers']:
        if ver.__appid__ not in log_config['loggers']:
            raise BaseException(f"Loggers not found.({ver.__appid__}) at log_conf_path={log_conf_path}")
        log_name = ver.__appid__
    log_config['disable_existing_loggers'] = False # これを入れないとdictConfigで既存のロガーが無効になる
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(log_name)
    set_debug(logger, debug)
    return logger, {}

def set_debug(logger:logging.Logger, debug:bool=False) -> None:
    """
    ロガーのデバッグモードを設定します。

    Args:
        logger (logging.Logger): ロガー
        debug (bool, optional): デバッグモード. Defaults to False.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.info("Use debug mode logging.")
    else:
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            handler.setLevel(logging.INFO)

def default_json_enc(o) -> Any:
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.float32):
        return float(o)
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.int32):
        return int(o)
    if isinstance(o, np.intc):
        return int(o)
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, tempfile._TemporaryFileWrapper):
        return str(o)
    if isinstance(o, datetime.datetime):
        if o.tzinfo is datetime.timezone.utc:
            return o.strftime('%Y-%m-%dT%H:%M:%S')
        return o.strftime('%Y-%m-%dT%H:%M:%S%z')
    if isinstance(o, feature.Feature):
        return 'object'
    raise TypeError(f"Type {type(o)} not serializable")

def saveopt(opt:dict, opt_path:Path, webmode:bool=False) -> None:
    """
    コマンドラインオプションをJSON形式でファイルに保存します。

    Args:
        opt (dict): コマンドラインオプション
        opt_path (Path): 保存先のファイルパス
        webmode (bool, optional): Webモードからの呼び出し. Defaults to False.
    """
    if opt_path is None:
        return
    if webmode and 'mode' in opt and 'cmd' in opt:
        refs = options.Options.getInstance().get_cmd_choices(opt['mode'], opt['cmd'])
        lopts = loadopt(opt_path)
        for r in refs:
            if 'opt' not in r or 'web' not in r:
                continue
            if r['web'] in ['mask', 'readonly']:
                k = r['opt']
                d = r['default'] if 'default' in r else None
                opt[k] = d if k not in lopts else lopts.get(k, d)
    def _w(f):
        json.dump(opt, f, indent=4, default=default_json_enc)
    save_file(opt_path, _w)

def saveuser(user_data:dict, user_path:Path) -> None:
    """
    ユーザーファイルを保存します。

    Args:
        user_data (dict): ユーザーファイル
        user_path (Path): 保存先のファイルパス
    """
    saveopt(user_data, user_path)

def loadopt(opt_path:str, webmode:bool=False) -> dict:
    """
    JSON形式のファイルからコマンドラインオプションを読み込みます。

    Args:
        opt_path (str): 読み込むファイルパス
        webmode (bool, optional): Webモードからの呼び出し. Defaults to False

    Returns:
        dict: 読み込んだコマンドラインオプション
    """
    if opt_path is None or not Path(opt_path).exists():
        return dict()
    with open(opt_path) as f:
        opt = json.load(f)
        if webmode:
            if 'mode' not in opt or 'cmd' not in opt:
                return opt
            refs = options.Options.getInstance().get_cmd_choices(opt['mode'], opt['cmd'], webmode)
            for r in refs:
                if 'opt' not in r:
                    continue
                if 'web' in r and r['web'] == 'mask':
                    opt[r['opt']] = '********'
        return opt

def loaduser(user_path:str) -> dict:
    """
    JSON形式のユーザーファイルを読み込みます。

    Args:
        user_path (str): ユーザーファイルのパス

    Returns:
        dict: 読み込んだユーザーファイル
    """
    return loadopt(user_path)

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False) -> any:
    """
    コマンドラインオプションから指定されたキーの値を取得します。

    Args:
        opt (dict): 読み込んだコマンドラインオプション
        key (str): キー
        preval (Any, optional): 引数で指定されたコマンドラインオプション. Defaults to None.
        defval (Any, optional): デフォルト値. Defaults to None.
        withset (bool, optional): optに引数のコマンドラインオプションを設定するかどうか. Defaults to False.

    Returns:
        Any: 取得した値
    """
    if preval is not None:
        v = preval
        if isinstance(preval, dict):
            v = preval.get(key, None)
        if (v is None or not v) and key in opt:
            v = opt[key]
        elif (v is None or not v) and v != 0:
            v = defval
        if withset:
            opt[key] = v
        return v
    if key in opt:
        return opt[key]
    else:
        if withset:
            opt[key] = defval
        return defval

def safe_fname(fname:str) -> str:
    """
    ファイル名に使えない文字を置換します。

    Args:
        fname (str): ファイル名

    Returns:
        str: 置換後のファイル名
    """
    fname = re.sub('[_]', '-_-',str(fname))
    return re.sub('[\s:;\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]', '_',str(fname))

def check_fname(fname:str) -> bool:
    """
    ファイル名に使えない文字が含まれているかどうかをチェックします。

    Args:
        fname (str): ファイル名

    Returns:
        bool: Trueの場合は使えない文字が含まれている
    """
    return re.search('[\s:;\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]',str(fname)) is not None

def mkdirs(dir_path:Path):
    """
    ディレクトリを中間パスも含めて作成します。

    Args:
        dir_path (Path): 作成するディレクトリのパス

    Returns:
        Path: 作成したディレクトリのパス
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def rmdirs(dir_path:Path, ignore_errors:bool=True):
    """
    ディレクトリをサブディレクトリ含めて削除します。

    Args:
        dir_path (Path): 削除するディレクトリのパス
    """
    shutil.rmtree(dir_path, ignore_errors=ignore_errors)

def random_string(size:int=16, chars=string.ascii_uppercase + string.digits) -> str:
    """
    ランダムな文字列を生成します。

    Args:
        size (int, optional): 文字列の長さ. Defaults to 16.
        chars ([type], optional): 使用する文字. Defaults to string.ascii_uppercase + string.digits.

    Returns:
        str: 生成された文字列
    """
    return ''.join(random.choices(chars, k=size))

def print_format(data:dict, format:bool, tm:float, output_json:str=None, output_json_append:bool=False, stdout:bool=True,
                 tablefmt:str='github', pf:List[Dict[str, float]]=[]):
    """
    データを指定されたフォーマットで出力します。

    Args:
        data (dict): 出力するデータ
        format (bool): フォーマットするかどうか
        tm (float): 処理時間
        output_json (str, optional): JSON形式で出力するファイルパス. Defaults to None.
        output_json_append (bool, optional): JSON形式で出力するファイルパス. Defaults to False.
        stdout (bool, optional): 標準出力に出力するかどうか. Defaults to True.
        tablefmt (str, optional): テーブルのフォーマット. Defaults to 'github'.
        pf (List[Dict[str, float]], optional): パフォーマンス情報. Defaults to [].
    Returns:
        str: 生成された文字列
    """
    is_data_dict = isinstance(data, dict)
    in_data_success = is_data_dict and 'success' in data
    is_success_dict = in_data_success and isinstance(data['success'], dict)
    is_data_list = isinstance(data, list)
    if is_success_dict and "performance" in data["success"] and isinstance(data["success"]["performance"], list) and pf is not None:
        data["success"]["performance"] += pf
    txt = ''
    if format:
        if is_success_dict:
            _data = data['success']['data'] if 'data' in data['success'] else data['success']
            if isinstance(_data, list):
                txt = tabulate(_data, headers='keys', tablefmt=tablefmt)
            elif isinstance(_data, dict):
                txt = tabulate([_data], headers='keys', tablefmt=tablefmt)
            else:
                txt = str(_data)
        elif is_data_list:
            txt = tabulate(data, headers='keys', tablefmt=tablefmt)
        else:
            txt = tabulate([data], headers='keys', tablefmt=tablefmt)
        if stdout:
            try:
                print(txt)
                print(f"{time.perf_counter() - tm:.03f}s.")
            except BrokenPipeError:
                pass
    else:
        if is_success_dict:
            if "performance" not in data["success"]:
                data["success"]["performance"] = []
            performance = data["success"]["performance"]
            performance.append(dict(key="app_proc", val=f"{time.perf_counter() - tm:.03f}s"))
        try:
            if is_data_dict:
                txt = json.dumps(data, default=default_json_enc, ensure_ascii=False)
            else:
                txt = data
        except:
            txt = data
        if stdout:
            try:
                print(txt)
            except BrokenPipeError:
                pass
    if output_json is not None:
        try:
            def _w(f):
                json.dump(data, f, default=default_json_enc, ensure_ascii=False)
                print('', file=f)
            save_file(Path(output_json), _w, mode='a' if output_json_append else 'w')
        except Exception as e:
            pass
    return txt

def to_str(o, slise=-1):
    ret = ""
    if type(o) == dict:
        ret = json.dumps(o, default=default_json_enc)
    elif type(o) == list and len(o) > 0 and type(o[0]) == dict:
        ret = json.dumps(o, default=default_json_enc)
    else:
        ret = str(o)
    if slise < 0:
        return ret
    ret = ret[0:slise]
    return len(ret) > 100 and ret + '...' or ret

def download_file(url:str, save_path:Path) -> Path:
    """
    ファイルをダウンロードします。

    Args:
        url (str): ダウンロードするファイルのURL
        save_path (Path): 保存先のファイルパス

    Returns:
        Path: 保存したファイルのパス
    """
    r = requests.get(url, stream=True)
    def _w(f):
        f.write(r.content)
    save_file(Path(save_path), _w)
    return save_path

def cmd(cmd:str, logger:logging.Logger, slise:int=100, newenv:Dict=None) -> Tuple[int, str, str]:
    """
    コマンドを実行します。

    Args:
        cmd (str): 実行するコマンド
        logger (logging.Logger): ロガー
        slise (int, optional): 出力文字列の最大長. Defaults to 100
        newenv (dict): 上書きしたい環境変数

    Returns:
        Tuple[int, str, str]: コマンドの戻り値と出力とコマンド
    """
    env = os.environ.copy()
    if newenv is not None:
        for k, v in newenv.items():
            env[k] = v
    if logger.level == logging.DEBUG:
        logger.debug(f"cmd={cmd}, newenv={newenv}")
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    output = None
    while proc.returncode is None:
        out = proc.stdout.readline()
        if out == b'' and proc.poll() is not None:
            break
        for enc in ['utf-8', 'cp932', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                output = out.decode(enc).rstrip()
                #if platform.system() == 'Windows' or strip:
                #    output = output.rstrip()
                if logger.level == logging.DEBUG:
                    output_str = to_str(output, slise=slise)
                    logger.debug(f"output: {output_str}")
                break
            except UnicodeDecodeError:
                pass
    #proc.stdout.read()

    return proc.returncode, output, cmd

def hash_password(password:str, hash:str) -> str:
    """
    パスワードをハッシュ化します。

    Args:
        password (str): パスワード
        hash (str): ハッシュアルゴリズム

    Returns:
        str: ハッシュ化されたパスワード
    """
    h = hashlib.new(hash)
    h.update(password.encode('utf-8'))
    passwd = h.hexdigest()
    return passwd

def encrypt(message:str, password:str) -> str:
    """
    メッセージを暗号化します。

    Args:
        message (str): メッセージ
        password (str): パスワード

    Returns:
        str: 暗号化されたメッセージ
    """
    pass32 = convert.str2b64str(hash_password(password, 'md5'))
    fernet = Fernet(bytes(pass32, encoding='utf-8'))
    enc_message = fernet.encrypt(bytes(message, encoding='utf-8'))
    return convert.bytes2b64str(enc_message)

def decrypt(enc_message:str, password:str) -> str:
    """
    メッセージを復号化します。

    Args:
        enc_message (str): 暗号化されたメッセージ
        password (str): パスワード

    Returns:
        str: 復号化されたメッセージ。失敗した場合はNone
    """
    try:
        pass32 = convert.str2b64str(hash_password(password, 'md5'))
        fernet = Fernet(bytes(pass32, encoding='utf-8'))
        enc_message = convert.b64str2bytes(enc_message)
        message = fernet.decrypt(enc_message)
        return message.decode(encoding='utf-8')
    except:
        return None

def chopdq(target:str):
    """"
    "で囲まれた文字列を取り除きます。
    targetにNoneが指定された場合はNoneを返します。

    Args:
        target (str): 対象文字列
    
    Returns:
        str: 取り除かれた文字列
    """
    if target is None:
        return None
    if not isinstance(target, str):
        return target
    return target[1:-1] if target.startswith('"') and target.endswith('"') else target

def is_japan() -> bool:
    """
    日本語環境かどうかを判定します

    Returns:
        bool: 日本語環境ならTrue、そうでなければFalse
    """
    language, _ = locale.getlocale()
    is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
    return is_japan

def is_event_loop_running() -> bool:
    """
    イベントループが実行中かどうかを取得します。

    Returns:
        bool: イベントループが実行中の場合はTrue
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False

def exec_sync(apprun, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]) -> Tuple[int, Dict[str, Any], Any]:
    """"
    指定された関数が非同期関数であっても同期的に実行します。

    Args:
        apprun (function): 関数
        logger (logging.Logger): ロガー
        args (argparse.Namespace): コマンドライン引数
        tm (float): 処理時間
        pf (List[Dict[str, float]]): パフォーマンス情報

    Returns:
        Tuple[int, Dict[str, Any], Any]: 戻り値のタプル。0は成功、1は失敗、2はキャンセル
    """
    if inspect.iscoroutinefunction(apprun):
        if is_event_loop_running():
            def _run(apprun, ctx, logger, args, tm, pf):
                ctx.append(asyncio.run(apprun(logger, args, tm, pf)))
            ctx = []
            th = threading.Thread(target=_run, args=(apprun, ctx, logger, args, tm, pf))
            th.start()
            th.join()
            result = ctx[0] if ctx else None
            return result
        return asyncio.run(apprun(logger, args, tm, pf))
    return apprun(logger, args, tm, pf)

def get_tzoffset_str() -> str:
    """
    タイムゾーンのオフセットを取得します

    Returns:
        str: タイムゾーンのオフセット
    """
    # 現在のタイムゾーンのオフセットを取得
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_local = now_utc.astimezone()
    offset = now_local.utcoffset()
    # timedelta オブジェクトから '+/-HH:MM' 形式の文字列を生成
    total_seconds = int(offset.total_seconds())
    hours = abs(total_seconds) // 3600
    minutes = (abs(total_seconds) % 3600) // 60
    sign = "+" if total_seconds >= 0 else "-"

    return f"{sign}{hours:02}:{minutes:02}"