from cmdbox.app import common, client, feature
from cmdbox.app.commons import redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import datetime
import logging


class ServerTime(feature.Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "server"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'time'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type=Options.T_STR, default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            description_ja="サーバー側の現在時刻を表示します。",
            description_en="Displays the current time at the server side.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None,
                        description_ja="Redisサーバーのサービスホストを指定します。",
                        description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None,
                        description_ja="Redisサーバーのサービスポートを指定します。",
                        description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None,
                        description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                        description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None,
                        description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                        description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="timedelta", type=Options.T_INT, default=9, required=False, multi=False, hide=False, choice=None,
                        description_ja="時差の時間数を指定します。",
                        description_en="Specify the number of hours of time difference."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                        description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                        description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                        description_ja="Redisサーバーに再接続までの秒数を指定します。",
                        description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                        description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                        description_en="Specify the maximum waiting time until the server responds."),
            ])

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'server_time'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
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
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [str(args.timedelta)],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

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
        td = 9 if msg[2] == None else int(msg[2])
        tz = datetime.timezone(datetime.timedelta(hours=td))
        dt = datetime.datetime.now(tz)
        ret = dict(success=dict(data=dt.strftime('%Y-%m-%d %H:%M:%S')))
        redis_cli.rpush(msg[1], ret)
        return self.RESP_SUCCESS

    def edgerun(self, opt, tool, logger, timeout, prevres = None):
        """
        この機能のエッジ側の実行を行います

        Args:
            opt (Dict[str, Any]): オプション
            tool (edge.Tool): 通知関数などedge側のUI操作を行うためのクラス
            logger (logging.Logger): ロガー
            timeout (int): タイムアウト時間
            prevres (Any): 前コマンドの結果。pipeline実行の実行結果を参照する時に使用します。

        Yields:
            Tuple[int, Dict[str, Any]]: 終了コード, 結果
        """
        status, res = tool.exec_cmd(opt, logger, timeout, prevres)
        tool.notify(res)
        yield 1, res
