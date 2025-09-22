"""
Zlogger Python Client
"""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any


class ZloggerClient:
    """Python client for Zlogger API"""

    def __init__(self, endpoint: str, api_key: str, app_name: str):
        """
        Initialize Zlogger client

        Args:
            endpoint: Zlogger API endpoint (e.g., "https://zlogger.ch/api/logs")
            api_key: Your Zlogger API key
            app_name: Name of your application
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.app_name = app_name
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        })

    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a log entry to Zlogger

        Args:
            level: Log level (debug, info, warn, error)
            message: Log message
            context: Additional context data

        Returns:
            True if log was sent successfully, False otherwise
        """
        try:
            payload = {
                "appName": self.app_name,
                "level": level.lower(),
                "message": message,
                "ts": datetime.now().isoformat() + "Z",
                "meta": context or {}
            }

            response = self.session.post(self.endpoint, json=payload)
            return response.status_code in [200, 201]

        except Exception:
            return False

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Send DEBUG level log"""
        return self.log("debug", message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Send INFO level log"""
        return self.log("info", message, context)

    def warn(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Send WARN level log"""
        return self.log("warn", message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Send ERROR level log"""
        return self.log("error", message, context)