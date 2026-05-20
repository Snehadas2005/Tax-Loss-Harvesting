# 📊 Portfolio Rebalancer: AI Tax-Loss Harvesting Engine

> **Current Status:** 🚧 Under Development - Phase 1 (ML Engine & Data Research)

An intelligent financial tool designed to optimize investment portfolios by automating **Tax-Loss Harvesting**. The application identifies "stagnant losers," predicts recovery trends using Machine Learning, and suggests tax-efficient replacements to maintain market exposure.

---

## 🏗️ Project Roadmap

### Phase 1: Data & Clustering (Current)

* **Status:** Active
* **Focus:** Gathering 5-year historical data using `yfinance` and building the **K-Means Clustering** "Twin Finder" to group stocks by risk profiles.

### Phase 2: Harvesting Logic & Regression

* **Status:** Pending
* **Focus:** Training the **XGBoost** model to predict 30-day trends and identifying "Primary Harvesting" candidates based on tax-saving potential.

### Phase 3: Backtesting & Validation

* **Status:** Planned
* **Focus:** Simulating the ML logic against historical bear markets to calculate **Tax Alpha** and ensure compliance with the **Wash-Sale Rule**.

### Phase 4: Integration & Deployment

* **Status:** Planned
* **Focus:** Wrapping ML models in **FastAPI** and connecting the engine to the React dashboard for a full end-to-end user experience.

---

## 👥 The Team

| Name | Role | Core Tech Stack | Responsibilities |
| --- | --- | --- | --- |
| **[Sneha Das](https://github.com/Snehadas2005)** | **ML Specialist** | Python, Scikit-learn, XGBoost, Pandas, yfinance | **The "Intelligence":** Building the clustering pipeline and regression models to optimize harvest timing. |
| **[Ansh Jaiswal](https://github.com/ansh1004-hub)** | **Frontend Engineer** | React.js/Next.js, Tailwind CSS, Recharts | **The "Interface":** Visualizing complex data into a user-friendly dashboard with interactive risk/asset charts. |
| **[Adveta Rai](https://github.com/AdvetaRai)** | **Backend Engineer** | FastAPI/Node.js, PostgreSQL | **The "Engine":** Architecting the database, handling the trade processing logic, and the backtesting loop. |
