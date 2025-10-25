import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import openpyxl
import re
import altair as alt

class Trade:
    def __init__(self, symbol, deal_in, deal_out, volume, time_in, time_out, status, strategy):
        self.symbol = symbol
        self.deal_in = deal_in
        self.deal_out = deal_out
        self.volume = volume
        self.time_in = time_in
        self.time_out = time_out
        self.status = status
        self.strategy = strategy
        self.time_elapsed = self.time_out - self.time_in
    
    def print_info(self):
        print(f'Strategy: {self.strategy}\nSymbol: {self.symbol}\nVolume: {self.volume}\nTime In: {self.time_in}\nTime Out: {self.time_out}\nTime elapsed: {self.time_elapsed}\nStatus: {self.status}\n')
    
    def convert(self):
        d = {"start": self.time_in,"end": self.time_out, "strategy":self.strategy, "status":self.status}
        return d

st.set_page_config(
    page_title="Strategy analyser",
    page_icon=":chart_with_upwards_trend:",
    layout='wide'
)

uploaded_file = st.file_uploader("Pick a file.")

if uploaded_file is not None:

    try:
        df=pd.read_excel(uploaded_file, skiprows=6)
        # display(df['Inputs:'])
        # print(list(df['Inputs:']))
        start = df.index[df['Inputs:'] == 'Deals'].tolist()[0]
        end = len(df)+7
        df = pd.read_excel(uploaded_file, skiprows=start+8, nrows=end-start-2)

        # st.dataframe(df)

        list_of_trades = []
        for index, row in df.iterrows():
            if row['Direction'] == 'in':
                datetime_str_in = row['Time']
                datetime_obj_in = datetime.strptime(datetime_str_in, '%Y.%m.%d %H:%M:%S')

                pattern = r'Taken by (\w+) v\d+\.\d+'
                extracted_text = ''
                match = re.search(pattern, row['Comment'])
                if match:
                    extracted_text = match.group(1)
                    # print(extracted_text)
                
                elif row['Comment'] == 'SALAD':
                    extracted_text = 'SALAD'

                found_out = False
                i = 0
                out = []
                while found_out == False:

                    if index+i == len(df):
                        found_out = True
                        # print(f"There is no corresponding out trade for this trade")
                        break

                    check_row = df.iloc[index + i]

                    if check_row['Symbol'] == row['Symbol'] and \
                        ('tp' in check_row['Comment'] or 'sl' in check_row['Comment']) and \
                            check_row['Volume'] == row['Volume'] and \
                                ((row['Type'] == 'buy' and check_row['Type'] == 'sell') or (row['Type'] == 'sell' and check_row['Type'] == 'buy')):
                        out.append(check_row)
                        found_out = True
                        # print(f"Corresponding out trade found.")
                    else:
                        i = i + 1
                
                if out != []:
                    datetime_str_out = out[0]['Time']
                    datetime_obj_out = datetime.strptime(datetime_str_out, '%Y.%m.%d %H:%M:%S')
                    time_elapsed = datetime_obj_out - datetime_obj_in
                    status = ''

                    if 'tp' in check_row['Comment']:
                        status = 'TP'
                    elif 'sl' in check_row['Comment']:
                        status = 'SL'

                    pnl_1 = row['Commission'] + row['Swap'] + row['Profit']
                    pnl_2 = check_row['Commission'] + check_row['Swap'] + check_row['Profit']
                    pnl = pnl_1 + pnl_2
                    newrow = {
                        'symbol': row['Symbol'],
                        'volume': row['Volume'],
                        'pnl': pnl,
                        'strategy': extracted_text,
                        'duration': time_elapsed,
                        'time_in': datetime_obj_in,
                        'time_out': datetime_obj_out,
                        'status': status
                    }

                    list_of_trades.append(newrow)

        trades_df = pd.DataFrame(list_of_trades)
        st.dataframe(trades_df)

        @st.cache_data
        def convert_for_download(df):
            return df.to_csv().encode("utf-8")

        datetime_stamp = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"

        if st.button("Process files."):
            csv = convert_for_download(trades_df)
            st.download_button(
                label="Download output as CSV.",
                data=csv,
                file_name=f'processed_report_{datetime_stamp}.csv',
                on_click="ignore",
                type="primary",
                mime='text/csv',
                icon=":material/download:",
            )

            st.title("Trade Performance Dashboard")

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            win_lose_counts = trades_df["status"].value_counts().reset_index()
            win_lose_counts.columns = ["Status", "Count"]
            win_lose_counts["Percent"] = win_lose_counts["Count"] / win_lose_counts["Count"].sum() * 100

            pie = alt.Chart(win_lose_counts).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status", type="nominal"),
                tooltip=["Status", "Count"]
            ).properties(title="Win Rate")

            text = pie.mark_text(radius=90, size=14).encode(
                text=alt.Text("Percent:Q", format=".1f")
            )

            col1.altair_chart(pie + text, use_container_width=True)


            df_sorted = trades_df.sort_values("time_in").reset_index(drop=True)
            df_sorted["cumulative"] = df_sorted["pnl"].cumsum()

            # st.dataframe(df_sorted)

            line_chart = alt.Chart(df_sorted).mark_line(point=True).encode(
                x=alt.X("time_in:T", title="Time"),
                y=alt.Y("cumulative:Q", title="Cumulative Profit"),
                tooltip=["time_in", "cumulative"]
            ).properties(title="Cumulative Profit Over Time")

            col2.altair_chart(line_chart, use_container_width=True)

            trades_df["duration_in_min"] = (trades_df["time_out"] - trades_df["time_in"]).dt.total_seconds() / 60  # in minutes

            scatter_chart = alt.Chart(trades_df).mark_circle(size=60).encode(
                x=alt.X("duration_in_min:Q", title="Trade Duration (min)"),
                y=alt.Y("pnl:Q", title="Profit / Loss"),
                color=alt.Color("status:N"),
                tooltip=["pnl", "duration_in_min", "status"]
            ).properties(title="Profit vs Trade Duration")

            col3.altair_chart(scatter_chart, use_container_width=True)

            st.title("Performing simulations")
            col5, col6 = st.columns(2)
            simulations = []
            total_trades = len(trades_df)
        
            # st.dataframe(trades_df)

            for _ in range(10000):
                n_trades = np.random.randint(int(0.5 * total_trades), total_trades + 1)
                sampled = trades_df.sample(n=n_trades, replace=False)
                simulations.append(
                    round(
                        sampled["pnl"].sum(), 2
                    )
                )

            sim_df = pd.DataFrame({"Total_Profit": simulations})
            mean_profit = sim_df["Total_Profit"].mean()
            std_profit = sim_df["Total_Profit"].std()

            percentiles = np.percentile(sim_df["Total_Profit"], [10, 25, 75, 90])
            p10, p25, p70, p90 = percentiles

            histogram = alt.Chart(sim_df).mark_bar().encode(
                alt.X('Total_Profit:Q',bin=alt.Bin(maxbins=50), title='PnL'),
                alt.Y('count():Q',title='Frequency')
            ).properties(
                title='Histogram of profits'
            )

            mean_line = alt.Chart(pd.DataFrame({'mean_profit': [mean_profit]})).mark_rule(
                color='red', strokeDash=[5, 5]
            ).encode(x='mean_profit:Q')

            col5.altair_chart(histogram + mean_line, use_container_width=True)

            summary_df = pd.DataFrame({
                "Statistic": [
                    "mean",
                    "standard_deviation",
                    "10%",
                    "25%",
                    "75%",
                    "90%"
                ],
                "Value": [
                    mean_profit,
                    std_profit,
                    p10,
                    p25,
                    p70,
                    p90
                ]
            })

            col6.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.warning("The file uploaded is not readable. Try again.")