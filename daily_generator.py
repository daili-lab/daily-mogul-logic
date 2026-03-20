import yfinance as yf
import google.generativeai as genai
import json
import os
from datetime import datetime

# 1. 自动配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)

def get_market_data():
    try:
        stock = yf.Ticker("NVDA") # 先拿英伟达试手
        hist = stock.history(period="2d")
        current_close = hist['Close'].iloc[-1]
        change_pct = ((current_close - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        return {"name": "英伟达", "ticker": "NVDA", "close": round(current_close, 2), "change": f"{round(change_pct, 2)}%"}
    except:
        return {"name": "美股大盘", "ticker": "SPY", "close": 500, "change": "1%"}

def generate_report(data):
    # 2. 自动试错模型名，哪个能用用哪个
    target_models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    model = None
    
    for m_name in target_models:
        try:
            model = genai.GenerativeModel(m_name)
            # 试着打个招呼
            test_res = model.generate_content("hi")
            if test_res: break
        except:
            continue

    prompt = f"数据：{data['name']}涨跌{data['change']}。写一份给山沟少年的土味内参，只要JSON格式：{{'tian_shi':'...','di_li':'...','ren_he':'...'}}"
    
    try:
        response = model.generate_content(prompt)
        # 强制清理格式
        txt = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(txt)
    except:
        return {"tian_shi": "天干物燥，小心火烛。", "di_li": "地脉波动，宜守不宜攻。", "ren_he": "和气生财，莫与人争。"}

def main():
    stock_data = get_market_data()
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
