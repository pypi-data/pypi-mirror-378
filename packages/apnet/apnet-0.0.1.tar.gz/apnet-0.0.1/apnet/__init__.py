"""
networkap/__init__.py
Biblioteca para comunicação TCP com suporte a múltiplos clientes, handshakes, criptografia e transferência de arquivos.
"""
import socket
import threading
import time
import json
import os
import secrets
from enum import Enum
from typing import Callable, Optional

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None  # criptografia opcional


# ---------------------- Logs ----------------------
class LogType(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    INFO = "INFO"


def log(msg: str, level: LogType = LogType.INFO):
    colors = {
        LogType.ERROR: "\033[91m",
        LogType.WARNING: "\033[93m",
        LogType.SUCCESS: "\033[92m",
        LogType.INFO: "\033[94m",
    }
    c = colors.get(level, "\033[0m")
    print(f"{c}[{time.strftime('%H:%M:%S')} {level.value}] {msg}\033[0m")


# ------------------ Utilidades --------------------
def generate_handshake(purpose: str) -> bytes:
    if purpose == "binary":
        return secrets.token_bytes(16)
    elif purpose == "js":
        return json.dumps({"handshake": secrets.token_hex(8)}).encode()
    return f"HANDSHAKE-{secrets.token_hex(4)}".encode()


def convert_data(data, to="bytes"):
    try:
        if to == "bytes":
            if isinstance(data, bytes):
                return data
            return json.dumps(data).encode()
        elif to == "json":
            if isinstance(data, bytes):
                return json.loads(data.decode())
            if isinstance(data, str):
                return json.loads(data)
        elif to == "str":
            if isinstance(data, bytes):
                return data.decode()
            return str(data)
        else:
            raise ValueError("Tipo de conversão inválido.")
    except Exception as e:
        log(f"Falha na conversão: {e}", LogType.ERROR)
        return None


# ------------------ Criptografia ------------------
def generate_key() -> bytes:
    if not Fernet:
        log("cryptography não instalado, criptografia indisponível.", LogType.WARNING)
        return b""
    return Fernet.generate_key()


def encrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data) if Fernet else data


def decrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(data) if Fernet else data


# ------------------ Classe Servidor ----------------
class AP1:
    """
    Servidor: aceita múltiplos clientes.
    """
    def __init__(self, encryption_key: bytes = b""):
        self.server = None
        self.clients = []   # [(conn, addr)]
        self.running = False
        self.handshake = None
        self.encryption_key = encryption_key
        # callbacks
        self.on_connect: Optional[Callable[[socket.socket, tuple], None]] = None
        self.on_message: Optional[Callable[[socket.socket, bytes], None]] = None
        self.on_disconnect: Optional[Callable[[tuple], None]] = None

    def OpenPort(self, port: int, purpose: str):
        self.handshake = generate_handshake(purpose)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", port))
        self.server.listen(5)
        self.running = True
        log(f"AP1 escutando na porta {port} para {purpose}", LogType.SUCCESS)

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while self.running:
            conn, addr = self.server.accept()
            log(f"Cliente {addr} conectado.", LogType.INFO)
            conn.sendall(self.handshake)
            self.clients.append((conn, addr))
            if self.on_connect:
                self.on_connect(conn, addr)
            threading.Thread(target=self._client_loop, args=(conn, addr), daemon=True).start()

    def _client_loop(self, conn, addr):
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                if self.encryption_key:
                    data = decrypt(data, self.encryption_key)
                if self.on_message:
                    self.on_message(conn, data)
        except Exception as e:
            log(f"Erro com {addr}: {e}", LogType.ERROR)
        finally:
            conn.close()
            self.clients = [c for c in self.clients if c[0] != conn]
            if self.on_disconnect:
                self.on_disconnect(addr)
            log(f"Cliente {addr} desconectado.", LogType.WARNING)

    def send_data(self, conn, data, encrypt_enable=True):
        payload = convert_data(data, "bytes")
        if self.encryption_key and encrypt_enable:
            payload = encrypt(payload, self.encryption_key)
        conn.sendall(payload)

    def broadcast(self, data):
        for conn, _ in list(self.clients):
            self.send_data(conn, data)

    def send_file(self, conn, file_path):
        size = os.path.getsize(file_path)
        self.send_data(conn, {"file_start": os.path.basename(file_path), "size": size})
        with open(file_path, "rb") as f:
            sent = 0
            while chunk := f.read(4096):
                if self.encryption_key:
                    chunk = encrypt(chunk, self.encryption_key)
                conn.sendall(chunk)
                sent += len(chunk)
                log(f"Enviado {sent}/{size} bytes", LogType.INFO)
        self.send_data(conn, {"file_end": True})

    def ClosePort(self, port: int):
        self.running = False
        if self.server:
            self.server.close()
        for c, _ in self.clients:
            c.close()
        log(f"Servidor na porta {port} fechado.", LogType.SUCCESS)


# ------------------ Classe Cliente -----------------
class AP2:
    """
    Cliente: conecta e envia/recebe mensagens.
    """
    def __init__(self, encryption_key: bytes = b""):
        self.sock = None
        self.encryption_key = encryption_key
        self.on_message: Optional[Callable[[bytes], None]] = None
        self.running = False

    def ConnectonPort(self, port: int, host="127.0.0.1"):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        handshake = self.sock.recv(1024)
        log(f"Handshake recebido: {handshake}", LogType.SUCCESS)
        self.running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self):
        while self.running:
            data = self.sock.recv(4096)
            if not data:
                break
            if self.encryption_key:
                data = decrypt(data, self.encryption_key)
            if self.on_message:
                self.on_message(data)

    def send_data(self, data, encrypt_enable=True):
        payload = convert_data(data, "bytes")
        if self.encryption_key and encrypt_enable:
            payload = encrypt(payload, self.encryption_key)
        self.sock.sendall(payload)

    def send_file(self, file_path):
        size = os.path.getsize(file_path)
        self.send_data({"file_start": os.path.basename(file_path), "size": size})
        with open(file_path, "rb") as f:
            sent = 0
            while chunk := f.read(4096):
                if self.encryption_key:
                    chunk = encrypt(chunk, self.encryption_key)
                self.sock.sendall(chunk)
                sent += len(chunk)
                log(f"Enviado {sent}/{size} bytes", LogType.INFO)
        self.send_data({"file_end": True})

    def ClosePort(self):
        self.running = False
        if self.sock:
            self.sock.close()
        log("Conexão encerrada.", LogType.SUCCESS)
