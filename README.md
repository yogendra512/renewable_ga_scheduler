# ⚡ Renewable Energy GA Scheduler (Dynamic)

A fully dynamic Streamlit app using a **Genetic Algorithm** to schedule renewable energy sources with **live progress**, **animated charts**, **run comparison**, and **save/load history**.

---

## 📁 Project Structure

```
renewable_ga_scheduler/
│
├── app.py                      # Entry point — tabbed layout
│
├── core/                       # Pure Python logic (no Streamlit)
│   ├── __init__.py
│   ├── battery.py              # Battery constraint enforcement
│   ├── fitness.py              # Objective / fitness function
│   ├── operators.py            # init, crossover, mutate
│   └── ga.py                   # GA runner with live yielding
│
├── ui/                         # Streamlit UI components
│   ├── __init__.py
│   ├── sidebar.py              # Sidebar config
│   ├── input_table.py          # Editable hourly data
│   ├── live_progress.py        # Real-time progress bar + animated charts
│   ├── results.py              # Final results panel + CSV download
│   └── compare.py              # Multi-run comparison tab
│
├── utils/
│   ├── __init__.py
│   └── storage.py              # JSON-based save/load run history
│
├── requirements.txt
└── README.md
```

---

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set **Main file path** to `app.py`
4. Click **Deploy** — done!

---

## ✨ Dynamic Features

| Feature | Description |
|---|---|
| **Live progress bar** | Updates every N generations showing current gen & best cost |
| **Animated fitness chart** | GA convergence curve updates in real-time |
| **Animated schedule charts** | Generation mix & SOC charts refresh as GA evolves |
| **Auto-save runs** | Every completed run is saved with name + timestamp |
| **Compare runs** | Overlay convergence curves, KPI table, side-by-side charts |
| **Delete / clear runs** | Manage saved history from the Compare tab |
| **CSV export** | Download final hourly schedule as CSV |
