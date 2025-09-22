import schedule
import time
import threading
from typing import Callable, Optional, Union, List
from datetime import datetime, timedelta
from .favicon_rotator import FaviconRotator

class FaviconScheduler:
    def __init__(self, favicon_rotator: FaviconRotator):
        self.favicon_rotator = favicon_rotator
        self.running = False
        self.thread = None
        self.schedule_jobs: List[schedule.Job] = []
        self._local_scheduler = schedule.Scheduler()
        
    def schedule_rotation(self, 
                         interval: Union[int, str] = "1hour",
                         rotation_type: str = "emoji",
                         category: Optional[str] = None):
        
        job = None
        
        if rotation_type == "emoji":
            rotation_func = lambda: self.favicon_rotator.rotate_emoji_favicon(category)
        elif rotation_type == "icon":
            rotation_func = lambda: self.favicon_rotator.rotate_icon_favicon()
        else:
            return False
        
        try:
            if isinstance(interval, str):
                if interval == "1hour" or interval == "hourly":
                    job = self._local_scheduler.every().hour.do(rotation_func)
                elif interval == "1day" or interval == "daily":
                    job = self._local_scheduler.every().day.do(rotation_func)
                elif interval == "30min":
                    job = self._local_scheduler.every(30).minutes.do(rotation_func)
                elif interval == "15min":
                    job = self._local_scheduler.every(15).minutes.do(rotation_func)
                elif interval == "5min":
                    job = self._local_scheduler.every(5).minutes.do(rotation_func)
                elif interval.endswith('s'):
                    seconds = int(interval[:-1])
                    job = self._local_scheduler.every(seconds).seconds.do(rotation_func)
                else:
                    return False
            elif isinstance(interval, int):
                if interval < 60:
                    job = self._local_scheduler.every(interval).seconds.do(rotation_func)
                else:
                    job = self._local_scheduler.every(interval).minutes.do(rotation_func)
            
            if job:
                self.schedule_jobs.append(job)
                rotation_func()
                return True
                
        except Exception:
            pass
        
        return False
    
    def start(self):
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self.clear_schedule()
    
    def clear_schedule(self):
        for job in self.schedule_jobs:
            self._local_scheduler.cancel_job(job)
        self.schedule_jobs.clear()
    
    def _run_scheduler(self):
        while self.running:
            try:
                self._local_scheduler.run_pending()
                time.sleep(1)
            except Exception:
                continue
    
    def is_running(self) -> bool:
        return self.running and bool(self.thread and self.thread.is_alive())
    
    def get_next_run_time(self) -> Optional[datetime]:
        try:
            if self.schedule_jobs:
                next_runs = [job.next_run for job in self.schedule_jobs if job.next_run]
                if next_runs:
                    return min(next_runs)
        except Exception:
            pass
        return None