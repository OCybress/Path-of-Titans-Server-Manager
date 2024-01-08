import threading
import time

class ThreadFactory:
    def __init__(self, log):
        self.threads = {}
        self.log = log

    def create(self, target, name=None, args=(), kwargs={}):
        thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs)
        thread_id = id(thread)
        self.threads[thread_id] = {'thread': thread, 'alive': True}
        return thread

    def kill_thread(self, thread_id):
        if thread_id in self.threads:
            self.threads[thread_id]['alive'] = False
            self.threads[thread_id]['thread'].join()  # Wait for the thread to finish
            del self.threads[thread_id]

    def monitor_threads(self):
        self.log.write(f'Monitor Thread started.')
        while True:
            threads_to_remove = [thread_id for thread_id, info in self.threads.items() if not info['thread'].is_alive()]
            for thread_id in threads_to_remove:
                del self.threads[thread_id]
            time.sleep(1)  # Adjust the sleep interval based on your needs

    def start_monitoring(self):
        self.log.write(f'Monitor Thread Starting.')
        monitoring_thread = threading.Thread(target=self.monitor_threads, name="ThreadMonitor")
        monitoring_thread.setDaemon(True)
        monitoring_thread.start()

