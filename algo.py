import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import time
from PIL import Image

# Define a dictionary of valid usernames and passwords (replace with your own)
valid_users = {
    "harsh": "1234",
}

# Function to fetch live stock data
def fetch_live_stock_data(symbol, interval='1m'):
    try:
        live_data = yf.download(symbol, period="1d", interval=interval, prepost=True, group_by='ticker')
        return live_data.copy(), None  # Return both data and None for error_message
    except Exception as e:
        return None, f"Error fetching live stock data: {str(e)}"  # Return None for data and the error message

# Function to fetch live stock price
def fetch_live_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        live_price = stock.history(period="1d")["Close"].iloc[-1]
        return live_price, None  # Return live_price and None for price_error
    except Exception as e:
        return None, f"Error fetching live stock price: {str(e)}"  # Return None for live_price and the error message

# Function to calculate Exponential Moving Averages (EMAs)
def calculate_ema(data, ema_periods):
    for period in ema_periods:
        data[f'EMA_{period}'] = data['Close'].ewm(span=period).mean()

# Function to display error message
def display_error_message(message):
    st.markdown(f'<div class="trading-suggestion" style="background-color: red;">{message}</div>', unsafe_allow_html=True)

# Function to display candlestick chart with EMAs
def display_candlestick_with_emas(data, ema_periods, chart_title):
    # Create the main chart with the stock data and EMAs
    main_fig = go.Figure()

    main_fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlesticks',
    ))

    # Add the EMAs to the main chart
    for period in ema_periods:
        main_fig.add_trace(go.Scatter(
            x=data.index,
            y=data[f'EMA_{period}'],
            mode='lines',
            line=dict(width=2),
            name=f'EMA {period}'
        ))

    # Update the layout for the main chart
    main_fig.update_layout(
        title=chart_title,
        xaxis_title='Time',
        yaxis_title='Price',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    # Display the main chart
    st.plotly_chart(main_fig, use_container_width=True)

# Function to fetch live stock data and display it
def fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods):
    # Fetch live data here
    live_data, _ = fetch_live_stock_data(symbol)

    if live_data is not None:
        calculate_ema(live_data, ema_periods)  # Calculate EMAs

        # Display candlestick chart with EMAs
        display_candlestick_with_emas(live_data, ema_periods, chart_title)

        # Display trading suggestion
        st.markdown(f'<div class="trading-suggestion">{trading_suggestion}</div>', unsafe_allow_html=True)

        # Fetch and display live stock price
        stock_live_price, price_error = fetch_live_stock_price(symbol)
        if stock_live_price is not None:
            st.markdown(f'<h2 class="live-price">{live_price_label}: {stock_live_price:.2f}</h2>', unsafe_allow_html=True)
        if price_error:
            display_error_message(price_error)

        # Add Buy and Sell buttons
        order_type = st.radio("Select Order Type", ["Buy", "Sell"])

        if order_type == "Buy" or order_type == "Sell":
            if symbol in ["^NSEI", "^NSEBANK"]:
                lot_size = 15
            else:
                lot_size = 1500
            quantity = st.number_input(f"Enter Quantity (lot size: {lot_size})", min_value=1)
            if st.button("Place Order"):
                if order_type == "Buy":
                    order_message = f"Placed a Buy order for {quantity} lots of {symbol} at {stock_live_price:.2f} each."
                else:
                    order_message = f"Placed a Sell order for {quantity} lots of {symbol} at {stock_live_price:.2f} each."
                st.success(order_message)

# Main function to run the dashboard
def run_dashboard():
    # Custom CSS styles
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background: black; /* Change background color to black */
            color: white;
        }
        .live-price {
            font-size: 24px;
            text-align: center;
            margin-bottom: 10px;
        }
        .trading-suggestion {
            background-color: #FF6600;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    # Define page title and header image
    st.title("Algo Trading Dashboard")
    image = Image.open("img.jpg")  # Replace with your exhibition image
    st.image(image, use_column_width=True)

    # Continue with the Algo Trading Dashboard logic here

    # Sidebar for user input
    st.sidebar.header('Choose the Desired Option')

    # Option to select what to view
    view_option = st.sidebar.radio("Select an Option", ["Indices", "Stocks", "Global Markets"])

    # Define ema_periods here
    ema_periods = [10, 20, 50]  # You can modify this list as needed

    # Main loop to display charts and live prices
    while True:
        # Fetch live data here
        live_data, _ = fetch_live_stock_data('^NSEI')  # Default symbol for Nifty 50

        if view_option == "Indices":
            selected_index = st.sidebar.selectbox("Select an Index", ["Nifty 50", "Bank Nifty"])

            if selected_index == "Nifty 50":
                symbol = '^NSEI'
                chart_title = 'Nifty 50 Live Stock Data'
                live_price_label = "Nifty 50 Live Price"

                # Trading strategy based on opening prices (simplified)
                nifty_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == nifty_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < nifty_open:
                    trading_suggestion = "Market was down, and Nifty 50 opened higher. Suggest to Buy."

                elif previous_close > nifty_open:
                    trading_suggestion = "Market was up, and Nifty 50 opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_index == "Bank Nifty":
                symbol = '^NSEBANK'
                chart_title = 'Bank Nifty Live Stock Data'
                live_price_label = "Bank Nifty Live Price"

                # Trading strategy based on opening prices (simplified)
                banknifty_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == banknifty_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < banknifty_open:
                    trading_suggestion = "Market was down, and Bank Nifty opened higher. Suggest to Buy."

                elif previous_close > banknifty_open:
                    trading_suggestion = "Market was up, and Bank Nifty opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

        # Stocks
        elif view_option == "Stocks":
            selected_stock = st.sidebar.selectbox("Select a Stock", ["RELIANCE", "TCS", "Infosys", "HDFC Bank"])

            if selected_stock == "RELIANCE":
                symbol = 'RELIANCE.BO'
                chart_title = 'Reliance Industries Live Stock Data'
                live_price_label = "Reliance Live Price"

                # Trading strategy based on opening prices (simplified)
                reliance_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == reliance_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < reliance_open:
                    trading_suggestion = "Market was down, and Reliance opened higher. Suggest to Buy."

                elif previous_close > reliance_open:
                    trading_suggestion = "Market was up, and Reliance opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_stock == "TCS":
                symbol = 'TCS.BO'
                chart_title = 'Tata Consultancy Services Live Stock Data'
                live_price_label = "TCS Live Price"

                # Trading strategy based on opening prices (simplified)
                tcs_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == tcs_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < tcs_open:
                    trading_suggestion = "Market was down, and TCS opened higher. Suggest to Buy."

                elif previous_close > tcs_open:
                    trading_suggestion = "Market was up, and TCS opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_stock == "Infosys":
                symbol = 'INFY.BO'
                chart_title = 'Infosys Live Stock Data'
                live_price_label = "Infosys Live Price"

                # Trading strategy based on opening prices (simplified)
                infosys_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == infosys_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < infosys_open:
                    trading_suggestion = "Market was down, and Infosys opened higher. Suggest to Buy."

                elif previous_close > infosys_open:
                    trading_suggestion = "Market was up, and Infosys opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_stock == "HDFC Bank":
                symbol = 'HDFCBANK.BO'
                chart_title = 'HDFC Bank Live Stock Data'
                live_price_label = "HDFC Bank Live Price"

                # Trading strategy based on opening prices (simplified)
                hdfcbank_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == hdfcbank_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < hdfcbank_open:
                    trading_suggestion = "Market was down, and HDFC Bank opened higher. Suggest to Buy."

                elif previous_close > hdfcbank_open:
                    trading_suggestion = "Market was up, and HDFC Bank opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

        # Global Markets
        elif view_option == "Global Markets":
            selected_market = st.sidebar.selectbox("Select a Global Market", ["US 30", "Dow Jones", "Nasdaq", "S&P 500", "US 30 Futur"])

            if selected_market == "US 30":
                symbol = '^DJI'
                chart_title = 'Dow Jones Industrial Average Live Data'
                live_price_label = "Dow Jones Live Price"

                # Trading strategy based on opening prices (simplified)
                dow_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == dow_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < dow_open:
                    trading_suggestion = "Market was down, and Dow Jones opened higher. Suggest to Buy."

                elif previous_close > dow_open:
                    trading_suggestion = "Market was up, and Dow Jones opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_market == "Dow Jones":
                symbol = '^DJI'
                chart_title = 'Dow Jones Industrial Average Live Data'
                live_price_label = "Dow Jones Live Price"

                # Trading strategy based on opening prices (simplified)
                dow_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == dow_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < dow_open:
                    trading_suggestion = "Market was down, and Dow Jones opened higher. Suggest to Buy."

                elif previous_close > dow_open:
                    trading_suggestion = "Market was up, and Dow Jones opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_market == "Nasdaq":
                symbol = '^IXIC'
                chart_title = 'Nasdaq Composite Live Data'
                live_price_label = "Nasdaq Live Price"

                # Trading strategy based on opening prices (simplified)
                nasdaq_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == nasdaq_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < nasdaq_open:
                    trading_suggestion = "Market was down, and Nasdaq opened higher. Suggest to Buy."

                elif previous_close > nasdaq_open:
                    trading_suggestion = "Market was up, and Nasdaq opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_market == "S&P 500":
                symbol = '^GSPC'
                chart_title = 'S&P 500 Live Data'
                live_price_label = "S&P 500 Live Price"

                # Trading strategy based on opening prices (simplified)
                sp500_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == sp500_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < sp500_open:
                    trading_suggestion = "Market was down, and S&P 500 opened higher. Suggest to Buy."

                elif previous_close > sp500_open:
                    trading_suggestion = "Market was up, and S&P 500 opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

            elif selected_market == "US 30 Futur":
                symbol = 'YM=F'
                chart_title = 'Dow Jones Industrial Average Futures Live Data'
                live_price_label = "Dow Jones Futures Live Price"

                # Trading strategy based on opening prices (simplified)
                dow_future_open = live_data.iloc[0]['Open']
                previous_close = live_data.iloc[0]['Close']  # Close price of the previous day

                trading_suggestion = ""

                if previous_close == dow_future_open:
                    trading_suggestion = "Market was sideways. Suggest to Buy."

                elif previous_close < dow_future_open:
                    trading_suggestion = "Market was down, and Dow Jones Futures opened higher. Suggest to Buy."

                elif previous_close > dow_future_open:
                    trading_suggestion = "Market was up, and Dow Jones Futures opened lower. Suggest to Sell."

                fetch_and_display_stock_data(symbol, chart_title, trading_suggestion, live_price_label, ema_periods)

        # Wait for a few seconds before updating the data (you can change the sleep duration)
        time.sleep(30)

# Run the dashboard
if __name__ == "__main__":
    run_dashboard()
