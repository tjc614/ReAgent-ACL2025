import pandas as pd
import requests
import json
from datetime import datetime


def analyze_market_period(start_date, end_date):
    # 读取CSV文件
    df = pd.read_csv('al_combined_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    # 转换输入的日期字符串为datetime对象
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # 过滤日期范围内的数据
    mask = (df['datetime'].dt.date >= start_date.date()) & (df['datetime'].dt.date <= end_date.date())
    date_range_df = df.loc[mask]

    # 获取日期范围内的唯一日期
    unique_dates = date_range_df['datetime'].dt.date.unique()

    # 存储每天的预测结果
    daily_predictions = {}

    for date in unique_dates:
        # 获取当天9:00的数据
        morning_data = date_range_df[
            (date_range_df['datetime'].dt.date == date) &
            (date_range_df['datetime'].dt.time == pd.Timestamp('09:00:00').time())
            ]

        # 获取当天00:55的数据（实际是前一天夜盘的数据）
        early_morning_data = date_range_df[
            (date_range_df['datetime'].dt.date == date) &
            (date_range_df['datetime'].dt.time == pd.Timestamp('00:55:00').time())
            ]

        if not morning_data.empty:
            morning_row = morning_data.iloc[0]

            # 获取当前交易日的数据
            current_date = morning_row['datetime'].strftime('%Y-%m-%d')
            morning_open = morning_row['open']
            morning_volume = morning_row['volume']
            morning_turnover = morning_row['turnover']
            morning_open_interest = morning_row['open_interest']

            Baseurl = "https://api.claude-Plus.top"
            Skey = "sk-Sm6GJ9xzufAaOP0L05B125A7B0474924Ac9aD551C76b16Ef"

            system_content = (
                f"You are an experienced futures analyst. Your task is to analyze the market trends based on the policy and news for {current_date}."
            )

            user_content = (
                f"Current market data ({current_date} 09:00):\n"
                f"- Opening Price: {morning_open}\n"
                f"- Volume: {morning_volume}\n"
                f"- Turnover: {morning_turnover}\n"
                f"- Open Interest: {morning_open_interest}\n\n"
            )

            if not early_morning_data.empty:
                early_row = early_morning_data.iloc[0]
                user_content += (
                    f"Early morning data ({current_date} 00:55):\n"
                    f"- Price: {early_row['close']}\n"
                    f"- Volume: {early_row['volume']}\n"
                    f"- Turnover: {early_row['turnover']}\n"
                    f"- Open Interest: {early_row['open_interest']}\n\n"
                )

            user_content += (
                "Consider the following factors:\n"
                "1. Price changes between early morning (00:55) and opening (09:00)\n"
                "2. Volume and turnover trends\n"
                "3. Open interest changes\n"
                "4. Overall market sentiment\n\n"
                "Based on the above market data and considering the impact of latest policy and news, "
                "please provide your trading recommendation.\n\n"
                "Please output your answer in the following JSON format: "
                "{'Evaluation': 'Sell'} or {'Evaluation': 'Buy'} or {'Evaluation': 'No transaction'}."
            )

            payload = json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": system_content
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ]
            })

            url = Baseurl + "/v1/chat/completions"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {Skey}',
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.request("POST", url, headers=headers, data=payload)
                data = response.json()
                prediction = data['choices'][0]['message']['content']
                daily_predictions[current_date] = prediction
                print(f"Date: {current_date}")
                print(f"Prediction: {prediction}")
                print("-" * 50)
            except Exception as e:
                daily_predictions[current_date] = f"Error occurred: {str(e)}"

    return daily_predictions


# 使用函数
start_date = "2021-01-09"  # 开始日期
end_date = "2021-02-01"  # 结束日期
results = analyze_market_period(start_date, end_date)