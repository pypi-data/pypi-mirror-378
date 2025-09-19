from __future__ import annotations
from typing import Set
class Watchlist:
    def __init__(self)->None:
        self.approved: Set[str] = set()
        self.blocked: Set[str] = set()
    def approve(self, player_id: str)->None: self.approved.add(player_id)
    def revoke(self, player_id: str)->None: self.approved.discard(player_id)
    def block(self, player_id: str)->None: self.blocked.add(player_id)
    def is_approved(self, player_id: str)->bool: return player_id in self.approved
    def is_blocked(self, player_id: str)->bool: return player_id in self.blocked
WATCH = Watchlist()
