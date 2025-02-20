import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from strategies.stock_scanner import StockScanner
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_monte_carlo_plot(symbol: str, price_paths: np.ndarray, current_price: float):
    """Create Monte Carlo simulation plot using Plotly"""
    fig = go.Figure()
    
    # Plot a subset of paths
    num_paths_to_plot = 100
    step = len(price_paths[0]) // num_paths_to_plot
    
    # Add simulation paths
    for path in price_paths.T[::step]:
        fig.add_trace(go.Scatter(
            y=path,
            mode='lines',
            opacity=0.1,
            line=dict(color='blue', width=0.5),
            showlegend=False
        ))
    
    # Add mean path
    mean_path = price_paths.mean(axis=1)
    fig.add_trace(go.Scatter(
        y=mean_path,
        mode='lines',
        line=dict(color='red', width=2),
        name='Mean Path'
    ))
    
    # Add confidence intervals
    percentile_5 = np.percentile(price_paths, 5, axis=1)
    percentile_95 = np.percentile(price_paths, 95, axis=1)
    
    fig.add_trace(go.Scatter(
        y=percentile_95,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        y=percentile_5,
        mode='lines',
        fill='tonexty',
        line=dict(width=0),
        name='90% Confidence Interval',
        fillcolor='rgba(128, 128, 128, 0.2)'
    ))
    
    # Add current price line
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="green",
        name="Current Price"
    )
    
    fig.update_layout(
        title=f'Monte Carlo Simulation - {symbol} Price Projections (1 Year)',
        xaxis_title='Trading Days',
        yaxis_title='Stock Price ($)',
        showlegend=True,
        height=500
    )
    
    return fig

def create_metrics_gauge(value: float, title: str, min_val: float, max_val: float):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, (max_val-min_val)/3], 'color': "red"},
                {'range': [(max_val-min_val)/3, 2*(max_val-min_val)/3], 'color': "yellow"},
                {'range': [2*(max_val-min_val)/3, max_val], 'color': "green"}
            ]
        }
    ))
    
    fig.update_layout(height=200)
    return fig

def main():
    st.set_page_config(layout="wide")
    st.title('Algorithmic Trading Dashboard')
    
    # Initialize scanner
    scanner = StockScanner()
    
    if st.button('Scan Market'):
        with st.spinner('Scanning S&P 500 stocks...'):
            opportunities = scanner.scan_stocks()
        
        if opportunities:
            for opp in opportunities:
                metrics = opp['metrics']
                symbol = opp['symbol']
                
                # Create expandable section for each stock
                with st.expander(f"{symbol} - Score: {opp['score']:.2f}", expanded=True):
                    # Create two columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Monte Carlo simulation plot
                        if 'price_paths' in opp:
                            mc_fig = create_monte_carlo_plot(
                                symbol,
                                opp['price_paths'],
                                metrics['current_price']
                            )
                            st.plotly_chart(mc_fig, use_container_width=True)
                    
                    with col2:
                        # Metrics
                        st.metric("Current Price", f"${metrics['current_price']:.2f}")
                        st.metric("Monthly Return", f"{metrics['monthly_return']:.1f}%")
                        
                        # Create gauge charts for key metrics
                        sharpe_gauge = create_metrics_gauge(
                            metrics['sharpe_ratio'],
                            "Sharpe Ratio",
                            0,
                            3
                        )
                        st.plotly_chart(sharpe_gauge, use_container_width=True)
                        
                        momentum_gauge = create_metrics_gauge(
                            metrics['momentum'],
                            "Momentum (RSI)",
                            0,
                            100
                        )
                        st.plotly_chart(momentum_gauge, use_container_width=True)
                    
                    # Additional metrics in columns
                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        st.metric("Expected Return (1Y)", 
                                f"{metrics['expected_return']*100:.1f}%")
                    with mc2:
                        st.metric("Probability of Positive Return",
                                f"{metrics['prob_positive']*100:.1f}%")
                    with mc3:
                        st.metric("95% VaR",
                                f"{metrics['var_95']*100:.1f}%")
        else:
            st.warning("No high-quality opportunities found.")

if __name__ == "__main__":
    main() 