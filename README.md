# Smart Delivery Simulator

A real-world delivery optimization system simulating dynamic agent behaviors, priority routing logic, and traffic constraints inside a gamified dashboard environment.

## Features

- **Dynamic Order Arrival:** Time-based continuous simulation with random origins/destinations, tracking peak-hour traffic multipliers.
- **Priority Delivery System:** Multi-tiered priority system (Normal, High, Urgent) applying specific delivery penalties or time bonuses dynamically.
- **Traffic System:** Grid-based visual mapping containing live traffic multipliers that augment algorithm path traversal costs.
- **AI Decision Engine & Route Optimization:** Contextually-aware routing utilizing NetworkX (A* pathfinding) factoring in congestion patterns and agent fatigue.
- **Weather & Chaos Mode:** Storm and Rain configurations shifting grid efficiencies globally, supported by predictive analytics displaying live.

## Tech Stack

- Python 3.10
- Streamlit (Animation-rich interactive UI with Glassmorphic styling)
- NetworkX (Dijkstra / A* Graph algorithms)
- Plotly (Data-streams and analytics)
- Pandas & Numpy

## Screenshots

![Dashboard Screenshot Placeholder](https://via.placeholder.com/800x450/475569/FFFFFF?text=Smart+Delivery+Dashboard)

## Folder Structure

```text
delivery_simulator/
├── env.py                # Core simulation environment mapping state
├── main.py               # App entry runner wrapper
├── models/               # Domain layer models (Agent, Order)
├── services/             # Application services (AI, Routing, Priority, Traffic)
├── ui/                   # Modular UI (app.py) & CSS Styling (styles.css)
├── utils/                # Helper tools (rank systems, formatters)
├── requirements.txt      # Dependency specification
├── Dockerfile            # Container deployment build map
└── README.md             # Project manifesto
```

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/delivery-simulator.git
   cd delivery-simulator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the platform:**
   ```bash
   streamlit run ui/app.py
   ```

## Deployment

The application runs seamlessly locally and defaults to port `7860`.

**Run with Docker:**
```bash
docker build -t smart-simulator .
docker run -p 7860:7860 smart-simulator
```

**Hugging Face Spaces:**
This app natively adheres to `.hf` structure defaults for Streamlit, exposing `0.0.0.0` at port `7860` out of the box leveraging the `Dockerfile`.
