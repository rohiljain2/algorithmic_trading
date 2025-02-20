import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from strategies.stock_scanner import StockScanner

# Custom CSS for styling
def local_css():
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight:bold !important;
            color: #1f77b4 !important;
            margin-bottom: 20px !important;
        }
        .stock-score {
            font-size:24px !important;
            color: #2ecc71 !important;
            font-weight:bold !important;
        }
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .metric-label {
            font-size:16px !important;
            color: #666666 !important;
            font-weight:500 !important;
        }
        .metric-value {
            font-size:24px !important;
            color: #2c3e50 !important;
            font-weight:bold !important;
        }
        .dashboard-title {
            text-align: center;
            font-size:40px !important;
            font-weight:bold !important;
            color: #2c3e50 !important;
            margin-bottom: 30px !important;
            padding: 20px;
            background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            height: 50px;
            font-size: 20px !important;
            font-weight: bold;
            background-color: #1f77b4;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

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
        title=dict(
            text=f'Monte Carlo Simulation - {symbol}',
            font=dict(size=24)
        ),
        xaxis_title='Trading Days',
        yaxis_title='Stock Price ($)',
        showlegend=True,
        height=500,
        template='plotly_white',
        margin=dict(t=100),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_metrics_gauge(value: float, title: str, min_val: float, max_val: float):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': "#1f77b4"},
            'bgcolor': "white",
            'steps': [
                {'range': [min_val, (max_val-min_val)/3], 'color': "rgba(255, 99, 132, 0.3)"},
                {'range': [(max_val-min_val)/3, 2*(max_val-min_val)/3], 'color': "rgba(255, 205, 86, 0.3)"},
                {'range': [2*(max_val-min_val)/3, max_val], 'color': "rgba(75, 192, 192, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(t=30, b=0),
        paper_bgcolor="white",
        font={'size': 16}
    )
    return fig

def main():
    st.set_page_config(layout="wide", page_title="Trading Dashboard")
    local_css()
    
    st.markdown('<div class="dashboard-title">Algorithmic Trading Dashboard</div>', unsafe_allow_html=True)
    
    # Initialize scanner
    scanner = StockScanner()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button('Scan Market for Opportunities'):
            with st.spinner('Analyzing S&P 500 stocks...'):
                opportunities = scanner.scan_stocks()
            
            if opportunities:
                for opp in opportunities:
                    metrics = opp['metrics']
                    symbol = opp['symbol']
                    
                    st.markdown(f'<div class="big-font">{symbol}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stock-score">Overall Score: {opp["score"]:.2f}</div>', unsafe_allow_html=True)
                    
                    # Create two columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if 'price_paths' in opp:
                            mc_fig = create_monte_carlo_plot(symbol, opp['price_paths'], metrics['current_price'])
                            st.plotly_chart(mc_fig, use_container_width=True)
                    
                    with col2:
                        # Key metrics in cards
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-label">Current Price</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">${metrics["current_price"]:.2f}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-label">Monthly Return</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{metrics["monthly_return"]:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Gauge charts
                        sharpe_gauge = create_metrics_gauge(metrics['sharpe_ratio'], "Sharpe Ratio", 0, 3)
                        st.plotly_chart(sharpe_gauge, use_container_width=True)
                        
                        momentum_gauge = create_metrics_gauge(metrics['momentum'], "Momentum (RSI)", 0, 100)
                        st.plotly_chart(momentum_gauge, use_container_width=True)
                    
                    # Additional metrics in columns with cards
                    mc1, mc2, mc3 = st.columns(3)
                    with mc1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Expected Return (1Y)</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{metrics["expected_return"]*100:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with mc2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">Probability of Positive Return</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{metrics["prob_positive"]*100:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with mc3:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.markdown('<div class="metric-label">95% VaR</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="metric-value">{metrics["var_95"]*100:.1f}%</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('---')
            else:
                st.warning("No high-quality opportunities found.")

if __name__ == "__main__":
    main() 