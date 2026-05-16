import logging
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any


class EnhancedLogger:
    def __init__(self, name: str = "LearnForge"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        log_dir = "ui/logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"{name.lower()}_{datetime.now().strftime('%Y%m%d')}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.error_logs = []
        self.request_count = 0
        self.error_count = 0
    
    def debug(self, message: str, **kwargs):
        extra = self._format_kwargs(kwargs)
        self.logger.debug(f"{message} {extra}")
        sys.stdout.flush()
    
    def info(self, message: str, **kwargs):
        extra = self._format_kwargs(kwargs)
        print(f"[INFO] {message}")
        self.logger.info(f"{message} {extra}")
        sys.stdout.flush()
    
    def warning(self, message: str, **kwargs):
        extra = self._format_kwargs(kwargs)
        print(f"[WARNING] {message}")
        self.logger.warning(f"{message} {extra}")
        sys.stdout.flush()
    
    def error(self, message: str, exception: Exception = None, **kwargs):
        extra = self._format_kwargs(kwargs)
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "exception": str(exception) if exception else None,
            "context": kwargs
        }
        self.error_logs.append(error_info)
        self.error_count += 1
        
        print(f"[ERROR] {message}")
        if exception:
            self.logger.error(f"{message} {extra}", exc_info=True)
        else:
            self.logger.error(f"{message} {extra}")
        sys.stdout.flush()
    
    def critical(self, message: str, exception: Exception = None, **kwargs):
        extra = self._format_kwargs(kwargs)
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "exception": str(exception) if exception else None,
            "context": kwargs,
            "level": "critical"
        }
        self.error_logs.append(error_info)
        self.error_count += 1
        
        print(f"[CRITICAL] {message}")
        if exception:
            self.logger.critical(f"{message} {extra}", exc_info=True)
        else:
            self.logger.critical(f"{message} {extra}")
        sys.stdout.flush()
    
    def log_request(self, endpoint: str, status: str, duration_ms: float = 0, **kwargs):
        self.request_count += 1
        self.info(f"Request completed", 
                  endpoint=endpoint, 
                  status=status, 
                  duration_ms=duration_ms, 
                  **kwargs)
    
    def log_model_call(self, model_name: str, success: bool, duration_ms: float = 0, **kwargs):
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"Model call {'success' if success else 'failed'}",
                       model=model_name, duration_ms=duration_ms, **kwargs)
        sys.stdout.flush()
    
    def save_error_report(self):
        if self.error_logs:
            report_path = os.path.join("logs", f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.error_logs, f, ensure_ascii=False, indent=2)
            self.info(f"Error report saved: {report_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": f"{self.error_count/self.request_count:.1%}" if self.request_count > 0 else "0%"
        }
    
    def _format_kwargs(self, kwargs: Dict[str, Any]) -> str:
        if not kwargs:
            return ""
        return json.dumps(kwargs, ensure_ascii=False)


logger = EnhancedLogger()