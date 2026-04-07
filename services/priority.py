PRIORITY_LEVELS = ["normal", "high", "urgent"]
PRIORITY_LABELS = {"normal": "Normal", "high": "High", "urgent": "Urgent"}
PRIORITY_PENALTY = {"normal": 0, "high": 5, "urgent": 15}
PRIORITY_BONUS = {"normal": 10, "high": 30, "urgent": 60}

def get_deadline_multiplier(priority: str) -> float:
    return {"normal": 1.0, "high": 0.6, "urgent": 0.3}.get(priority, 1.0)

def calculate_priority_bonus(priority: str) -> int:
    return PRIORITY_BONUS.get(priority, PRIORITY_BONUS["normal"])
