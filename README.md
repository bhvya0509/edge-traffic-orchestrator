# 🚦 Nexus Edge Traffic Orchestrator

A real-time, edge-deployed AI traffic monitoring system built with **YOLOv8, FastAPI, and Next.js**. This system analyzes video feeds to track vehicle density, estimate speed using physics calculations, and flag traffic violations in real-time.

## ✨ Core Features
- **Real-Time Object Tracking:** Uses YOLOv8 to detect and track cars, motorbikes, buses, and trucks.
- **Physics-Based Speed Estimation:** Calculates `Δy / Δt` frame-by-frame to estimate vehicle speed (km/h) across a virtual tripwire.
- **Automated Violation Detection:** Flags speeding, red-light breaches, wrong-way driving, and illegal parking.
- **Simulated ALPR Snapshots:** Dynamically crops the vehicle bounding box and sends base64 image strings to the frontend upon violation.
- **Live WebSocket Telemetry:** Pushes frame-by-frame analytics to a Next.js dashboard.
- **Recharts Data Visualization:** Plots live traffic density on an interactive graph.

## 🏗️ Architecture Stack
* **AI Edge Node:** Python, FastAPI, Ultralytics YOLO, OpenCV
* **Frontend Dashboard:** Next.js, React, Recharts, Tailwind CSS, Lucide Icons
* **Database (Optional):** Supabase (PostgreSQL) for violation logging

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone [https://github.com/bhvya0509/edge-traffic-orchestrator.git](https://github.com/bhvya0509/edge-traffic-orchestrator.git)
cd edge-traffic-orchestrator
cd edge-ai-node
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Run the inference engine
python stream_processor.py
The WebSocket and video feed will now be live on ws://localhost:8000/ws/traffic.
cd frontend-dashboard
npm install
npm run dev
Navigate to http://localhost:3000 to view the live interface.
📂 Dataset & Model Weights
Note: The training dataset (6,000+ images) and the .pt model weights are hosted externally due to Git size limits.

[Link to Hugging Face / Google Drive Dataset goes here]

[Link to YOLOv8 weights goes here]

Built by Bhvya Gupta
