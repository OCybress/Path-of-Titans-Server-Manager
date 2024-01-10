import threading
import time

class ThreadFactory:
    """
    A class that provides methods for creating and managing threads.

    Attributes:
        threads (dict): A dictionary that stores information about the created threads.
        log: The log object used for writing log messages.

    Methods:
        create(target, name=None, args=(), kwargs={}): Creates a new thread.
        kill_thread(thread_id): Kills a running thread.
        monitor_threads(): Monitors the running threads and removes the finished ones.
        start_monitoring(): Starts the thread monitoring process.
    """

    def __init__(self, log):
        self.threads = {}
        self.log = log

    def create(self, target, name=None, args=(), kwargs={}):
        """
        Creates a new thread.

        Args:
            target: The target function to be executed by the thread.
            name (str): The name of the thread (optional).
            args (tuple): The arguments to be passed to the target function (optional).
            kwargs (dict): The keyword arguments to be passed to the target function (optional).

        Returns:
            The created thread object.
        """
        thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
        thread_id = id(thread)
        self.threads[thread_id] = {'thread': thread, 'alive': True}
        return thread

    def kill_thread(self, thread_id):
        """
        Kills a running thread.

        Args:
            thread_id: The ID of the thread to be killed.
        """
        if thread_id in self.threads:
            self.threads[thread_id]['alive'] = False
            self.threads[thread_id]['thread'].join()  # Wait for the thread to finish
            del self.threads[thread_id]

    def monitor_threads(self):
        """
        Monitors the running threads and removes the finished ones.
        """
        self.log.write(f'Monitor Thread started.')
        while True:
            threads_to_remove = [thread_id for thread_id, info in self.threads.items() if not info['thread'].is_alive()]
            for thread_id in threads_to_remove:
                del self.threads[thread_id]
            time.sleep(1)  # Adjust the sleep interval based on your needs

    def start_monitoring(self):
        """
        Starts the thread monitoring process.
        """
        self.log.write(f'Monitor Thread Starting.')
        monitoring_thread = threading.Thread(target=self.monitor_threads, name="ThreadMonitor")
        monitoring_thread.setDaemon(True)
        monitoring_thread.start()

