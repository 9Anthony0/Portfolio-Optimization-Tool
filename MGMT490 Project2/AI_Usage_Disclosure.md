# AI Usage Disclosure

**Project Name:** Project 2: Investment Management Application (Path A: Portfolio Optimizer)
**Student Name:** [Your Name Here]

## Declaration of Generative AI Use

In accordance with course policies and the DRIVER™ Best Practices Guide, I am disclosing the use of Generative AI in the development of this project.

### AI Tool(s) Used
*   **Model:** Google DeepMind's Antigravity Agent (Gemini Pro)

### Purpose and Extent of Usage

**1. Brainstorming and Structural Planning (DISCOVER & DEFINE)**
AI was used to structure the initial project architecture. I used it to outline the required Streamlit elements and determine the optimal Python libraries (`scipy.optimize` vs `PyPortfolioOpt`) for demonstrating constraint-based optimization clearly.

**2. Boilerplate Code Generation (IMPLEMENT)**
I requested AI to generate foundational code snippets for the Streamlit UI, such as setting up the sidebar sliders, and standard boilerplate for downloading data using `yfinance`. 

**3. Mathematical Syntax and Optimization Logic**
Mean-Variance Optimization requires exact mathematical vectorization. AI was incredibly helpful in translating my goal (e.g., "Minimize Variance given a set of bounds and constraints") into the specific syntax required by `scipy.optimize.minimize`, including the creation of lambda functions for weight constraints. 

**4. Data Visualization**
AI assisted in writing the Plotly Scatter and Line plot code to properly layer individual assets, randomly generated portfolios, and the statistically rigorous Efficient Frontier curve on the same graph layout.

### Human Oversight and Validation (VALIDATE & EVOLVE)
As the "Pilot-in-Command", all AI-generated logic and outputs were reviewed, tested, and validated by me. I manually verified the logic:
*   Confirmed that weights output by the optimizer actively sum to 100%.
*   Ensured that boundary constraints accurately alter the portfolio (e.g., stopping Apple from claiming 100% of the portfolio).
*   Verified that expected returns derived from Yahoo Finance align with historical performance reasonably.
*   The final interpretation of the Efficient Frontier and financial trade-offs in the recorded video are entirely my own words and financial judgement.
