from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Tuple

@dataclass
class DeliveryOrder:
    id: int
    origin: Tuple[int, int]
    destination: Tuple[int, int]
    created_at: datetime
    priority: str = "normal"
    deadline: datetime = field(default_factory=datetime.now)
    assigned: bool = False
    picked_up: bool = False
    completed: bool = False
    delivered_at: Optional[datetime] = None
    status: str = "waiting"

    def age(self, current_time: datetime) -> int:
        return int((current_time - self.created_at).total_seconds() / 60)

    def summary(self, current_time: datetime) -> Dict[str, str]:
        return {
            "ID": str(self.id),
            "From": f"{self.origin[0]},{self.origin[1]}",
            "To": f"{self.destination[0]},{self.destination[1]}",
            "Priority": self.priority.title(),
            "Status": self.status,
            "Age (m)": str(self.age(current_time)),
        }
