import time
import pandas as pd
import streamlit as st
import plotly.express as px

from env import DeliveryEnvironment
from utils.helpers import get_rank

st.set_page_config(page_title="Smart Delivery Simulator", layout="wide", initial_sidebar_state="expanded")

def apply_css(env: DeliveryEnvironment = None):
    try:
        with open("ui/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    weather = getattr(env.traffic, "weather", "Clear") if env and env.traffic else "Clear"
    if weather != "Clear":
        overlay = f"<div style='position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;' class='weather-{weather.lower()}'></div>"
        st.markdown(overlay, unsafe_allow_html=True)
        
    if env and env.notifications:
        notif_html = "<div style='position:fixed;top:20px;right:20px;z-index:10000;'>"
        for n in env.notifications:
            notif_html += f"<div class='floating-notif'>{n}</div>"
        notif_html += "</div>"
        st.markdown(notif_html, unsafe_allow_html=True)
        env.notifications.clear()

def render_map(env: DeliveryEnvironment):
    grid = []
    agent_pos = {a.position: f"🛵<div style='font-size:10px'>{a.agent_id}</div>" for a in env.agents}
    order_pos = {o.origin: o for o in env.orders if not o.picked_up}
    
    for y in range(env.grid_size - 1, -1, -1):
        row = []
        for x in range(env.grid_size):
            coord = (x, y)
            t_class = f"traffic-{env.traffic.zone_map.get(coord, 'low')}"
            
            icon = ""
            cell_cls = ["grid-cell", t_class]
            
            if coord in agent_pos:
                icon = agent_pos[coord]
                cell_cls.append("agent-node")
            elif coord in order_pos:
                o = order_pos[coord]
                icon = {"normal": "📦", "high": "⚡", "urgent": "🚨"}.get(o.priority, "📦")
                if o.priority == "urgent": cell_cls.append("urgent-pulse")
                cell_cls.append("order-node")
                
            row.append(f"<div class='{' '.join(cell_cls)}' title='{coord}'>{icon}</div>")
        grid.append("<div class='grid-row'>" + "".join(row) + "</div>")
    
    st.markdown(f"<div class='card grid-container'>{''.join(grid)}</div>", unsafe_allow_html=True)

def render_dashboard(env: DeliveryEnvironment):
    metrics = env.get_metrics()
    rank = get_rank(metrics["Score"])
    
    st.markdown(f"""
    <div class='card'>
        <h3>Dashboard</h3>
        <p>Simulation Time: <b>{env.time.strftime('%H:%M')}</b> | Weather: <b>{getattr(env.traffic, 'weather', 'Clear')}</b> | Rank: <b>{rank}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(metrics))
    for i, (k, v) in enumerate(metrics.items()):
        cols[i].markdown(f"<div class='card' style='text-align:center;'><div style='font-size:14px;color:#64748b;'>{k}</div><div class='metric-value'>{v}</div></div>", unsafe_allow_html=True)

    if env.history:
        st.markdown("<div class='card'><h4>Performance Growth</h4>", unsafe_allow_html=True)
        df = pd.DataFrame(env.history)
        fig = px.line(df, x="tick", y=["score", "delivered", "pending"], template="plotly_white")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    if "env" not in st.session_state:
        st.session_state.env = DeliveryEnvironment()
        st.session_state.running = False
        st.session_state.speed = 0.5
        
    env = st.session_state.env
    apply_css(env)

    with st.sidebar:
        st.markdown("## ⚙️ Control Center")
        st.markdown('<div class="card" style="margin-bottom: 20px; font-size: 14px; color: #475569;">🚦 <b>System Dashboard</b><br>Configure simulation parameters, agent behaviors, and environmental constraints.</div>', unsafe_allow_html=True)
        lvl = st.selectbox("Level", ["Easy", "Medium", "Hard"])
        mode = st.radio("Assignment Mode", ["AI", "Manual"])
        strategy = st.selectbox("Routing Strategy", ["Balanced", "Fastest Route", "Least Traffic"])
        chaos = st.toggle("🌪️ Chaos Mode", value=env.chaos_mode)
        speed = st.slider("Time Warp (Tick Speed)", 0.1, 2.0, 0.5, 0.1)
        st.session_state.speed = speed
        
        c1, c2 = st.columns(2)
        if c1.button("▶️ Start/Resume", use_container_width=True): st.session_state.running = True
        if c2.button("⏸️ Pause", use_container_width=True): st.session_state.running = False
        if st.button("🔄 Reset Simulation", use_container_width=True):
            st.session_state.env = DeliveryEnvironment(level=lvl, manual_mode=(mode=="Manual"), chaos=chaos)
            st.session_state.env.strategy = strategy
            st.session_state.running = False
            if hasattr(st, "rerun"): st.rerun()
            else: st.experimental_rerun()
            
        if mode == "Manual":
            st.markdown("---")
            st.subheader("Manual Control")
            avail = [o.id for o in env.orders if not o.assigned]
            for a in env.agents:
                if a.is_idle() and avail:
                    oid = st.selectbox(f"Agent {a.agent_id}", ["none"] + avail)
                    if oid != "none": env.manual_assign(a.agent_id, int(oid))

    c_map, c_dash = st.columns([1.5, 1])
    
    with c_map:
        st.markdown("<h3>🌍 Live City Grid</h3>", unsafe_allow_html=True)
        render_map(env)
        
        c_pred, c_log = st.columns(2)
        with c_pred:
            st.markdown("<div class='card prediction-box'><h4>🔮 AI Prediction</h4>", unsafe_allow_html=True)
            current_weather = getattr(env.traffic, "weather", "Clear") if env and env.traffic else "Clear"
            if current_weather == "Storm":
                st.markdown("⚠️ **Expected delay spike in next 2 mins** due to severe weather.", unsafe_allow_html=True)
            elif len(env.orders) > 4:
                st.markdown("📈 **High order volume** detected. Agents will experience fatigue soon.", unsafe_allow_html=True)
            else:
                st.markdown("✨ **Traffic is smooth**. Excellent delivery conditions.", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_log:
            st.markdown("<div class='card'><h4>🧠 Why this decision?</h4>", unsafe_allow_html=True)
            if env.ai_decisions:
                for l in env.ai_decisions[:3]: 
                    st.markdown(f"<span style='font-size:14px;color:#475569;'>• {l}</span>", unsafe_allow_html=True)
            else:
                st.caption("No AI logs yet.")
            st.markdown("</div>", unsafe_allow_html=True)

    with c_dash:
        render_dashboard(env)

    if st.session_state.running:
        with st.spinner("AI Engine Optimizing Routes..."):
            env.step()
            time.sleep(speed)
            if hasattr(st, 'rerun'): st.rerun()
            else: st.experimental_rerun()

if __name__ == "__main__":
    main()
