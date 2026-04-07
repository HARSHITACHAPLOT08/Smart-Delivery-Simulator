import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from models.agent import DeliveryAgent
from models.order import DeliveryOrder
from services.priority import PRIORITY_LEVELS, PRIORITY_PENALTY, calculate_priority_bonus, get_deadline_multiplier
from services.routing import build_grid_graph, shortest_path
from services.traffic import TrafficManager
from services.ai_engine import AIEngine

LEVEL_CONFIG = {
    "Easy": {"rate": 0.0, "base": 4, "weights": [1.0, 0.0, 0.0]},
    "Medium": {"rate": 0.2, "base": 2, "weights": [0.6, 0.3, 0.1]},
    "Hard": {"rate": 0.45, "base": 2, "weights": [0.4, 0.3, 0.3]},
}

PEAK_WINDOWS = [(11, 14), (18, 21)]

class DeliveryEnvironment:
    def __init__(self, level: str = "Easy", manual_mode: bool = False, agent_count: int = 3, grid_size: int = 10, chaos: bool = False, strategy: str = "Balanced"):
        self.level = level
        self.manual_mode = manual_mode
        self.chaos_mode = chaos
        self.strategy = strategy
        self.grid_size = grid_size
        self.agent_count = agent_count
        self.tick = 0
        self.time = datetime(2026, 1, 1, 8, 0)
        self.score = 0
        self.penalties = 0
        self.orders: List[DeliveryOrder] = []
        self.completed_orders: List[DeliveryOrder] = []
        self.agents: List[DeliveryAgent] = []
        self.notifications: List[str] = []
        
        self.traffic = TrafficManager(grid_size)
        self.graph = build_grid_graph(grid_size, self.traffic)
        self.ai = AIEngine()
        self.ai_decisions = []
        
        self.history: List[Dict[str, float]] = []
        self.order_counter = 0
        self.manual_assignments: Dict[int, int] = {}
        
        self._prepare_agents()
        self._initialize_orders()

    def _prepare_agents(self) -> None:
        self.agents = [DeliveryAgent(agent_id=i+1, position=(random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)), efficiency=round(random.uniform(0.8, 1.2), 2)) for i in range(self.agent_count)]

    def _initialize_orders(self) -> None:
        for _ in range(LEVEL_CONFIG[self.level]["base"]):
            self.orders.append(self._create_order("normal" if self.level == "Easy" else None))

    def _create_order(self, force_priority: str = None) -> DeliveryOrder:
        self.order_counter += 1
        pos1 = (random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1))
        pos2 = pos1
        while pos2 == pos1:
            pos2 = (random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1))
        pri = force_priority or random.choices(PRIORITY_LEVELS, weights=LEVEL_CONFIG[self.level]["weights"], k=1)[0]
        dl = self.time + timedelta(minutes=15 * get_deadline_multiplier(pri) * (0.8 if self.chaos_mode else 1.0))
        return DeliveryOrder(id=self.order_counter, origin=pos1, destination=pos2, created_at=self.time, priority=pri, deadline=dl)

    def generate_orders(self) -> None:
        if self.level == "Easy": return
        change_chance = LEVEL_CONFIG[self.level]["rate"] * (1.5 if any(s <= self.time.hour < e for s,e in PEAK_WINDOWS) else 1.0)
        if self.chaos_mode: change_chance *= 1.3
        if random.random() < change_chance:
            new_order = self._create_order()
            self.orders.append(new_order)
            if new_order.priority == "urgent":
                self.notifications.append("🚨 Urgent order received!")

    def update_environment(self) -> None:
        old_weather = self.traffic.weather
        self.traffic.update(self.level, self.chaos_mode)
        if old_weather != self.traffic.weather and self.traffic.weather == "Storm":
            self.notifications.append("⚡ Severe weather detected! Traffic delayed.")
        self.graph = build_grid_graph(self.grid_size, self.traffic)

    def assign_orders(self) -> None:
        avail = [o for o in self.orders if not o.assigned and not o.completed]
        if not avail: return
        
        if self.manual_mode:
            for aid, oid in list(self.manual_assignments.items()):
                agent = next((a for a in self.agents if a.agent_id == aid), None)
                order = next((o for o in self.orders if o.id == oid), None)
                if agent and order and agent.is_idle() and not order.assigned:
                    agent.assign(order)
            self.manual_assignments.clear()
            return

        for order in sorted(avail, key=lambda x: {"urgent":0, "high":1, "normal":2}[x.priority]):
            if all(not a.is_idle() for a in self.agents): break
            agent, reason = self.ai.evaluate_best_agent(self.agents, order, self.graph)
            if agent:
                agent.assign(order)
                self.ai_decisions.insert(0, f"Tick {self.tick}: Order {order.id} -> {reason}")
                
        self.ai_decisions = self.ai_decisions[:5]

    def move_agents(self) -> None:
        for agent in self.agents:
            if not agent.assigned_order: continue
            order = agent.assigned_order
            
            goal = order.destination if order.picked_up else order.origin
            path = shortest_path(self.graph, agent.position, goal)
            agent.route = path[1:] if len(path) > 1 else []
            
            if agent.route:
                agent.move_to(agent.route[0])
            
            if agent.position == order.origin and not order.picked_up:
                order.picked_up = True
                order.status = "in transit"
            elif agent.position == order.destination and order.picked_up:
                self._complete(agent, order)

    def _complete(self, agent: DeliveryAgent, order: DeliveryOrder) -> None:
        order.completed = True
        order.delivered_at = self.time
        order.status = "delivered"
        agent.completed_orders += 1
        
        bonus = calculate_priority_bonus(order.priority)
        pen = max(0, PRIORITY_PENALTY[order.priority] * int((order.delivered_at - order.deadline).total_seconds() / 60))
        self.penalties += pen
        reward = bonus - pen
        agent.score += reward
        self.score += reward
        
        self.completed_orders.append(order)
        self.orders.remove(order)
        agent.clear_assignment()

    def step(self) -> None:
        self.tick += 1
        self.time += timedelta(minutes=2)
        self.update_environment()
        self.generate_orders()
        self.assign_orders()
        self.move_agents()
        self.history.append({"tick": self.tick, "score": self.score, "delivered": len(self.completed_orders), "pending": len([o for o in self.orders if not o.completed])})

    def get_metrics(self) -> Dict[str, float]:
        return {
            "Tick": self.tick,
            "Score": max(self.score, 0),
            "Delivered": len(self.completed_orders),
            "Pending": len(self.orders),
            "Penalties": self.penalties,
        }
