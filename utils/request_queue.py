import queue
import threading
import time
from typing import Callable, Any, Optional
from uuid import uuid4


class RequestQueue:
    def __init__(self, max_pending: int = 10, max_concurrent: int = 2):
        self.request_queue = queue.Queue(maxsize=max_pending)
        self.max_concurrent = max_concurrent
        self.active_workers = 0
        self.lock = threading.Lock()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def submit(self, task: Callable, *args, **kwargs) -> Optional[str]:
        try:
            request_id = str(uuid4())
            self.request_queue.put({
                'request_id': request_id,
                'task': task,
                'args': args,
                'kwargs': kwargs
            }, block=False)
            return request_id
        except queue.Full:
            return None
    
    def _worker_loop(self):
        while self.running:
            try:
                with self.lock:
                    if self.active_workers >= self.max_concurrent:
                        time.sleep(0.1)
                        continue
                
                item = self.request_queue.get(timeout=1)
                request_id = item['request_id']
                task = item['task']
                args = item['args']
                kwargs = item['kwargs']
                
                with self.lock:
                    self.active_workers += 1
                
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    print(f"Request {request_id} failed: {e}")
                finally:
                    with self.lock:
                        self.active_workers -= 1
                
                self.request_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}")
    
    def get_status(self) -> dict:
        with self.lock:
            return {
                'pending_tasks': self.request_queue.qsize(),
                'active_workers': self.active_workers,
                'max_concurrent': self.max_concurrent,
                'is_running': self.running
            }
    
    def shutdown(self):
        self.running = False
        self.worker_thread.join(timeout=5)


request_queue = RequestQueue(max_pending=10, max_concurrent=2)
