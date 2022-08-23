import json
import tkinter as tk
import numpy as np
import requests
from datetime import datetime
from cryptomonitor.profit_window import ProfitWindow, coins_name_key, coins_id_key, cg, fiat_symbol, fiats_list, cur_fiat
from tkinter import ANCHOR, ttk
from cryptomonitor.wallets import Wallet


############################################ VARIABLES #############################################


# cg.update_coins_list()

wallets = Wallet().get_all_wallets()
wallets_names = list(wallet.name for wallet in wallets)

cur_wallet = None
cur_pair = cur_fiat


file = open('fiats.json', 'r')
data = json.load(file)
if cur_fiat == 'USD': fiat_multiplier = 1
else: fiat_multiplier = float(data[f'USD{cur_fiat}']['bid'])
if cur_pair == 'USD': pair_multiplier = 1
else: pair_multiplier = float(data[f'USD{cur_pair}']['bid'])
file.close()


columns = ('coin', 'amount', 'value', 'total')

row = 0
wallet_lb_row = None
coin_lb_row = None

############################################# FUNCTIONS #############################################
def _add_errors(coin, amount, value, transaction):
    err = None
    try: float(value)
    except: err = 'Valor invalido'
    try: float(amount)
    except: err = 'Quantidade invalida'

    if coin not in coins_name_key.keys(): err = 'Moeda nao encontrada'
    if not transaction: err = 'Por favor, selecione um tipo de transacao'

    tk.Label(text=err, fg='red').grid(row=error_row, column=0, columnspan=2, sticky='new')

    if err: return 1

def _check_entry(event, lst, lst_box):
    value = event.widget.get()
    if value == '': data = lst
    else: data = tuple(filter(lambda item: value.lower() in item.lower(), lst))
    lst_box.delete(0, 'end')   
    for item in data: lst_box.insert('end', item)

def _fill_entry(lst_box, entry):
    entry_value = lst_box.get(ANCHOR)
    entry.delete(0, 'end')
    entry.insert(0, entry_value)
    return entry_value

def _sn_format(num):
    return np.format_float_positional(num, trim='-')

def hide_listboxes(event):
    if event.widget == app:
        wallets_listbox.grid_remove()
        coins_listbox.grid_remove()

def show_wallets_listbox(_):
    wallets_listbox.grid(row=wallet_lb_row, column=1,columnspan=1, sticky='new', padx=0, pady=(0, 0))

def show_coins_listbox(_):
    coins_listbox.grid(row=coin_lb_row, column=0, columnspan=2, sticky='nw', padx=(50, 0), pady=0)

def check_wallet_entry(event):
    _check_entry(event, wallets_names, wallets_listbox)

def check_coin_entry(event):
    _check_entry(event, coins_name_key.keys(), coins_listbox)

def fill_wallet_items_tree_view(_):
    global cur_wallet
    _fill_entry(wallets_listbox, wallets_entry)

    for item in old_transactions_tree_view.get_children(): old_transactions_tree_view.delete(item)

    wn = wallets_entry.get()
    cur_wallet = tuple(filter(lambda x: x.name == wn, wallets))[0]
    coins = list(cur_wallet.sum_coins())
    coins = sorted(coins, key=lambda x: x[1]*coins_id_key[x[0]]['current_price'], reverse=True)
    for coin in coins: 
        coin_id = coin[0]
        value = coins_id_key[coin_id]['current_price']*fiat_multiplier

        old_transactions_tree_view.insert('', 'end',
                                        values=(
                                            coins_id_key[coin_id]['name'], 
                                            str(f'{coin[1]:.8f}'), 
                                            str(f'{(value):.2f}'), 
                                            str(f'{(coin[1]*value):.2f}')
                                        )
        )

    wallets_listbox.grid_remove()

def fill_coin_value(_):
    val = _fill_entry(coins_listbox, coins_entry)
    value_entry.delete(0, 'end')
    value_entry.insert(0, f"{coins_name_key[val]['current_price']*pair_multiplier:.2f}")
    coins_listbox.grid_remove()

def color_radio_button():
    if var_transaction.get() == 1:
        buy_radio['bg'] = 'green'
        buy_radio['activebackground'] = 'green'
        sell_radio['bg'] = '#999999'
        sell_radio['activebackground'] = '#999999'

    if var_transaction.get() == 2:
        sell_radio['bg'] = 'red'
        sell_radio['activebackground'] = 'red'
        buy_radio['bg'] = '#999999'
        buy_radio['activebackground'] = '#999999'
    
def add_to_treeview(_):
    coin = coins_entry.get()
    amount = amount_entry.get()
    value = value_entry.get()

    if _add_errors(coin, amount, value, var_transaction.get()): return
    value = f'{float(value)/pair_multiplier:.2f}'

    coins_entry.delete(0, 'end')
    amount_entry.delete(0, 'end')
    value_entry.delete(0, 'end')

    if var_transaction.get() == 1: tag = 'buy'
    if var_transaction.get() == 2: tag = 'sell'

    new_transactions_tree_view.tag_configure("buy",background='green',foreground='white')
    new_transactions_tree_view.tag_configure("sell",background='red',foreground='white')
    new_transactions_tree_view.insert('', 'end',text="8",values=(coin, amount, value), tags=[tag])

def save_transactions(_):
    global cur_wallet
    if not cur_wallet: return
    items = new_transactions_tree_view.get_children()
    for item in items:
        coin = new_transactions_tree_view.item(item)['values']
        transaction = new_transactions_tree_view.item(item)['tags'][0]
        data = {}
        data['name'] = coin[0]
        data['symbol'] = coins_name_key[coin[0]]['symbol']
        data['buy'] = transaction == 'buy'
        data['amount'] = coin[1]
        data['value'] = coin[2]
        data['wallet_id'] = cur_wallet.id
        data['cg_id'] = coins_name_key[coin[0]]['id']
        data['date'] = None
        cur_wallet.add_coin(data)
    for item in new_transactions_tree_view.get_children(): new_transactions_tree_view.delete(item)
    fill_wallet_items_tree_view('')

def coin_profit_data(_):
    global cur_wallet

    selection = old_transactions_tree_view.selection()
    if not selection: return
    values = old_transactions_tree_view.item(selection[0])['values']
    coin = values[0]
    pw = ProfitWindow(app, cur_wallet, coin)

def update_fiat_multiplier():
    global fiat_multiplier, pair_multiplier
    file = open('fiats.json', 'r')
    data = json.load(file)
    file.close()

    if cur_fiat == 'USD': fiat_multiplier = 1
    else: fiat_multiplier = float(data[f'USD{cur_fiat}']['bid'])
    if cur_pair == 'USD': pair_multiplier = 1
    else: pair_multiplier = float(data[f'USD{cur_pair}']['bid'])
    
def update_fiats():
    param = tuple(f'usd-{f}' for f in fiats_list)
    p = ','.join(param)
    r = requests.get(f'https://economia.awesomeapi.com.br/json/last/{p}')
    with open('fiats.json', 'w') as file:
        data = r.json()
        data['time'] = datetime.timestamp(datetime.utcnow())
        json.dump(data, file)

def update_cur_fiat(event):
    global cur_fiat
    value = event.widget.get()
    cur_fiat = value

    file = open('fiat_codes.json', 'r')
    data = json.load(file)
    data['cur'] = value
    file.close()

    file = open('fiat_codes.json', 'w')
    json.dump(data, file)
    file.close()

    file = open('t.json', 'r')
    fiat_symbol = json.load(file)[cur_fiat]['code']
    file.close()

    old_transactions_tree_view.heading("value", text=f"Valor({fiat_symbol})")
    old_transactions_tree_view.heading("total", text=f"Total({fiat_symbol})")
    update_fiat_multiplier()
    fill_wallet_items_tree_view('')

def update_cur_pair(event):
    global cur_pair
    value = event.widget.get()
    cur_pair = value
    file = open('t.json', 'r')
    fiat_symbol = json.load(file)[cur_pair]['code']
    file.close()

    value_label['text'] = f'Valor({fiat_symbol})'
    update_fiat_multiplier()

    if coins_entry.get() in coins_name_key:
        fill_coin_value('')
    

################################################ APP ################################################

# First config ========================================
app = tk.Tk()
app.title('Crypto Monitor')
app.resizable(0, 0)
app.geometry('850x850')
#======================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 0++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                        Label and an entry for a wallet


# Select Label ===================================================================================
tk.Label(text='Selecione uma carteira: ', borderwidth=2)\
.grid(row=row, column=0, sticky='nsew', padx=0, pady=(15, 3))
#==================================================================================================

# Wallets Entry ===================================================================================
wallets_entry = tk.Entry()
wallets_entry.grid(row=row, column=1,columnspan=1, sticky='nsew', padx=0, pady=(15, 0))
wallets_entry.bind('<Button-1>', show_wallets_listbox)
wallets_entry.bind('<KeyRelease>', check_wallet_entry)
#===================================================================================================


#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 1++++++++++++++++++++++++++++++++++++++++++++++++++++
#                               invisible list box binded with entry in last row 
#                                                     and
#                                                  a button
row+=1
wallet_lb_row = row

# ListBox ===========================================================================================
wallets_listbox = tk.Listbox(height=3)
wallets_listbox.bind("<<ListboxSelect>>", fill_wallet_items_tree_view)
for name in wallets_names:
    wallets_listbox.insert('end', name)

tk.Label(text='', height=4).grid(row=row, column=0, sticky='nsew', padx=0, pady=(0, 0)) # Just for space the row height

#=====================================================================================================

# New Button =========================================================================================
new_button = tk.Button(text='New wallet')#, command=get_wallet)
new_button.grid(row=row, column=0, padx=0, pady=(0, 15))
#=====================================================================================================


#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 2++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                    Treeview of old transactions in a wallet
row+=1

# Tree View ===========================================================================================
old_transactions_tree_view = ttk.Treeview(columns=columns, show='headings', height=4)
old_transactions_tree_view.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=(50, 0), pady=20)
old_transactions_tree_view.column("coin", anchor=tk.CENTER, stretch=tk.NO, width=250)
old_transactions_tree_view.heading("coin", text="Moeda")
old_transactions_tree_view.column("amount", anchor=tk.CENTER, stretch=tk.NO, width=150)
old_transactions_tree_view.heading("amount", text="Quantidade")
old_transactions_tree_view.column("value",anchor=tk.CENTER, stretch=tk.NO, width=150)
old_transactions_tree_view.heading("value", text=f"Valor({fiat_symbol})")
old_transactions_tree_view.column("total", anchor=tk.CENTER, stretch=tk.NO, width=200)
old_transactions_tree_view.heading("total", text=f"Total({fiat_symbol})")

scrollbar = ttk.Scrollbar(orient=tk.VERTICAL, command=old_transactions_tree_view.yview)
old_transactions_tree_view.configure(yscroll=scrollbar.set)
scrollbar.grid(row=row, column=2, sticky='nsew', padx=(0, 50), pady=20)

old_transactions_tree_view.bind('<Double-1>', coin_profit_data)
#=========================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 3++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                               Sum of total
row+=1

# Total ==================================================================================================
tk.Label(text='Total: ')\
.grid(row=row, column=1, sticky='nsew', padx=0, pady=0)
#=========================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 4++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                                  Separator
row+=1

# Separator
separator = ttk.Separator(orient='horizontal')
separator.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=0, pady=0)
#

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 5+++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                            Sell andd buy buttons
row+=1

# Buy and Sell radio buttons ===============================================================================
var_transaction = tk.IntVar()
buy_radio = tk.Radiobutton(text='Compra', 
                           variable=var_transaction, 
                           value=1, 
                           fg='white', 
                           bg='#999999', 
                           width=30, 
                           height=2,
                           command=color_radio_button)

buy_radio.grid(row=row, column=0, columnspan=2, sticky='nsw', padx=(125, 0), pady=20)

sell_radio = tk.Radiobutton(text='Venda ', 
                            variable=var_transaction, 
                            value=2, 
                            fg='white', 
                            bg='#999999', 
                            width=30,
                            command=color_radio_button)

sell_radio.grid(row=row, column=0, columnspan=2, sticky='nse', padx=(0, 125), pady=20)
#===============================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 6++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                       New transactions actions labels
row+=1

# Labels =======================================================================================================
tk.Label(text='Moeda: ', font=('Arial', 13))\
.grid(row=row, column=0, columnspan=2, sticky='nsw', padx=(50, 0), pady=0)

tk.Label(text='Par: ', font=('Arial', 13))\
.grid(row=row, column=0, columnspan=1, sticky='ns', padx=(70, 0), pady=0)

tk.Label(text='Quantidade: ', font=('Arial', 13))\
.grid(row=row, column=0, columnspan=2, sticky='ns', padx=(0, 65), pady=0)

value_label = tk.Label(text=f'Valor({fiat_symbol})', font=('Arial', 13))
value_label.grid(row=row, column=0, columnspan=2, sticky='nse', padx=(0, 145), pady=0)
#================================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 7++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                         New transactions entries
row+=1

# Coin name entry ================================================================================================
coins_entry = ttk.Entry(width=20)
coins_entry.grid(row=row, column=0, columnspan=2, sticky='nsw', padx=(50, 0), pady=0)
coins_entry.bind('<KeyRelease>', check_coin_entry)
coins_entry.bind('<Button-1>', show_coins_listbox)
#==================================================================================================================

# Pair Combobox ================================================================================================
pair = ttk.Combobox(values=fiats_list, width=8, state="readonly") #ttk.Entry(width=8)
pair.current(0)
pair.bind('<<ComboboxSelected>>', update_cur_pair)
pair.grid(row=row, column=0, columnspan=1, sticky='ns', padx=(100, 0), pady=0)
#==================================================================================================================



# Amount entry =====================================================================================================
amount_entry = ttk.Entry(width=28)
amount_entry.grid(row=row, column=0, columnspan=2, sticky='ns', padx=(50, 0), pady=0)
#==================================================================================================================


# Value entry =====================================================================================================
value_entry = ttk.Entry(width=28)
value_entry.grid(row=row, column=0, columnspan=2, sticky='nse', padx=(50, 0), pady=0)
#===================================================================================================================


#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 8++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                         Invisible listbox and a button
row+=1
coin_lb_row = row

# Coins listbox =====================================================================================================
coins_listbox = tk.Listbox(height=4, width=28)
coins_listbox.bind("<<ListboxSelect>>", fill_coin_value)
for name in coins_name_key:
    coins_listbox.insert('end', name)



tk.Label(text='', height=5).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 0))
#===================================================================================================================

# Button ===========================================================================================================
add_button = ttk.Button(text='Adicionar')
add_button.grid(row=row, column=1, sticky='nsew', padx=0, pady=(30, 20))
add_button.bind('<Button-1>', add_to_treeview)
#===================================================================================================================
row+=1
error_row = row

tk.Label(text='', height=1).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 15))

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 9++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                           New transaction treeview
row+=1

# Tree View =========================================================================================================
new_transactions_tree_view = ttk.Treeview(columns=columns, show='headings', height=5)
new_transactions_tree_view.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=(50, 0), pady=0)
new_transactions_tree_view.column("coin",anchor=tk.CENTER, stretch=tk.NO, width=275)
new_transactions_tree_view.heading("coin", text="Moeda")
new_transactions_tree_view.column("amount", anchor=tk.CENTER, stretch=tk.NO, width=275)
new_transactions_tree_view.heading("amount", text="Quantidade")
new_transactions_tree_view.column("value",anchor=tk.CENTER, stretch=tk.NO, width=200)
new_transactions_tree_view.heading("value", text=f"Valor($)")

scrollbar = ttk.Scrollbar(orient=tk.VERTICAL, command=new_transactions_tree_view.yview)
new_transactions_tree_view.configure(yscroll=scrollbar.set)
scrollbar.grid(row=row, column=2, sticky='nsew', padx=(0, 50))
#===================================================================================================================



#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 10++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                                    Button
row+=1

# Button ============================================================================================================
save_button = ttk.Button(text='Salvar')
save_button.grid(row=row, column=1, sticky='nsew', padx=0, pady=(10, 50))
save_button.bind('<Button-1>', save_transactions)
#====================================================================================================================

#+++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 11++++++++++++++++++++++++++++++++++++++++++++++++++++
row+=1

fiat_combobox = ttk.Combobox(values=fiats_list, width=8, state="readonly")
fiat_combobox.grid(row=row, column=0, sticky='nsw', padx=(50, 0), pady=0)
index = fiats_list.index(cur_fiat)
fiat_combobox.current(index)
fiat_combobox.bind('<<ComboboxSelected>>', update_cur_fiat)



app.bind("<Button-1>", hide_listboxes)
app.grid_columnconfigure(0, weight=1, pad=15)
app.grid_columnconfigure(1, weight=1, pad=15)

if __name__ == '__main__':
    app.mainloop()

