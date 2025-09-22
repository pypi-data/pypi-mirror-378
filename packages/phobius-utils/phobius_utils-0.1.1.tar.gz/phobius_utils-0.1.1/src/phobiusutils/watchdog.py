import threading
import time
from datetime import datetime
import queue
import sys
from pympler import asizeof

#
class Watchdog:
    _log_buffer = queue.Queue()
    _keep_watching = True
    _watch_lock = threading.Lock()
    _watch_list = []
    #
    _LOG_FILE = "WATCHDOG.LOG"
    _TIME_WATCH = 2  # seconds

    class _Entry:
        def __init__(self, name, parent_name, type,tracked,module):
            self.name = name
            self.type = type
            self.parent_name = parent_name
            self.tracked = tracked
            self.module = module

    # MANAGER
    @staticmethod
    def start():
        """
        Start the WatchDog monitoring process.

        If the WatchDog is already running (_keep_watching == True), this method does nothing.

        Otherwise, it:
        - Clears all pending log messages in the internal queue.
        - Clears the list of watched entries (_watch_list).
        - Starts two worker threads:
            - _monitor_worker: responsible for monitoring the watched entries.
            - _log_worker: responsible for processing and outputting log messages.
        """
        if Watchdog._keep_watching:
            return
        Watchdog._keep_watching = True
        Watchdog._watch_list = []
        Watchdog._log_buffer = queue.Queue()
        # Start the monitoring thread
        threading.Thread(target=Watchdog._monitor_worker, daemon=True).start()
        # Start the logging thread
        threading.Thread(target=Watchdog._log_worker, daemon=True).start()

    @staticmethod
    def stop():
        """
        Stop the WatchDog monitoring process.

        If the WatchDog is not running (_keep_watching == False), this method does nothing.

        Otherwise, it:
        - Clears all pending log messages in the internal queue.
        - Clears the list of watched entries (_watch_list).
        - (Thường sẽ đặt _keep_watching = False để dừng các worker thread, nếu có.)
        """
        if not Watchdog._keep_watching:
            return
        Watchdog._keep_watching = False
        Watchdog._watch_list = []
        Watchdog._log_buffer = queue.Queue()

    @staticmethod
    def watch(name: str, tracked, parent_name: str = "unknown"):
        """
        Register an object to be monitored by the WatchDog.

        Parameters:
        - name (str): The unique name of the object being tracked.
        - tracked (Any): The actual object to monitor (e.g. list, queue, class instance, thread, etc.).
        - parent_name (str, optional): The logical group or owner of the object. Defaults to "unknown".

        This method automatically:
        - Calls `WatchDog.start()` to ensure the monitoring system is running.
        - Appends a new entry (with name, tracked object, and parent_name) to the internal _watch_list
        so it can be monitored for size, status, or growth over time.
        """
        Watchdog.start()
        with Watchdog._watch_lock:
            Watchdog._watch_list.append(
                Watchdog._Entry(
                    name=name,
                    type=type(tracked).__name__,
                    parent_name=parent_name,
                    tracked=tracked,
                    module=type(tracked).__module__
                )
            )
    @staticmethod
    def get_all_log() -> list:
        """
        Get all log entries from the internal log buffer.

        This method retrieves and returns all log messages currently stored in the internal
        _log_buffer queue. After calling this method, the buffer will be empty.

        Returns:
            List[str]: A list of log messages in the order they were logged.
        """
        items = []
        while True:
            try:
                items.append(Watchdog._log_buffer.get_nowait())
            except queue.Empty:
                break
        return items

    @staticmethod
    def unwatch(name: str):
        """
        Remove a watched entry from the WatchDog by its name.

        Parameters:
            name (str): The name of the watched object to remove.

        This method searches the internal _watch_list for an entry matching the given name
        and removes it, stopping further monitoring of that object.
        If the name does not exist, the method silently does nothing.
        """
        with Watchdog._watch_lock:
            Watchdog._watch_list = [
                entry for entry in Watchdog._watch_list if entry.name != name
            ]

    # WORKERS
    @staticmethod
    def _monitor_worker():
        while Watchdog._keep_watching:
            for entry in Watchdog._watch_list:
                try:
                    # list
                    if entry.module == "builtins":
                        Watchdog._log_buffer.put(
                            f"!!!INFO!!!>>> [BUILTIN] {entry.parent_name}.{entry.name} of type {entry.type} has size: {sys.getsizeof(entry.tracked)} bytes."
                        )
                        continue
                    # thread
                    module = "[CLASS SIZE]"
                    if isinstance(entry.tracked, threading.Thread):
                        module = "[THREAD SIZE]"
                        if not entry.tracked.is_alive:
                            Watchdog._log_buffer.put(
                                f"!!!WARNING!!!>>> {entry.parent_name}.{entry.name} of type {entry.type} has stopped unexpectedly."
                            )
                            Watchdog.unwatch(entry.name)
                            continue
                    # thread & class
                    Watchdog._log_buffer.put(
                        f"!!!INFO!!!>>> {module} {entry.parent_name}.{entry.name} ({entry.type}) = {asizeof.asizeof(entry.tracked)} bytes"
                    )
                except Exception as e:
                    Watchdog._log_buffer.put(
                        f"!!!EXEPTION!!!>>> Error monitoring {entry.parent_name}.{entry.name}: {e}"
                    )
                    Watchdog.unwatch(entry.name)
            #
            time.sleep(Watchdog._TIME_WATCH)

    @staticmethod
    def _log_worker():
        while Watchdog._keep_watching:
            buffer = Watchdog.get_all_log()
            if not buffer:
                continue
            with open(Watchdog._LOG_FILE, "a") as file:
                for line in buffer:
                    file.write(f"[{datetime.now()}] - {line}\n")
                #
            #
        #
