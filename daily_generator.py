import yfinance as yf
import google.generativeai as genai
import json
import os
from datetime import datetime

# 1. 自动化配置
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)

# 监控的“大鱼”列表
STOCK_POOL = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "BABA", "PDD", "COIN"]

def get_market_data():
    results = []
    for ticker in STOCK_POOL:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d") # 多看几天趋势
            info = stock.info
            current_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_pct = ((current_close - prev_close) / prev_close) * 100
            
            results.append({
                "name": info.get('shortName', ticker),
                "ticker": ticker,
                "close": round(current_close, 2),
                "change": f"{round(change_pct, 2)}%",
                "trend": "向上突破" if change_pct > 0 else "向下试探"
            })
        except: continue
    
    # 挑选波动最大的那个作为今日“戏精”
    if results:
        return sorted(results, key=lambda x: abs(float(x['change'].replace('%',''))), reverse=True)[0]
    return {"name": "纳指", "ticker": "QQQ", "close": 440, "change": "0.5%"}

def generate_report(data):
    # 自动探测可用模型
    model_name = 'gemini-1.5-flash'
    try:
        model = genai.GenerativeModel(model_name)
    except:
        model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    你是一个隐居山林的金融奇才，外号“草鞋索罗斯”。
    今日监控到：{data['name']} ({data['ticker']}) 昨晚价格为 {data['close']}，涨跌幅为 {data['change']}。
    
    请写一份内容丰富的【土味内参】，要求包含以下板块（用土话讲干货）：
    1. 【星象复盘】：用一种极其离奇的修辞描述昨晚的走势。
    2. 【庄家心法】：分析为什么这帮“城里人”要这么拉升或砸盘（结合具体跌幅）。
    3. 【致富玄学】：给出一个具体的“支撑价”或“压力位”，但要用土话（比如：村口歪脖子树的价格）。
    4. 【今日忌宜】：宜做什么，忌做什么（比如：宜吃红薯补气，忌乱开杠杆）。
    
    字数要求：每个板块不少于50字。
    必须返回纯JSON格式，禁止任何解释文字，结构如下：
    {{
      "headline": "...",
      "xing_xiang": "...",
      "zhuang_jia": "...",
      "xuan_xue": "...",
      "ji_yi": "..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        txt = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(txt)
    except Exception as e:
        return {"headline": "天机不可泄露", "xing_xiang": "云里雾里看花。", "zhuang_jia": "深不可测。", "xuan_xue": "多看少动。", "ji_yi": "宜睡觉。"}

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
