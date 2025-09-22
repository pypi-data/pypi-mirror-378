import signal
import threading
import time
from abc import ABC, abstractmethod

from kaq_quant_common.utils.logger_utils import get_logger


# 通用的抽象类，包装一层ws操作
class WsWrapper(ABC):
    def __init__(self):
        # 初始化
        self.init()

    # 初始化
    def init(self):
        # 执行初始化
        self._do_init()

    @abstractmethod
    def _do_init(self):
        pass

    # 开始，需要确保这个方法在op线程执行，执行这个方法会阻塞当前线程！
    def start(self):
        # 全局退出事件，用于传递终止信号
        exit_event = threading.Event()

        logger = get_logger(self)

        #
        def handle_terminate_signal(signum, frame):
            """信号处理函数：捕获终止信号并触发退出事件"""
            logger.info(f"收到终止信号 {signum}")
            exit_event.set()
            # 优雅地关闭
            self.close()

        # 监听信号
        # SIGTERM：Dagster通常发送此信号进行终止
        # SIGINT：对应Ctrl+C，用于本地测试
        signal.signal(signal.SIGTERM, handle_terminate_signal)
        signal.signal(signal.SIGINT, handle_terminate_signal)

        self._do_start()

        # 监听退出事件
        while not exit_event.is_set():
            time.sleep(1)

        logger.warning("WsWrapper 线程退出")

    @abstractmethod
    def _do_start(self):
        pass

    # 断开连接，主动关闭
    def close(self):
        self._do_close()

    @abstractmethod
    def _do_close(self):
        pass
