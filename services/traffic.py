import random
from typing import Dict, Tuple

TRAFFIC_LEVELS = ["low", "medium", "high"]
TRAFFIC_MULTIPLIER = {"low": 1.0, "medium": 2.0, "high": 4.0}
TRAFFIC_ICON = {"low": "🟢", "medium": "🟠", "high": "🔴"}

class TrafficManager:
    def __init__(self, grid_size: int = 10):
        self.grid_size = grid_size
        self.zone_map: Dict[Tuple[int, int], str] = {}
        self.weather = "Clear"
        self._initialize_zones()

    def _initialize_zones(self) -> None:
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                self.zone_map[(x, y)] = "low"

    def update(self, level: str, chaos_mode: bool) -> None:
        change_chance = 0.05 if level == "Medium" else 0.15 if level == "Hard" else 0.0
        
        # Weather shift
        if level == "Hard" and random.random() < 0.02:
            self.weather = random.choice(["Clear", "Rain", "Storm"])
            
        if chaos_mode:
            change_chance = 0.3
            if random.random() < 0.05:
                self.weather = "Storm"

        if random.random() < change_chance:
            self._mutate_zones(chaos_mode)

    def _mutate_zones(self, chaos: bool) -> None:
        impact = 0.4 if chaos else (0.3 if self.weather == "Rain" else 0.1)
        for coord in self.zone_map:
            if random.random() < impact:
                weights = [0.2, 0.4, 0.4] if self.weather == "Storm" else [0.6, 0.3, 0.1]
                if chaos:
                    weights = [0.1, 0.4, 0.5]
                self.zone_map[coord] = random.choices(TRAFFIC_LEVELS, weights=weights, k=1)[0]

    def edge_weight(self, source: Tuple[int, int], target: Tuple[int, int]) -> float:
        s_lvl = self.zone_map.get(source, "low")
        t_lvl = self.zone_map.get(target, "low")
        multiplier = (TRAFFIC_MULTIPLIER[s_lvl] + TRAFFIC_MULTIPLIER[t_lvl]) / 2.0
        weather_penalty = 1.5 if self.weather == "Rain" else 2.5 if self.weather == "Storm" else 1.0
        return max(multiplier * weather_penalty, 1.0)
