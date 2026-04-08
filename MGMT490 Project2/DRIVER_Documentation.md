# DRIVER™ Best Practices Guide: Project 2 Portfolio Optimizer

This document outlines the systematic process used to build the Portfolio Optimizer application, adhering to the DRIVER framework.

## 1. DISCOVER & DEFINE

**Objective**: Build a portfolio optimization tool that accepts multiple tickers, allows adjustment of constraints and risk preferences, and visually demonstrates how the optimal portfolio changes.

*   **Requirements**:
    *   Accept 5-15 stock tickers.
    *   Retrieve historical price data (last 5 years).
    *   Calculate expected returns and covariance (risk).
    *   Optimize based on user-defined objectives (Max Sharpe, Min Variance, Target Return).
    *   Allow the user to adjust constraints (max weight per stock).
    *   Visualize the Efficient Frontier.
*   **Success Criteria**: The application runs successfully as a Streamlit module, produces accurate weights that sum to 100%, generates a visually appealing Efficient Frontier that accurately depicts individual stocks plotted alongside theoretical portfolios, and allows constraint modifications in real-time.
*   **Constraints**: Application must run computationally fast despite the complex constrained optimization using `scipy.optimize`. 

## 2. REPRESENT

**Solution Structure & Workflow**:
1.  **Input Layer** (Streamlit Sidebar): Users provide Tickers, History Length, Constraints (Max Weight), and the Optimization Objective.
2.  **Data Layer**: `yfinance` module queries Yahoo Finance for Adjusted Close prices spanning the timeframe specified. Return data is extracted and calculated using percent change.
3.  **Math Layer**: Compute average annualized returns and the covariance matrix.
4.  **Optimization Module**: `scipy.optimize.minimize` searches for optimal portfolio weights using the Sequential Least SQuares Programming (SLSQP) method to enforce bounds (0, max_weight) and constraints (sum of weights = 1, and optional target return).
5.  **Visualization Layer**: Plotly charts generate a pie chart of the chosen portfolio and a scatter plot of the Efficient Frontier line, individual assets, random portfolios, and the specific optimal portfolio.

**AI Collaboration vs. Human Judgment**:
*   *AI was leveraged* for boilerplate Streamlit UI code, scaffolding the `scipy.optimize` objective math (like negative Sharpe functions), and quickly drafting the Plotly logic to overlay random portfolios and an optimal line.
*   *Human judgment was maintained* to dictate how the Efficient Frontier line should be drawn using target returns, verifying that weights correctly equal 100%, and organizing the Streamlit layout logically.

## 3. IMPLEMENT

*   **Execution**: We incrementally created the application. First, data retrieval was verified. Second, optimization logic was coded and tested in isolation by sending test covariance matrices. Finally, everything was united under the `streamlit` wrapper.
*   **The R-I Loop (Represent ↔ Implement)**: Initially, the plan was just to plot random portfolio configurations. However, during execution, we realized an actual frontier curve (a line representing minimum variance given a fixed set of target returns) was much more statistically rigorous. We looped back to representation and updated our Plotly implementation to loop through `target_returns` to generate points on the optimal curve explicitly.
*   **Code as a Logic Check**: Using `scipy.optimize` forced exactness. We had to ensure bounds matched the scale of weights `(0.0, 1.0)` and that risk-free rate was applied correctly to the Sharpe Ratio matrix.

## 4. VALIDATE

*   **Financial Principles Check**: Does the optimized portfolio obey structural constraints? Yes, the weights always sum to Exactly 1.00 (`100%`).
*   **Reasonableness**: Are expected returns realistic? The expected returns strictly depend on historical prices. When tested against highly volatile tech stocks, the Max Sharpe Ratio accurately balanced risk, avoiding 100% allocation into a single asset due to high individual volatility despite higher expected returns. 
*   **Boundary Testing**: Stress-testing edge cases: Setting the max weight constraint to 100% reverted the optimal portfolio to standard unconstrained optimization, naturally clustering weights into 2-3 optimal assets. Reducing the max weight constraint to `20%` (for exactly 5 assets) forced all asset weights to distribute identically (`20%` equal weight).
*   **Data Integrity**: Data sourced directly from Yahoo Finance provides verified historical Adjusted Closing equivalents.

## 5. EVOLVE

*   **Refinement**: We realized that creating 2,000 random portfolios for the scatter plot could cause minor lag depending on CPU performance. We wrapped the optimization loop in a `st.spinner()` indicator so the user has visual feedback that complex math is calculating. 
*   **Optimization**: Filtered out fractional weights (`< 0.01%`) from the summary tables so the user views only meaningful allocations rather than micro-fractions that occur naturally in SLSQP bounds searching.

## 6. REFLECT

*   **Learnings Captured**: 
    1.  *Tool Use*: Streamlit's caching (`@st.cache_data`) is incredibly necessary when dealing with external API calls (like `yfinance`) to avoid excessive data fetching on every slider adjustment.
    2.  *Knowledge Build*: We solidified an understanding that **Min Variance** portfolios explicitly dismiss expected return in favor of the lowest aggregate risk, leading to the left-most tip of the Efficient Frontier, while **Target Return** traces the line higher.
*   **Reusability**: The core `scipy.optimize` functions (`portfolio_annualised_performance`, `neg_sharpe_ratio`, `portfolio_volatility`) are highly generalized and can be detached from Streamlit and reused in any future Python notebook or CLI tool requiring basic Mean-Variance Optimization.
