import yfinance as yf
import google.generativeai as genai
import json
import os
from datetime import datetime

# 配置 Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)

# 备选股票池（你可以随心增加）
STOCK_POOL = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "BABA", "PDD"]

def get_market_data():
    best_story_stock = None
    max_change = 0
    for ticker in STOCK_POOL:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) < 2: continue
            prev_close = hist['Close'].iloc[-2]
            current_close = hist['Close'].iloc[-1]
            change_pct = ((current_close - prev_close) / prev_close) * 100
            if abs(change_pct) > abs(max_change):
                max_change = change_pct
                best_story_stock = {
                    "ticker": ticker, 
                    "name": stock.info.get('shortName', ticker), 
                    "close": round(current_close, 2), 
                    "change": f"{round(change_pct, 2)}%"
                }
        except: continue
    return best_story_stock

def generate_report(data):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    角色：你是一个在山沟里修老手电筒、却偷偷通过收音机听行情、外号“扫地僧”的高人。
    数据：昨晚 {data['name']} ({data['ticker']}) 价格是 {data['close']}，涨跌幅为 {data['change']}。
    任务：写一份给村里卖了牛进城闯荡少年的“土味内参”。
    要求：
    1. 【天时】：吐槽昨晚这股的表现（用土话，如：像二踢脚、像霜打的茄子）。
    2. 【地利】：给一个玄乎的看多理由和扎心的看空风险。
    3. 【人和】：今日玄学小贴士（宜/忌）。
    4. 严禁提到iPad、电脑等数码产品，要符合山沟少年的认知。
    格式：必须只返回纯JSON格式，不要有任何多余文字，结构如下：{{"tian_shi": "...", "di_li": "...", "ren_he": "..."}}
    """
    response = model.generate_content(prompt)
    clean_text = response.text.strip().replace('```json', '').replace('```', '')
    return json.loads(clean_text)

def main():
    stock_data = get_market_data()
    if not stock_data: return
    report_content = generate_report(stock_data)
    final_output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "stock": stock_data,
        "content": report_content
    }
    with open("today.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
