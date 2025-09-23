from cmdbox import version
from cmdbox.app import common, edge_tool
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.web import Web
from fastapi import FastAPI
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import os


class Feature(object):
    USE_REDIS_FALSE:int = -1
    USE_REDIS_MEIGHT:int = 0
    USE_REDIS_TRUE:int = 1
    RESP_SUCCESS:int = 0
    RESP_WARN:int = 1
    RESP_ERROR:int = 2
    DEFAULT_CAPTURE_MAXSIZE:int = 1024 * 1024 * 10
    default_host:str = os.environ.get('REDIS_HOST', 'localhost')
    default_port:int = int(os.environ.get('REDIS_PORT', '6379'))
    default_pass:str = os.environ.get('REDIS_PASSWORD', 'password')
    default_svname:str = os.environ.get('SVNAME', 'server')

    def __init__(self, appcls, ver):
        self.ver = ver
        self.appcls = appcls
        self.default_svname:str = ver.__appid__
        self.default_data:Path = os.environ.get('DATA_DIR', common.HOME_DIR / f".{self.ver.__appid__}")

    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        raise NotImplementedError

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        raise NotImplementedError

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        raise NotImplementedError

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return None

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        raise NotImplementedError

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        raise NotImplementedError

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        raise NotImplementedError

    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        """
        この機能のエッジ側の実行を行います

        Args:
            opt (Dict[str, Any]): オプション
            tool (edge_tool.Tool): 通知関数などedge側のUI操作を行うためのクラス
            logger (logging.Logger): ロガー
            timeout (int): タイムアウト時間
            prevres (Any): 前コマンドの結果。pipeline実行の実行結果を参照する時に使用します。

        Yields:
            Tuple[int, Dict[str, Any]]: 終了コード, 結果
        """
        status, res = tool.exec_cmd(opt, logger, timeout, prevres)
        yield status, res

    def audited_by(self, logger:logging.Logger, args:argparse.Namespace) -> bool:
        """
        この機能が監査ログを記録する対象かどうかを返します

        Returns:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            bool: 監査ログを記録する場合はTrue
        """
        if hasattr(self, 'client_only') and self.client_only:
            return False
        return True

class OneshotEdgeFeature(Feature):
    """
    一度だけ実行するエッジ機能の基底クラス
    """
    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        status, res = tool.exec_cmd(opt, logger, timeout, prevres)
        yield 1, res

class OneshotNotifyEdgeFeature(OneshotEdgeFeature):
    """
    実行結果の通知を行うエッジ機能の基底クラス
    """
    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        status, res = next(super().edgerun(opt, tool, logger, timeout, prevres))
        tool.notify(res)
        yield status, res

class ResultEdgeFeature(Feature):
    """
    実行結果をWebブラウザで表示するエッジ機能の基底クラス
    """
    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        status, res = next(super().edgerun(opt, tool, logger, timeout, prevres))
        if status == 0:
            status, res = tool.pub_result(opt['title'], res, timeout)
        else:
            tool.notify(res)
        yield status, res

class OneshotResultEdgeFeature(ResultEdgeFeature):
    """
    一度だけ実行結果をWebブラウザで表示するエッジ機能の基底クラス
    """
    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        status, res = next(super().edgerun(opt, tool, logger, timeout, prevres))
        yield 1, res

class UnsupportEdgeFeature(Feature):
    """
    サポートされていないエッジ機能の基底クラス
    """
    def edgerun(self, opt:Dict[str, Any], tool:edge_tool.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
        res = dict(warn=f'Unsupported edgerun. mode="{opt["mode"]}", cmd="{opt["cmd"]}"')
        tool.notify(res)
        yield 1, res

class WebFeature(object):
    USE_REDIS_FALSE:int = Feature.USE_REDIS_FALSE
    USE_REDIS_MEIGHT:int = Feature.USE_REDIS_MEIGHT
    USE_REDIS_TRUE:int = Feature.USE_REDIS_TRUE
    DEFAULT_CAPTURE_MAXSIZE:int = Feature.DEFAULT_CAPTURE_MAXSIZE
    DEFAULT_401_MESSAGE:str = "Unauthorized operation. Please sign in again as an authorized user."

    def __init__(self, appcls=None, ver=version):
        self.ver = ver
        self.appcls = appcls

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        raise NotImplementedError

    def filemenu(self, web:Web) -> Dict[str, Any]:
        """
        ファイルメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: fileメニュー情報
        
        Notes:
            以下は返されるJSONのサンプル::
            
                {
                    'filer': {
                        'html': 'Filer',
                        'href': 'filer',
                        'target': '_blank',
                        'css_class': 'dropdown-item'
                        'onclick': 'alert("filer")'
                    }
                }
        """
        return dict()

    def toolmenu(self, web:Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: ツールメニュー情報
        
        Notes:
            以下は返されるJSONのサンプル::

                {
                    'filer': {
                        'html': 'Filer',
                        'href': 'filer',
                        'target': '_blank',
                        'css_class': 'dropdown-item',
                        'onclick': 'alert("filer")'
                    }
                }
        """
        return dict()

    def viewmenu(self, web:Web) -> Dict[str, Any]:
        """
        Viewメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: Viewメニュー情報
        
        Notes:
            以下は返されるJSONのサンプル::

                {
                    'filer': {
                        'html': 'Filer',
                        'href': 'filer',
                        'target': '_blank',
                        'css_class': 'dropdown-item',
                        'onclick': 'alert("filer")'
                    }
                }
        """
        return dict()

    def aboutmenu(self, web:Web) -> Dict[str, Any]:
        """
        Aboutメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: Aboutメニュー情報
        
        Notes:
            以下は返されるJSONのサンプル::

                {
                    'filer': {
                        'html': 'Filer',
                        'href': 'filer',
                        'target': '_blank',
                        'css_class': 'dropdown-item',
                        'onclick': 'alert("filer")'
                    }
                }
        """
        return dict()
