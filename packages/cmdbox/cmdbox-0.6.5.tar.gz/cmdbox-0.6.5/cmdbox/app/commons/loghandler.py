from rich.console import Console
from rich import highlighter
from rich.theme import Theme
import re
import logging
import logging.handlers
import pickle
import socketserver
import struct
import socket


class Colors:
    S = "\033["
    D = ";"
    E = "m"
    # https://pkg.go.dev/github.com/whitedevops/colors
    ResetAll = 0

    Bold       = 1
    Dim        = 2
    Underlined = 4
    Blink      = 5
    Reverse    = 7
    Hidden     = 8

    ResetBold       = 21
    ResetDim        = 22
    ResetUnderlined = 24
    ResetBlink      = 25
    ResetReverse    = 27
    ResetHidden     = 28

    Default      = 39
    Black        = 30
    Red          = 31
    Green        = 32
    Yellow       = 33
    Blue         = 34
    Magenta      = 35
    Cyan         = 36
    LightGray    = 37
    DarkGray     = 90
    LightRed     = 91
    LightGreen   = 92
    LightYellow  = 93
    LightBlue    = 94
    LightMagenta = 95
    LightCyan    = 96
    White        = 97

    BackgroundDefault      = 49
    BackgroundBlack        = 40
    BackgroundRed          = 41
    BackgroundGreen        = 42
    BackgroundYellow       = 43
    BackgroundBlue         = 44
    BackgroundMagenta      = 45
    BackgroundCyan         = 46
    BackgroundLightGray    = 47
    BackgroundDarkGray     = 100
    BackgroundLightRed     = 101
    BackgroundLightGreen   = 102
    BackgroundLightYellow  = 103
    BackgroundLightBlue    = 104
    BackgroundLightMagenta = 105
    BackgroundLightCyan    = 106
    BackgroundWhite        = 107

    _colorize_suffix = S + str(ResetAll) + E

    product_word = re.compile(r"CMDBOX|IINFER|USOUND|GAIAN|GAIC|WITSHAPE", re.IGNORECASE)
    success_word = re.compile(r"SUCCESS|OK|PASSED|DONE|COMPLETE|START|FINISH|OPEN|CONNECTED|ALLOW|EXEC", re.IGNORECASE)
    warning_word = re.compile(r"WARNING|WARN|CAUTION|NOTICE|STOP|DISCONNECTED|DENY", re.IGNORECASE)
    error_word = re.compile(r"ERROR|ALERT|CRITICAL|FATAL|ABORT|FAILED", re.IGNORECASE)

def colorize(s:str, *colors:int) -> str:
    return Colors.S + Colors.D.join(map(str, [Colors.ResetAll]+list(colors))) + Colors.E + s + Colors._colorize_suffix

def colorize_msg(msg) -> str:
    msg = Colors.success_word.sub(colorize(r"\g<0>", Colors.Green), msg)
    msg = Colors.warning_word.sub(colorize(r"\g<0>", Colors.Yellow), msg)
    msg = Colors.error_word.sub(colorize(r"\g<0>", Colors.Red), msg)
    msg = Colors.product_word.sub(colorize(r"\g<0>", Colors.LightBlue), msg)
    return msg

level_mapping = {
    logging.DEBUG:   f"{colorize('DEBUG', Colors.Bold, Colors.Cyan)}",
    logging.INFO:    f"{colorize('INFO', Colors.Bold, Colors.Green)} ",
    logging.WARNING: f"{colorize('WARN', Colors.Bold, Colors.Yellow)} ",
    logging.ERROR:   f"{colorize('ERROR', Colors.Bold, Colors.Red)}",
    logging.CRITICAL:f"{colorize('FATAL', Colors.Bold, Colors.LightGray, Colors.BackgroundRed)}"}

level_mapping_nc = {
    logging.DEBUG:   f"DEBUG",
    logging.INFO:    f"INFO ",
    logging.WARNING: f"WARN ",
    logging.ERROR:   f"ERROR",
    logging.CRITICAL:f"FATAL"}

theme=Theme({
    "repr.log_debug": "bold cyan",
    "repr.log_info": "bold green",
    "repr.log_warn": "bold Yellow",
    "repr.log_error": "bold red",
    "repr.log_fatal": "bold red reverse",
    "repr.log_product": "dodger_blue2 reverse",
    "repr.log_success": "green",})

class LogLevelHighlighter(highlighter.ReprHighlighter):
    """
    ログメッセージのログレベルをハイライトします。
    """
    def __init__(self):
        #self.highlights = []
        self.highlights.append(r"(?P<log_debug>DEBUG|EXEC)")
        self.highlights.append(r"(?P<log_info>INFO)")
        self.highlights.append(r"(?P<log_warn>WARN|WARNING|WARN|CAUTION|NOTICE|STOP|DISCONNECTED|DENY)")
        self.highlights.append(r"(?P<log_error>ERROR|ALERT|ABORT|FAILED)")
        self.highlights.append(r"(?P<log_fatal>FATAL|CRITICAL)")
        self.highlights.append(r"(?P<log_product>CMDBOX|IINFER|USOUND|GAIAN|GAIC|WITSHAPE)")
        self.highlights.append(r"(?P<log_success>SUCCESS|OK|PASSED|DONE|COMPLETE|START|FINISH|OPEN|CONNECTED|ALLOW)")
        self.highlights = [re.compile(h, re.IGNORECASE) for h in self.highlights]

class ColorfulStreamHandler(logging.StreamHandler):
    """
    コンソールにカラフルなログメッセージを出力します。
    """
    console = Console(soft_wrap=True, height=True, highlighter=LogLevelHighlighter(), theme=theme)

    def emit(self, record: logging.LogRecord) -> None:
        #record.levelname = level_mapping[record.levelno]
        #record.asctime = colorize(record.asctime, Colors.Bold)
        #record.msg = colorize_msg(record.msg)
        #super().emit(record)
        record.levelname = level_mapping_nc[record.levelno]
        record.msg = self.format(record)
        try:
            self.console.print(record.msg)
        except Exception as e:
            self.console.print(record.msg, highlight=False)

class TimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = level_mapping_nc[record.levelno]
        super().emit(record)

class SocketHandler(logging.handlers.SocketHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = level_mapping_nc[record.levelno]
        super().emit(record)

class LogRecordRequestHandler(socketserver.StreamRequestHandler):
    """
    ログリクエストを処理するためのハンドラ
    """
    def setup(self):
        super().setup()
        from cmdbox.app import common
        common.set_debug(self._getLogger(), LogRecordTCPServer.debug)

    def _getLogger(self):
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = self.logname
        return logging.getLogger(name)

    def handle(self):
        """
        ログリクエストを処理します。
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)
    
    def handleLogRecord(self, record):
        logger = self._getLogger()
        logger.handle(record)

class LogRecordTCPServer(socketserver.ThreadingTCPServer):
    """
    ログレコードを受信するためのTCPサーバー。
    """
    # 停止後すぐにサーバーを再起動できるようにする
    allow_reuse_address = True

    def __init__(self, logname, host='localhost', port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordRequestHandler, debug=False):
        """
        コンストラクタ

        Args:
            logname (str): ログ名
            host (str): ホスト名
            port (int): ポート番号
            handler (socketserver.RequestHandler): リクエストハンドラ
            debug (bool): デバッグモード
        """
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler, bind_and_activate=False)
        self.allow_reuse_address = False
        self.allow_reuse_port = False
        self.request_queue_size = 15
        self.abort = 0
        self.timeout = 1
        self.logname = logname
        self.handler = handler
        LogRecordTCPServer.debug = debug

    def serve_until_stopped(self):
        import select
        abort = 0
        try:
            self.server_bind()
            self.server_activate()
        except:
            # すでにlogsvが起動中の場合は待機しない
            self.server_close()
            abort = 1
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort
