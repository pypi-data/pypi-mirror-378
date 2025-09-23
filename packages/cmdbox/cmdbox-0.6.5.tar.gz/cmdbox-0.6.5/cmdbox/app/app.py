from cmdbox import version
from cmdbox.app import common, feature, options
from pathlib import Path
from typing import List
import argparse
import argcomplete
import logging
import time
import threading
import sys


def main(args_list:list=None, webcall:bool=False):
    app = CmdBoxApp.getInstance(appcls=CmdBoxApp, ver=version)
    return app.main(args_list, webcall=webcall)[0]

class CmdBoxApp:
    _instance = None
    @staticmethod
    def getInstance(appcls=None, ver=version, cli_features_packages:List[str]=None, cli_features_prefix:List[str]=None):
        if CmdBoxApp._instance is None:
            _self = appcls.__new__(appcls)
            _self.__init__(appcls=appcls, ver=ver, cli_features_packages=cli_features_packages, cli_features_prefix=cli_features_prefix)
            CmdBoxApp._instance = _self
        return CmdBoxApp._instance

    def __init__(self, appcls=None, ver=version, cli_features_packages:List[str]=None, cli_features_prefix:List[str]=None):
        """
        コンストラクタ

        Args:
            ver (version, optional): バージョンモジュール. Defaults to version.
            cli_package_name (str, optional): プラグインのパッケージ名. Defaults to None.
            cli_features_prefix (List[str], optional): プラグインのパッケージのモジュール名のプレフィックス. Defaults to None.
        """
        self.appcls = self.__class__ if appcls is None else appcls
        self.ver = ver
        self.options = options.Options.getInstance(self.appcls, self.ver)
        self.cli_features_packages = cli_features_packages
        self.cli_features_prefix = cli_features_prefix

    def main(self, args_list:list=None, file_dict:dict=dict(), webcall:bool=False):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        smaintime = time.perf_counter()
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 9:
            parser = argparse.ArgumentParser(prog=self.ver.__appid__, description=self.ver.__logo__ + '\n\n' + self.ver.__description__,
                                            formatter_class=argparse.RawDescriptionHelpFormatter, exit_on_error=False)
        else:
            parser = argparse.ArgumentParser(prog=self.ver.__appid__, description=self.ver.__logo__ + '\n\n' + self.ver.__description__,
                                            formatter_class=argparse.RawDescriptionHelpFormatter)
        if args_list is not None and '--debug' in args_list:
            self.default_logger = common.default_logger(True, ver=self.ver, webcall=webcall)
        elif sys.argv is not None and '--debug' in sys.argv:
            self.default_logger = common.default_logger(True, ver=self.ver, webcall=webcall)
        else:
            self.default_logger = common.default_logger(False, ver=self.ver, webcall=webcall)

        # プラグイン読込み
        sfeatureloadtime = time.perf_counter()
        self.options._load_features_yml(self.ver, logger=self.default_logger)
        self.options.load_features_agentrule(self.default_logger)
        self.options.load_svcmd('cmdbox.app.features.cli', prefix="cmdbox_", excludes=[], appcls=self.appcls, ver=self.ver, logger=self.default_logger,
                                isloaded=self.options.is_features_loaded('cli'))
        if self.cli_features_packages is not None:
            if self.cli_features_prefix is None:
                raise ValueError(f"cli_features_prefix is None. cli_features_packages={self.cli_features_packages}")
            if len(self.cli_features_prefix) != len(self.cli_features_packages):
                raise ValueError(f"cli_features_prefix is not match. cli_features_packages={self.cli_features_packages}, cli_features_prefix={self.cli_features_prefix}")
            for i, pn in enumerate(self.cli_features_packages):
                self.options.load_svcmd(pn, prefix=self.cli_features_prefix[i], excludes=[], appcls=self.appcls, ver=self.ver, logger=self.default_logger)
        self.options.load_features_file('cli', self.options.load_svcmd, self.appcls, self.ver, self.default_logger)
        self.options.load_features_aliases_cli(self.default_logger)
        self.options.load_features_audit(self.default_logger)
        efeatureloadtime = time.perf_counter()

        # コマンド引数の生成
        sargsparsetime = time.perf_counter()
        opts = self.options.list_options()
        for opt in opts.values():
            default = opt["default"] if opt["default"] is not None and opt["default"] != "" else None
            if opt["action"] is None:
                parser.add_argument(*opt["opts"], help=opt["help"], type=opt["type"], default=default, choices=opt["choices"])
            else:
                parser.add_argument(*opt["opts"], help=opt["help"], default=default, action=opt["action"])

        argcomplete.autocomplete(parser)
        # mainメソッドの起動時引数がある場合は、その引数を解析する
        try:
            if args_list is not None and len(args_list) > 0:
                args = parser.parse_args(args=args_list)
            else:
                args = parser.parse_args()
        except argparse.ArgumentError as e:
            msg = dict(warn=f"ArgumentError: {e}")
            common.print_format(msg, False, 0, None, False)
            return feature.Feature.RESP_WARN, msg, None
        # 起動時引数で指定されたオプションをファイルから読み込んだオプションで上書きする
        args_dict = vars(args)
        for key, val in file_dict.items():
            args_dict[key] = val
        # useoptオプションで指定されたオプションファイルを読み込む
        opt = common.loadopt(args.useopt)
        # 最終的に使用するオプションにマージする
        for key, val in args_dict.items():
            args_dict[key] = common.getopt(opt, key, preval=args_dict, withset=True)
            # オプションの型が辞書の場合は、文字列から辞書に変換する
            if opts[key]["type"] is dict:
                if isinstance(args_dict[key], list):
                    d = dict()
                    for v in args_dict[key]:
                        kv = v.split('=')
                        d[kv[0]] = kv[1]
                    args_dict[key] = d
        # featuresの初期値を適用する
        self.options.load_features_args(args_dict)
        args = argparse.Namespace(**{k:common.chopdq(v) for k,v in args_dict.items()})
        eargsparsetime = time.perf_counter()

        if args.debug_attach:
            import debugpy
            debugpy.listen(("", args.debug_attach_port))
            self.default_logger.info(f"Waiting for debugger attach on port {args.debug_attach_port}...")
            debugpy.wait_for_client()
            self.default_logger.info("Debugger attached.")

        ret = dict(success=f"Start command. {args}")
        if args.saveopt:
            if args.useopt is None:
                msg = dict(warn=f"Please specify the --useopt option.")
                common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
                return feature.Feature.RESP_WARN, msg, None
            common.saveopt(opt, args.useopt)
            ret = dict(success=f"Save options file. {args.useopt}")

        smakesampletime = time.perf_counter()
        common.mklogdir(args.data)
        #common.copy_sample(args.data, ver=self.ver)
        common.copy_sample(Path.cwd(), ver=self.ver)
        emakesampletime = time.perf_counter()

        if args.version:
            v = self.ver.__logo__ + '\n' + self.ver.__description__
            common.print_format(v, False, smaintime, None, False)
            return feature.Feature.RESP_SUCCESS, v, None

        if args.mode is None:
            msg = dict(warn=f"mode is None. Please specify the --help option.")
            common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
            return feature.Feature.RESP_WARN, msg, None

        sloggerinittime = time.perf_counter()
        logger = self.load_config(args, webcall=webcall if args.cmd != 'webcap' else True)
        try:
            eloggerinittime = time.perf_counter()
            if logger.level == logging.DEBUG:
                logger.debug(f"args.mode={args.mode}, args.cmd={args.cmd}")
                # 警告出力時にスタックを出力する
                import warnings
                def custom_warning_handler(message, category, filename, lineno, file=None, line=None):
                    import traceback
                    logger.warning(f"Warning: {message}, Category: {category}, File: {filename}, Line: {lineno}", exc_info=True)
                    traceback.print_stack()
                warnings.showwarning = custom_warning_handler

            #scmdexectime = time.perf_counter()
            feat = self.options.get_cmd_attr(args.mode, args.cmd, 'feature')
            if feat is not None and isinstance(feat, feature.Feature):
                pf = []
                pf.append(dict(key="app_featureload", val=f"{efeatureloadtime-sfeatureloadtime:.03f}s"))
                pf.append(dict(key="app_argsparse", val=f"{eargsparsetime-sargsparsetime:.03f}s"))
                pf.append(dict(key="app_makesample", val=f"{emakesampletime-smakesampletime:.03f}s"))
                pf.append(dict(key="app_loggerinit", val=f"{eloggerinittime-sloggerinittime:.03f}s"))
                self.options.audit_exec(args, logger, feat, audit_type=options.Options.AT_EVENT)
                status, ret, obj = common.exec_sync(feat.apprun, logger, args, smaintime, pf)
                return status, ret, obj
            else:
                msg = dict(warn=f"Unkown mode or cmd. mode={args.mode}, cmd={args.cmd}")
                common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
                return feature.Feature.RESP_WARN, msg, None
        finally:
            # ログの状態をwebcallから戻す
            self.load_config(args, webcall=False)

    def load_config(self, args:argparse.Namespace, webcall:bool=False) -> logging.Logger:
        """
        アプリケーションの設定を読み込みます。
        """
        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data, webcall=webcall if args.cmd != 'webcap' else True, ver=self.ver)
        if not hasattr(common, 'logsv') and hasattr(args, 'logsv') and args.logsv:
            from cmdbox.app.commons import loghandler
            common.logsv = loghandler.LogRecordTCPServer("logsv", host="localhost", port=9020, debug=args.debug)
            threading.Thread(daemon=True, target=common.logsv.serve_until_stopped, name="logsv").start()

        return logger