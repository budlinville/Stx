import os
from dotenv import load_dotenv

from trading_bot.trading_bot_base import TradingBotBase

def main():
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    bot = TradingBotBase(email, password)
    market_data = bot.get_market_data()

    # f = open("temp.txt", "a")
    # f.write(str(market_data))
    # f.close()

    market_id = list(market_data.keys())[0]
    order = bot.create_order(market_id, 1, 64, action="BUY", order_type="LIMIT")
    print(order['id'])
    bot.cancel_order(order['id'])

if __name__ == '__main__':
    load_dotenv()
    main()
