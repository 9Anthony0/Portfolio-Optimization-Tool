import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import scipy.optimize as sco
import plotly.graph_objects as go
import plotly.express as px

# Ensure the page is wide for charts
st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

st.title("📈 Project 2: Investment Management")
st.markdown("### Path A: Portfolio Optimizer")
st.markdown("""
Welcome to the interactive Portfolio Optimizer! Adjust the assumptions in the **sidebar** to define your constraints, and the engine will instantly calculate the mathematically optimal allocation based on your chosen risk preferences.
---
""")

# Sidebar for Inputs
st.sidebar.header("1. Input Assumptions")

# Tickers
default_tickers = "AAPL, MSFT, GOOG, AMZN, NVDA, TSLA, META"
tickers_input = st.sidebar.text_input("Enter 5-15 Tickers (comma separated):", default_tickers)
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Timeframe
years = st.sidebar.slider("Years of Historical Data", 1, 10, 5)

# Risk Free Rate
rf = st.sidebar.number_input("Risk Free Rate (%)", min_value=0.0, value=2.0, step=0.1) / 100

st.sidebar.header("2. Constraint Settings")
max_weight = st.sidebar.slider("Max Weight per Asset (%)", 10, 100, 30) / 100.0

st.sidebar.header("3. Optimization Objective")
objective = st.sidebar.selectbox(
    "Select Objective:",
    ("Max Sharpe Ratio", "Min Volatility", "Target Return")
)

target_return = None
if objective == "Target Return":
    target_return = st.sidebar.number_input("Target Return Level (%)", min_value=-50.0, value=15.0, step=1.0) / 100

if len(tickers) < 5:
    st.warning("Please enter at least 5 tickers.")
else:
    # Function to fetch data
    @st.cache_data
    def get_data(tickers, years):
        start_date = pd.Timestamp.today() - pd.DateOffset(years=years)
        data = yf.download(tickers, start=start_date)['Close']
        data.dropna(inplace=True)
        return data

    st.write(f"Fetching data for: {', '.join(tickers)}")
    try:
        prices = get_data(tickers, years)
        if len(prices) == 0:
            st.error("No data fetched. Check tickers.")
            st.stop()
            
        # Display Historical Price Data
        st.markdown("### 📈 Historical Price Data")
        with st.expander("View Raw Data Dashboard"):
            st.dataframe(prices, use_container_width=True)
            
        chart_type = st.radio("Select Chart View:", ["Actual Prices ($)", "Normalized Growth (Base 100)"], horizontal=True)
        
        if chart_type == "Normalized Growth (Base 100)":
            plot_data = prices / prices.iloc[0] * 100
            y_label = 'Price Level (Base 100)'
            title_text = 'Normalized Historical Performance'
        else:
            plot_data = prices
            y_label = 'Stock Price (USD)'
            title_text = 'Actual Historical Prices'
            
        fig_prices = px.line(
            plot_data, 
            labels={'value': y_label, 'index': 'Date', 'variable': 'Ticker'}
        )
        fig_prices.update_layout(height=450, template='plotly_white', title=dict(text=title_text, font=dict(size=20)))
        st.plotly_chart(fig_prices, use_container_width=True)
        st.markdown("---")

        returns = prices.pct_change().dropna()

        # Calculate Expected Returns and Covariance Matrix
        # Using Historical Average Annualized Returns
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252

        num_assets = len(tickers)

        # Optimization Functions
        def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
            returns = np.sum(mean_returns * weights)
            std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return std, returns

        def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
            p_var, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
            return -(p_ret - risk_free_rate) / p_var

        def portfolio_volatility(weights, mean_returns, cov_matrix):
            return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]

        # Constraints and Bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.0, max_weight) for asset in range(num_assets))

        if objective == "Target Return":
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: portfolio_annualised_performance(x, mean_returns, cov_matrix)[1] - target_return}
            )

        # Optimize!
        initial_guess = num_assets * [1. / num_assets]
        
        opt_results = None
        
        if objective == "Max Sharpe Ratio":
            opt_results = sco.minimize(neg_sharpe_ratio, initial_guess, args=(mean_returns, cov_matrix, rf),
                                    method='SLSQP', bounds=bounds, constraints=constraints)
        elif objective == "Min Volatility":
            opt_results = sco.minimize(portfolio_volatility, initial_guess, args=(mean_returns, cov_matrix),
                                    method='SLSQP', bounds=bounds, constraints=constraints)
        elif objective == "Target Return":
            opt_results = sco.minimize(portfolio_volatility, initial_guess, args=(mean_returns, cov_matrix),
                                    method='SLSQP', bounds=bounds, constraints=constraints)

        if not opt_results.success:
            st.error("Optimization failed to find a solution. Try relaxing the max weight or target return constraints.")
        else:
            opt_weights = opt_results.x
            opt_vol, opt_ret = portfolio_annualised_performance(opt_weights, mean_returns, cov_matrix)
            opt_sharpe = (opt_ret - rf) / opt_vol

            st.markdown("### 🏆 Optimization Results")
            st.success(f"**Optimization Successful!** Objective: {objective}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Expected Annual Return", f"{opt_ret*100:.2f}%")
            col2.metric("Annual Volatility (Risk)", f"{opt_vol*100:.2f}%")
            col3.metric("Sharpe Ratio", f"{opt_sharpe:.2f}")

            # Display Optimal Weights
            weights_df = pd.DataFrame(data={'Weight (%)': [round(w * 100, 2) for w in opt_weights]}, index=tickers)
            weights_df = weights_df[weights_df['Weight (%)'] > 0.01].sort_values(by="Weight (%)", ascending=False)
            
            st.markdown("#### Optimal Portfolio Weights")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(weights_df.style.format("{:.2f}%").background_gradient(cmap='viridis'), use_container_width=True)
            with col2:
                # Pie Chart
                fig_pie = go.Figure(data=[go.Pie(
                    labels=weights_df.index, 
                    values=weights_df['Weight (%)'], 
                    hole=.4,
                    textinfo='label+percent',
                    hoverinfo='label+percent',
                    marker=dict(colors=px.colors.qualitative.Prism)
                )])
                fig_pie.update_layout(
                    height=400, 
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05)
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📊 Efficient Frontier")

            # Efficient Frontier Generation
            with st.spinner("Generating Efficient Frontier (calculating curve)..."):
                num_portfolios = 800
                results = np.zeros((3, num_portfolios))
                weights_record = []
                
                for i in range(num_portfolios):
                    weights = np.random.random(num_assets)
                    weights /= np.sum(weights)
                    weights_record.append(weights)
                    p_std, p_ret = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
                    results[0,i] = p_std
                    results[1,i] = p_ret
                    results[2,i] = (p_ret - rf) / p_std
                
                # Compute actual frontier line with a lighter load (15 points instead of 50 to drastically reduce lag)
                target_returns = np.linspace(mean_returns.min(), mean_returns.max(), 12)
                efficient_vols = []
                efficient_returns = []
                for tr in target_returns:
                    cons_ef = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                               {'type': 'eq', 'fun': lambda x: portfolio_annualised_performance(x, mean_returns, cov_matrix)[1] - tr})
                    res_ef = sco.minimize(portfolio_volatility, initial_guess, args=(mean_returns, cov_matrix), method='SLSQP', bounds=bounds, constraints=cons_ef)
                    if res_ef.success:
                        efficient_vols.append(res_ef.fun)
                        efficient_returns.append(tr)

                fig_ef = go.Figure()

                # Simulated Portfolios
                fig_ef.add_trace(go.Scatter(
                    x=results[0,:],
                    y=results[1,:],
                    mode='markers',
                    marker=dict(
                        color=results[2,:],
                        colorscale='Viridis',
                        showscale=True,
                        size=5,
                        colorbar=dict(title='Sharpe Ratio')
                    ),
                    name='Random Portfolios'
                ))

                # Efficient Frontier Line
                fig_ef.add_trace(go.Scatter(
                    x=efficient_vols,
                    y=efficient_returns,
                    mode='lines',
                    line=dict(color='firebrick', width=3),
                    name='Efficient Frontier Line (With Constraints)'
                ))

                # Optimal Point
                fig_ef.add_trace(go.Scatter(
                    x=[opt_vol],
                    y=[opt_ret],
                    mode='markers',
                    marker=dict(color='red', size=15, symbol='star'),
                    name=f'Optimal: {objective}'
                ))
                
                # Plot individual assets
                asset_vols = np.sqrt(np.diag(cov_matrix))
                fig_ef.add_trace(go.Scatter(
                    x=asset_vols,
                    y=mean_returns,
                    mode='markers+text',
                    text=tickers,
                    textposition="top center",
                    marker=dict(color='black', size=10, symbol='diamond'),
                    name='Individual Stocks'
                ))

                fig_ef.update_layout(
                    title=dict(text='Portfolio Efficient Frontier', font=dict(size=24)),
                    xaxis_title='Volatility (Risk) - Standard Deviation',
                    yaxis_title='Expected Annual Return',
                    height=750,
                    hovermode='closest',
                    template='plotly_white',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.05,
                        xanchor="center",
                        x=0.5,
                        bgcolor="rgba(0,0,0,0)",
                        font=dict(size=14)
                    ),
                    margin=dict(t=120, b=50, l=50, r=50)
                )

                st.plotly_chart(fig_ef, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
