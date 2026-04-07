from typing import List, Optional
import networkx as nx
from models.agent import DeliveryAgent
from models.order import DeliveryOrder
from services.routing import shortest_path, path_cost

class AIEngine:
    def __init__(self):
        self.history = []

    def evaluate_best_agent(self, agents: List[DeliveryAgent], order: DeliveryOrder, graph: nx.DiGraph) -> tuple[Optional[DeliveryAgent], str]:
        best_agent = None
        best_score = float('inf')
        reasoning = "No available agents."

        idle_agents = [a for a in agents if a.is_idle()]
        if not idle_agents:
            return None, reasoning

        for agent in idle_agents:
            path = shortest_path(graph, agent.position, order.origin)
            dist_cost = path_cost(graph, path)
            fatigue_penalty = agent.fatigue * 10
            
            # Simple heuristic incorporating distance, agent fatigue, and base efficiency
            # Modify heuristic based on strategy if accessible
            score = (dist_cost + fatigue_penalty) / agent.efficiency

            if score < best_score:
                best_score = score
                best_agent = agent
                factors = []
                if dist_cost < 2: factors.append("very close proximity")
                if agent.fatigue < 0.2: factors.append("well rested")
                if agent.efficiency > 1.0: factors.append("high efficiency mapping")
                
                reason = " and ".join(factors) if factors else ("lowest path cost of " + str(round(dist_cost,1)))
                reasoning = f"Agent {agent.agent_id} selected due to {reason}."

        if best_agent:
            self.history.append({"agent": best_agent.agent_id, "order": order.id, "reasoning": reasoning})

        return best_agent, reasoning
