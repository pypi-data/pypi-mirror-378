from collections.abc import Callable

from loguru import logger
from PySide6.QtCore import QObject, QThread, Signal

class Worker(QObject):
    """
    """
    finished = Signal()

    def __init__(self, task: Callable, fin_cb: Callable, name: str = "") -> None:
        super().__init__()
        self._task = task
        self._finished = False

        if fin_cb:
            self.finished.connect(fin_cb)
        self.finished.connect(self._on_finished)

        if name == "":
            self._name = f"JZWorker-{self._task.__name__}"
        else:
            self._name = name

    def run(self) -> None:
        """
        The logic for calling non-blocking runnable task. This runs when JZWorker().start() is
        called. Getting an error here will not result in anything for the app since the thread
        in non-blocking and all of the logic related to that should be handled from elsewhere
        if needed.
        """
        logger.debug(f"Running separate task in a JZWorker thread: {self._name}")

        try:
            self._task()
        except Exception as ex:
            logger.exception(f"Error in worker thread {self._name}: {ex}")
        self.finished.emit()

    def _on_finished(self) -> None:
        self._finished = True

    def is_finished(self) -> bool:
        return self._finished


class JZWorker(QObject):
    """
    JZWorker is a class that can be used to run a non-blocking task in a separate thread without
    having to do all of the boilerplate code
    """
    finished = Signal()

    def __init__(
        self, task: Callable, fin_cb: Callable | None = None, name: str = "") -> None:
        super().__init__()
        self._thread = QThread()
        self._worker = Worker(task, fin_cb, name)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(lambda: self._thread.quit())
        #self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self.finished)
        self._thread.finished.connect(self._thread.deleteLater)
        # self._worker.finished.connect(
        #     lambda: logger.warning(f"Worker thread {self._worker._name} finished"))
        # self._thread.finished.connect(
        #     lambda: logger.error(f"Thread for worker {self._worker._name} finished"))

    def start(self) -> None:
        """
        Starts the thread and runs the task in a separate thread. This is a non-blocking call.
        """
        self._thread.start()

    def stop(self, timeout_ms: int = -1) -> None:
        """
        Stops the thread and waits for it to finish. This is a blocking call.
        """
        try:
            self._thread.quit()
        except Exception as ex:
            logger.warning(f"Error quitting thread: {ex}")

        try:
            if timeout_ms < 0:
                self._thread.wait() # wait indefinitely
            else:
                self._thread.wait(timeout_ms)
        except Exception as ex:
            logger.warning(f"Error waiting for thread to finish: {ex}")

    def is_finished(self) -> bool:
        """
        Returns True if the thread is finished, False otherwise
        """
        return self._worker.is_finished()
