import socket
import logging

logger = logging.getLogger(__name__)


class PortManager:
    _instance = None

    @classmethod
    def get_instance(cls) -> "PortManager":
        if cls._instance is None:
            raise RuntimeError("PortManager not initialized. Call initialize() first.")
        return cls._instance

    @classmethod
    def initialize(cls, start_port: int, host: str) -> "PortManager":
        if cls._instance is None:
            cls._instance = cls(start_port, host)
        return cls._instance

    def __init__(self, start_port: int, host: str):
        if PortManager._instance is not None:
            raise RuntimeError(
                "PortManager is a singleton. Use get_instance() instead."
            )

        self.host = host
        self.port = self.find_available_port(start_port)
        logger.info(f"PortManager initialized with port {self.port}")

        PortManager._instance = self

    def get_port(self) -> int:
        return self.port

    def get_host(self) -> str:
        return self.host

    def get_base_url(self) -> str:
        display_host = "localhost" if self.host == "0.0.0.0" else self.host
        return f"http://{display_host}:{self.port}"

    def get_ws_url(self) -> str:
        display_host = "localhost" if self.host == "0.0.0.0" else self.host
        return f"ws://{display_host}:{self.port}"

    @staticmethod
    def find_available_port(start_port: int, max_attempts: int = 100) -> int:
        for port in range(start_port, start_port + max_attempts):
            if PortManager._is_port_available(port):
                return port

        raise RuntimeError(
            f"Could not find available port in range {start_port}-{start_port + max_attempts - 1}"
        )

    @staticmethod
    def _is_port_available(port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return True
        except OSError:
            return False
