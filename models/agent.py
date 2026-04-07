from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from models.order import DeliveryOrder

@dataclass
class DeliveryAgent:
    agent_id: int
    position: Tuple[int, int]
    speed: int = 1  # 1 cell per tick
    efficiency: float = 1.0
    fatigue: float = 0.0
    assigned_order: Optional[DeliveryOrder] = None
    route: List[Tuple[int, int]] = field(default_factory=list)
    completed_orders: int = 0
    score: int = 0
    status: str = "idle"

    def is_idle(self) -> bool:
        return self.assigned_order is None

    def assign(self, order: DeliveryOrder) -> None:
        self.assigned_order = order
        order.assigned = True
        self.status = "assigned"

    def clear_assignment(self) -> None:
        self.assigned_order = None
        self.route = []
        self.status = "idle"
        self.fatigue = max(0.0, self.fatigue - 0.1) # recovers slightly when dropping off

    def move_to(self, next_position: Tuple[int, int]) -> None:
        self.position = next_position
        self.status = "en route"
        self.fatigue += 0.02 # increases as they move
