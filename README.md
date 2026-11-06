# Live Portfolio Optimizer (Modern Portfolio Theory)

An interactive mean-variance optimizer. Enter 5–15 tickers, set your constraints, and it pulls live price history, solves for the optimal weights and plots the efficient frontier.

🚀 **[Try the live app](https://petrescu-portfolio.streamlit.app)**

📝 **Write-up:** [Implementing Modern Portfolio Theory: Building a Live Optimizer from the Ground Up](https://9numbers0.substack.com/p/implementing-modern-portfolio-theory)

## What it does
- **Live data:** downloads historical prices from Yahoo Finance (`yfinance`) for any ticker list and lookback window.
- **Risk model:** computes annualized expected returns and the covariance matrix from daily returns.
- **Three objectives:** maximize Sharpe ratio, minimize variance, or minimize risk for a target return.
- **Constraints:** a max-weight-per-asset cap; weights always sum to 100%.
- **Efficient frontier:** traces the true frontier by solving a minimum-variance problem at each target return, then overlays 2,000 random portfolios, the individual assets and the optimal portfolio.
- **Output:** expected return, volatility and Sharpe ratio, plus an allocation chart and a weights table that hides tiny weights.

## How the optimization works
`scipy.optimize.minimize` with **SLSQP** handles the constrained problem:

| Objective | Function minimized | Constraints |
|-----------|--------------------|-------------|
| Max Sharpe | −(Rₚ − R_f) / σₚ | Σw = 1, 0 ≤ wᵢ ≤ max weight |
| Min Variance | σₚ | Σw = 1, 0 ≤ wᵢ ≤ max weight |
| Target Return | σₚ | Σw = 1, Rₚ = target, bounds |

## Validation highlights
- Weights always sum to exactly 100%.
- With a 100% cap the optimizer concentrates in 2–3 assets, as unconstrained MPT predicts. With five assets and a 20% cap it correctly forces equal weights.
- Max Sharpe avoids putting everything in the single highest-return stock when that stock's volatility is high.

## Run it locally
```bash
pip install -r requirements.txt
cd "MGMT490 Project2"
streamlit run app.py
```

## Repo contents
```
MGMT490 Project2/
├── app.py                    # Streamlit app: data, optimization, charts
├── DRIVER_Documentation.md   # Build process: discover → represent → implement → validate → evolve → reflect
└── AI_Usage_Disclosure.md    # How AI tools were and weren't used
Video Explanation Transcript.pdf
```

## Tech
Python · pandas · NumPy · SciPy · yfinance · Plotly · Streamlit

---
Built by [Anthony Petrescu](https://www.linkedin.com/in/anthony-petrescu/) for MGMT 490 at Purdue · Finance + Computer Science '27
