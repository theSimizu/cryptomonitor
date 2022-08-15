import json
import tkinter as tk
from cryptomonitor.coingecko import CoinGecko
from tkinter import ANCHOR, Label, ttk
from tkinter.scrolledtext import ScrolledText

cg = CoinGecko()

f = open('coins_list.json', 'r')
coin_json = json.load(f)
f.close()

coins_id_key = {coin['id']: coin for coin in coin_json}
coins_name_key = {coin['name']: coin for coin in coin_json}


class ProfitWindow:
    def __init__(self, app, wallet, coin_name_or_id) -> None:
        wallet_transactions_data = wallet.coin_transactions(coin_name_or_id)
        
        self.wallet = wallet
        self.coin_name = coin_name_or_id

        self.holding = self.get_holdint_and_net_cost()[0]
        self.net_cost = self.get_holdint_and_net_cost()[1]
        self.mkt_value = self.get_mkt_value()
        self.average_buy = self.average_buy_and_sell()[0]
        self.average_sell = self.average_buy_and_sell()[1]
        self.delta = self.get_delta(self.average_sell, self.average_buy)


        self.newWindow = tk.Toplevel(app)
        self.newWindow.title("New Window")
        self.newWindow.geometry("500x500")
        self.newWindow.resizable(0, 0)

        self.newWindow.grid_columnconfigure(0, weight=1)
        self.newWindow.grid_columnconfigure(1, weight=1)
        self.newWindow.grid_columnconfigure(2, weight=1)

        # ROW 0 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        coin_title = tk.Label(self.newWindow, text=coin_name_or_id)\
        .grid(row=0, column=0, columnspan=3, sticky='nsew')

        # ROW 1 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        coin_all_time_profit = tk.Label(self.newWindow, text='All Time Profit: PlaceHolder')\
        .grid(row=1, column=0, columnspan=3, sticky='nsew')

        # ROW 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        label = tk.Label(self.newWindow, text='Holding')\
        .grid(row=2, column=0, columnspan=1, sticky='nsew')
        label = tk.Label(self.newWindow, text='Valor de mercado')\
        .grid(row=2, column=1, columnspan=1, sticky='nsew')
        label = tk.Label(self.newWindow, text='Valor de aquisicao')\
        .grid(row=2, column=2, columnspan=1, sticky='nsew')

        # ROW 3 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        holdings = tk.Label(self.newWindow, text=f'{self.holding:.8f}')\
        .grid(row=3, column=0, columnspan=1, sticky='nsew')
        mkt_value = tk.Label(self.newWindow, text=f'{self.mkt_value:.2f}')\
        .grid(row=3, column=1, columnspan=1, sticky='nsew')
        net_cost = tk.Label(self.newWindow, text=f'{self.net_cost:.2f}')\
        .grid(row=3, column=2, columnspan=1, sticky='nsew')

        # ROW 4 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        label = tk.Label(self.newWindow, text='Valor medio de compra')\
        .grid(row=4, column=0, columnspan=1, sticky='nsew')
        label = tk.Label(self.newWindow, text='Valor medio de venda')\
        .grid(row=4, column=1, columnspan=1, sticky='nsew')
        label = tk.Label(self.newWindow, text='Porcentagem de lucro')\
        .grid(row=4, column=2, columnspan=1, sticky='nsew')

        # ROW 5 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        av_buy_price = tk.Label(self.newWindow, text=f'{self.average_buy:.2f}')\
        .grid(row=5, column=0, columnspan=1, sticky='nsew')
        av_sell_price = tk.Label(self.newWindow, text=f'{self.average_sell:.2f}')\
        .grid(row=5, column=1, columnspan=1, sticky='nsew')
        av_delta = tk.Label(self.newWindow, text=f'{self.delta:.2f}%')\
        .grid(row=5, column=2, columnspan=1, sticky='nsew')

        # ROW 6 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        frame = tk.LabelFrame(self.newWindow)
        frame.grid(row=6, column=0, columnspan=3, sticky='nsew', padx=25, pady=20)

        canvas = tk.Canvas(frame)
        canvas.grid(row=0, column=0)

        canvas.bind('<Configure>', lambda x: canvas.configure(scrollregion = canvas.bbox('all')))
        self.wheel_move(canvas)

        myframe = tk.Frame(canvas)
        canvas.create_window((0, 0), window=myframe, anchor='nw')

        padxLeft = (25, 30)
        padxMiddle = 20
        padxRight = (30, 25)

        for index, coin in enumerate(wallet_transactions_data):
            if coin.buy: 
                frame_text = 'Buy'
                color = 'green'
            else: 
                frame_text = 'Sell'
                color = 'red'

            box = tk.LabelFrame(myframe, text=frame_text, width=50, height=135, fg=color) # idk why using this height it works
            space = tk.Label(myframe, text='', padx=12)
            space.grid(row=index, column=0)
            box.grid(row=index, column=1, columnspan=1, sticky='nsew', padx=(0, 0), pady=10)

            l = tk.Label(box, text=f'Valor').grid(row=0, column=0, sticky='nsew', padx=padxLeft, pady=(5, 0))
            l = tk.Label(box, text=f'Par').grid(row=0, column=1, sticky='nsew', padx=padxMiddle, pady=(5, 0))
            l = tk.Label(box, text=f'Quantidade').grid(row=0, column=2, padx=padxRight, pady=(5, 0))

            l = tk.Label(box, text=coin.value).grid(row=1, column=0, padx=padxLeft, pady=(0, 5))
            l = tk.Label(box, text=f'btc/usd').grid(row=1, column=1, padx=padxMiddle, pady=(0, 5))
            l = tk.Label(box, text=f'{coin.amount:.8f}').grid(row=1, column=2, padx=padxRight, pady=(0, 5))

            l = tk.Label(box, text=f'Total').grid(row=2, column=1, padx=padxMiddle, pady=(5, 0))
            l = tk.Label(box, text=f'{coin.amount*coin.value:.2f}').grid(row=3, column=1, padx=padxMiddle, pady=(0, 15))

    def wheel_move(self, canvas):
        def _on_mouse_wheel_down(_):
            canvas.yview_scroll(1 * 2, "units")

        def _on_mouse_wheel_up(_):
            # print(event)
            canvas.yview_scroll(-1 * 2, "units")

        canvas.bind_all("<Button-4>", _on_mouse_wheel_up)
        canvas.bind_all("<Button-5>", _on_mouse_wheel_down)

    def wallet_data(self):
        coins = self.wallet.coin_transactions(self.coin_name)

    def get_holdint_and_net_cost(self):
        holding = 0
        net_cost = 0
        for coin in self.wallet.coins:
            if self.coin_name in (coin.name, coin.cg_id):
                if coin.buy: buy=1
                else: buy=-1
                holding += coin.amount*buy
                net_cost += coin.value*coin.amount*buy
        
        return (holding, net_cost)

    def get_mkt_value(self):
        cur_price = coins_name_key[self.coin_name]['current_price']
        return self.holding*cur_price

    def average_buy_and_sell(self):
        buy_count = 0
        buy_total = 0
        sell_count = 0
        sell_total = 0

        for coin in self.wallet.coins:
            if self.coin_name in (coin.name, coin.cg_id):
                if coin.buy: 
                    buy_count+=1
                    buy_total+=coin.value
                else: 
                    sell_count+=1
                    sell_total+=coin.value
                
        return (buy_total/buy_count, sell_total/sell_count)

    def get_delta(self, avg_sell, avg_buy):
        return (avg_sell/avg_buy)*100-100









