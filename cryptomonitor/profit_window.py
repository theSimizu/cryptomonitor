import json
import tkinter as tk
from cryptomonitor.coingecko import CoinGecko


cg = CoinGecko()

f = open('coins_list.json', 'r')
coin_json = json.load(f)
f.close()

coins_id_key = {coin['id']: coin for coin in coin_json}
coins_name_key = {coin['name']: coin for coin in coin_json}


class TransactionsBox:
    def __init__(self, window, coin, index, frame_text, fg) -> None:
        self.upper = window
        self.wallet = window.wallet
        symbol = window.symbol
        multiplier = window.multiplier
        padxLeft = (7, 20)
        padxMiddle = 22
        padxRight = (20, 7)

        self.box = tk.LabelFrame(window.myframe, text=frame_text, width=45, height=181, fg=fg) # idk why using this height it works
        space = tk.Label(window.myframe, text='', padx=12)
        space.grid(row=index, column=0)
        self.box.grid(row=index, column=1, columnspan=1, sticky='nsew', padx=(0, 0), pady=10)

        tk.Label(self.box, text=f'Valor')\
        .grid(row=0, column=0, sticky='nsew', padx=padxLeft, pady=(5, 0))
        tk.Label(self.box, text=f'Par')\
        .grid(row=0, column=1, sticky='nsew', padx=padxMiddle, pady=(5, 0))
        tk.Label(self.box, text=f'Quantidade')\
        .grid(row=0, column=2, padx=padxRight, pady=(5, 0))

        tk.Label(self.box, text=f'{symbol}{coin.value*multiplier:.2f}')\
        .grid(row=1, column=0, padx=padxLeft, pady=(0, 5))
        tk.Label(self.box, text=f'btc/usd')\
        .grid(row=1, column=1, padx=padxMiddle, pady=(0, 5))
        tk.Label(self.box, text=f'{coin.amount:.8f}')\
        .grid(row=1, column=2, padx=padxRight, pady=(0, 5))

        tk.Label(self.box, text=f'Total')\
        .grid(row=2, column=1, padx=padxMiddle, pady=(5, 0))
        tk.Label(self.box, text=f'{symbol}{coin.amount*coin.value*multiplier:.2f}')\
        .grid(row=3, column=1, padx=padxMiddle, pady=(0, 15))

        remove = tk.Button(self.box, text='Remove')
        remove.config(command=lambda: self.remove(coin))
        remove.grid(row=4, column=1, padx=padxMiddle, pady=(0, 15))

    def remove(self, transaction):
        self.wallet.remove_transaction(transaction)
        self.upper.newWindow.destroy()
        self.upper.__init__(self.upper.app, self.upper.wallet, self.upper.coin_name, self.upper.symbol, self.upper.multiplier, self.upper.test)

class ProfitWindow:
    def __init__(self, app, wallet, coin_name_or_id, symbol, multiplier, update_current_wallet) -> None:
        self.update_current_wallet = update_current_wallet
        wallet_transactions_data = lambda: wallet.coin_transactions(coin_name_or_id)
        
        self.symbol = symbol
        self.multiplier = multiplier

        self.app = app
        self.wallet = wallet
        self.coin_name = coin_name_or_id
        self.holding = self.get_holdint_and_net_cost()[0]
        self.net_cost = self.get_holdint_and_net_cost()[1]*multiplier
        self.mkt_value = self.get_mkt_value()*multiplier
        self.time_profit = self.mkt_value-self.net_cost
        self.average_buy = self.average_buy_and_sell()[0]*multiplier
        self.average_sell = self.average_buy_and_sell()[1]*multiplier
        self.delta = self.get_delta(self.average_sell, self.average_buy)

        self.newWindow = tk.Toplevel(self.app)
        self.newWindow.title("New Window")
        self.newWindow.geometry("500x550")
        self.newWindow.resizable(0, 0)

        self.newWindow.grid_columnconfigure(0, weight=1)
        self.newWindow.grid_columnconfigure(1, weight=1)
        self.newWindow.grid_columnconfigure(2, weight=1)

        self.newWindow.protocol("WM_DELETE_WINDOW", self.onclose)


        # ROW 0 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        tk.Label(self.newWindow, text=coin_name_or_id)\
        .grid(row=0, column=1, columnspan=1, sticky='nsew')

        # ROW 1 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        fg = self.positive_and_negative_color(self.time_profit)
        tk.Label(self.newWindow, text=f'Lucro total: {symbol}{self.time_profit:.2f}', fg=fg)\
        .grid(row=1, column=0, columnspan=3, sticky='nsew')

        # ROW 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        tk.Label(self.newWindow, text='Holding')\
        .grid(row=2, column=0, columnspan=1, sticky='nsew')
        tk.Label(self.newWindow, text='Valor de mercado')\
        .grid(row=2, column=1, columnspan=1, sticky='nsew')
        tk.Label(self.newWindow, text='Valor de aquisicao')\
        .grid(row=2, column=2, columnspan=1, sticky='nsew')

        # ROW 3 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        tk.Label(self.newWindow, text=f'{self.holding:.8f}')\
        .grid(row=3, column=0, columnspan=1, sticky='nsew', pady=(0, 10))
        tk.Label(self.newWindow, text=f'{symbol}{self.mkt_value:.2f}')\
        .grid(row=3, column=1, columnspan=1, sticky='nsew', pady=(0, 10))
        tk.Label(self.newWindow, text=f'{symbol}{self.net_cost:.2f}')\
        .grid(row=3, column=2, columnspan=1, sticky='nsew', pady=(0, 10))

        # ROW 4 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        tk.Label(self.newWindow, text='Valor medio de compra')\
        .grid(row=4, column=0, columnspan=1, sticky='nsew')
        tk.Label(self.newWindow, text='Valor medio de venda')\
        .grid(row=4, column=1, columnspan=1, sticky='nsew')
        tk.Label(self.newWindow, text='Porcentagem de lucro')\
        .grid(row=4, column=2, columnspan=1, sticky='nsew')

        # ROW 5 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        tk.Label(self.newWindow, text=f'{symbol}{self.average_buy:.2f}')\
        .grid(row=5, column=0, columnspan=1, sticky='nsew')
        tk.Label(self.newWindow, text=f'{symbol}{self.average_sell:.2f}')\
        .grid(row=5, column=1, columnspan=1, sticky='nsew')

        fg = self.positive_and_negative_color(self.delta)
        tk.Label(self.newWindow, text=f'{self.delta:.2f}%', fg=fg)\
        .grid(row=5, column=2, columnspan=1, sticky='nsew')

        # ROW 6 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        frame = tk.LabelFrame(self.newWindow)
        frame.grid(row=6, column=0, columnspan=3, sticky='nsew', padx=10, pady=20)

        canvas = tk.Canvas(frame)
        canvas.grid(row=0, column=0)

        canvas.bind('<Configure>', lambda x: canvas.configure(scrollregion = canvas.bbox('all')))
        self.wheel_move(canvas)

        self.myframe = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.myframe, anchor='nw')

        for index, coin in enumerate(wallet_transactions_data()):
            if coin.buy: frame_text, fg = 'Buy', 'green'
            else: frame_text, fg = 'Sell', 'red'
            TransactionsBox(self, coin, index, frame_text, fg)

    def wheel_move(self, canvas):
        def _on_mouse_wheel_down(_):
            canvas.yview_scroll(1 * 2, "units")

        def _on_mouse_wheel_up(_):
            canvas.yview_scroll(-1 * 2, "units")

        canvas.bind_all("<Button-4>", _on_mouse_wheel_up)
        canvas.bind_all("<Button-5>", _on_mouse_wheel_down)

    def get_holdint_and_net_cost(self):
        holding = 0
        net_cost = 0
        for coin in self.wallet.coins:
            if not self.coin_name in (coin.name, coin.cg_id): continue

            if coin.buy: buy=1
            else: buy=-1
            holding += coin.amount*buy
            net_cost += coin.value*coin.amount*buy
        
        return (holding, net_cost)

    def get_mkt_value(self):
        cur_price = coins_name_key[self.coin_name]['current_price']
        return self.holding*cur_price

    def average_buy_and_sell(self):
        buy_count, buy_total, sell_count, sell_total = 0, 0, 0, 0

        for coin in self.wallet.coins:
            if not self.coin_name in (coin.name, coin.cg_id): continue

            if coin.buy: 
                buy_count+=1
                buy_total+=coin.value
            else: 
                sell_count+=1
                sell_total+=coin.value
        
        if buy_count: buy_average = buy_total/buy_count
        else: buy_average = 0

        if sell_count: sell_average = sell_total/sell_count
        else: sell_average = 0

        return (buy_average, sell_average)

    def get_delta(self, avg_sell, avg_buy):
        if not avg_buy or not avg_sell: avg = 0
        else: avg = (avg_sell/avg_buy)*100-100
        return avg

    def positive_and_negative_color(self, value):
        if value > 0: return 'green'
        elif value < 0: return 'red'
        else: return None

    def onclose(self):
        self.newWindow.destroy()
        self.update_current_wallet('')










