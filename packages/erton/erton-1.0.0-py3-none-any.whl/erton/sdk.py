from __future__ import annotations
import socket, json, base64
from typing import Dict, Any
from .crypto import issue_token
class ErtonClient:
    def __init__(self, host: str="127.0.0.1", port: int=8765, shared_key: bytes=b"default_dev_key____________________"[:32], timeout: float=1.0):
        self.addr = (host, port); self.timeout = timeout; self.shared_key = shared_key
    def _token(self, player_id: str) -> str: return issue_token(player_id, self.shared_key, ttl=5)
    def send(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s = socket.create_connection(self.addr, timeout=self.timeout)
        with s:
            s_file = s.makefile("rwb"); greet = json.loads(s_file.readline().decode())
            data["token"] = self._token(data.get("player_id","anon"))
            s_file.write((json.dumps(data, ensure_ascii=False)+"\n").encode()); s_file.flush()
            resp = s_file.readline()
        try: return json.loads(resp.decode("utf-8", errors="ignore"))
        except Exception: return {"ok": False, "error":"invalid response"}
    def approve(self, player_id: str) -> Dict[str, Any]: return self.send({"type":"watch.approve","player_id":player_id})
    def revoke(self, player_id: str) -> Dict[str, Any]: return self.send({"type":"watch.revoke","player_id":player_id})
    def aim_tick(self, player_id: str, **payload) -> Dict[str, Any]:
        payload.update({"type":"aim_tick","player_id":player_id}); return self.send(payload)
