import json
import tkinter as tk
import numpy as np
import requests
from datetime import datetime
from cryptomonitor.profit_window import ProfitWindow, coins_name_key, coins_id_key, cg
from tkinter import ANCHOR, ttk
from cryptomonitor.wallets import Wallet

####################################### FUNCTIONS ###############################################

def fiat_multiplier(fiat):
    with open('fiats.json', 'r') as file:
        data = json.load(file)
        if fiat.upper() == 'USD': return 1
        else: return float(data[f'USD{fiat}']['bid'])

def get_fiat_symbol(fiat):
    with open('fiat_codes.json', 'r') as file:
        return json.load(file)['fiats_info'][fiat]['code']

def get_fiats():
    with open('fiat_codes.json', 'r') as file:
        data = json.load(file)
        fiats_list = data['fiat_codes']
        current_general_fiat = data['current']
        return fiats_list, current_general_fiat

############################################ VARIABLES #############################################

fiats_list, current_general_fiat = get_fiats()
current_pair_fiat = current_general_fiat

cg.update_coins_list()
columns = ('coin', 'amount', 'value', 'total')
wallets_list = lambda: Wallet().get_all_wallets()
wallets_names = lambda: list(wallet.name for wallet in wallets_list())


general_multiplier = lambda: fiat_multiplier(current_general_fiat)
pair_multiplier = lambda: fiat_multiplier(current_pair_fiat)

general_symbol = lambda: get_fiat_symbol(current_general_fiat)
pair_symbol = lambda: get_fiat_symbol(current_pair_fiat)

current_wallet = None
current_wallet_coins = lambda: update_current_wallet_coins()

wallet_lb_row = None
coin_lb_row = None
row = 0

############################################# TK FUNCTIONS #############################################
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

def new_wallet(_):
    if wallets_entry.get() and wallets_entry.get().upper() not in map(lambda x: x.upper(), wallets_names()):
        wallets_listbox.grid_remove()
        Wallet().new_wallet(wallets_entry.get())
        wallets_entry.delete(0, 'end')
        wallets_listbox.delete(0, 'end')
        for name in wallets_names(): wallets_listbox.insert('end', name)

def del_wallet(_):
    global current_wallet
    if current_wallet:
        wallets_listbox.grid_remove()
        current_wallet = current_wallet.delete()
        wallets_entry.delete(0, 'end')
        wallets_listbox.delete(0, 'end')
        for name in wallets_names(): wallets_listbox.insert('end', name)

def hide_listboxes(event):
    if event.widget == app:
        wallets_listbox.grid_remove()
        coins_listbox.grid_remove()

def show_wallets_listbox(_):
    wallets_listbox.grid(row=wallet_lb_row, column=1,columnspan=1, sticky='new', padx=0, pady=(0, 0))
    wallets_listbox.lift()

def show_coins_listbox(_):
    coins_listbox.grid(row=coin_lb_row, column=0, columnspan=2, sticky='nw', padx=(50, 0), pady=0)

def check_wallet_entry(event):
    _check_entry(event, wallets_names(), wallets_listbox)

def check_coin_entry(event):
    _check_entry(event, coins_name_key.keys(), coins_listbox)

def update_current_wallet_coins():
    coins = list(current_wallet.sum_coins())
    return sorted(coins, key=lambda x: x[1]*coins_id_key[x[0]]['current_price'], reverse=True)

def update_current_wallet(_):
    global current_wallet
    _fill_entry(wallets_listbox, wallets_entry)
    wallet_name = wallets_entry.get()
    current_wallet = tuple(filter(lambda wallet: wallet.name == wallet_name, wallets_list()))[0]
    wallets_listbox.grid_remove()
    wallet_total()
    fill_wallet_items_tree_view('')


def fill_wallet_items_tree_view(_):
    for item in old_transactions_tree_view.get_children(): old_transactions_tree_view.delete(item)
    for coin in current_wallet_coins(): 
        coin_id = coin[0]
        coin_value = coins_id_key[coin_id]['current_price']*general_multiplier()
        values = [coins_id_key[coin_id]['name']]
        values.append(str(f'{coin[1]:.8f}'))
        values.append(str(f'{(coin_value):.2f}'))
        values.append(str(f'{(coin[1]*coin_value):.2f}'))
        old_transactions_tree_view.insert('', 'end',values=values)

def fill_coin_value(_):
    val = _fill_entry(coins_listbox, coins_entry)
    value_entry.delete(0, 'end')
    value_entry.insert(0, f"{coins_name_key[val]['current_price']*pair_multiplier():.2f}")
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
    if var_transaction.get() == 1: tag = 'buy'
    if var_transaction.get() == 2: tag = 'sell'
    value = f'{float(value)/pair_multiplier():.2f}'
    coins_entry.delete(0, 'end')
    amount_entry.delete(0, 'end')
    value_entry.delete(0, 'end')
    new_transactions_tree_view.tag_configure("buy",background='green',foreground='white')
    new_transactions_tree_view.tag_configure("sell",background='red',foreground='white')
    new_transactions_tree_view.insert('', 'end',text="8",values=(coin, amount, value), tags=[tag])

def save_transactions(_):
    if not current_wallet: return
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
        data['wallet_id'] = current_wallet.id
        data['cg_id'] = coins_name_key[coin[0]]['id']
        data['date'] = None
        current_wallet.add_coin(data)
        new_transactions_tree_view.delete(item)
    fill_wallet_items_tree_view('')

def coin_profit_data(_):
    selection = old_transactions_tree_view.selection()
    if not selection: return
    values = old_transactions_tree_view.item(selection[0])['values']
    coin = values[0]
    pw = ProfitWindow(app, current_wallet, coin, general_symbol(), general_multiplier(), update_current_wallet)
    
def update_fiats():
    param = tuple(f'usd-{f}' for f in fiats_list if f.lower() != 'usd')
    p = ','.join(param)
    r = requests.get(f'https://economia.awesomeapi.com.br/json/last/{p}')
    with open('fiats.json', 'w') as file:
        data = r.json()
        data['time'] = datetime.timestamp(datetime.utcnow())
        json.dump(data, file)
    
def update_tree_view_fiat_symbol():
    old_transactions_tree_view.heading("value", text=f"Valor({general_symbol()})")
    old_transactions_tree_view.heading("total", text=f"Total({general_symbol()})")

def update_general_fiat(event):
    global current_general_fiat
    value = event.widget.get()
    current_general_fiat = value
    update_tree_view_fiat_symbol()
    with open('fiat_codes.json', 'r+') as file:
        data = json.load(file)
        data['current'] = value
        file.seek(0)
        file.truncate()
        json.dump(data, file)

def update_pair_fiat(event):
    global current_pair_fiat
    current_pair_fiat = event.widget.get()
    value_label['text'] = f'Valor({pair_symbol()})'
    if coins_entry.get() in coins_name_key: fill_coin_value('')

def wallet_total():
    total = 0
    for coin in current_wallet_coins(): total+=get_current_price(coin[0])*general_multiplier()*coin[1]
    total_label.configure(text=f'Total: {general_symbol()}{total:.2f}')

def get_current_price(coin):
    return coins_id_key[coin]['current_price']

################################################ APP ################################################

# update_fiats()
# App config ========================================
app = tk.Tk()
app.title('Crypto Monitor')
app.resizable(0, 0)
app.geometry('850x850')
app.bind("<Button-1>", hide_listboxes)
app.grid_columnconfigure(0, weight=1, pad=15)
app.grid_columnconfigure(1, weight=1, pad=15)
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
wallets_listbox = tk.Listbox(height=4)
wallets_listbox.bind("<<ListboxSelect>>", update_current_wallet)
for name in wallets_names(): wallets_listbox.insert('end', name)
tk.Label(text='', height=4).grid(row=row, column=0, sticky='nsew', padx=0, pady=(0, 0)) # Just for space the row height

#=====================================================================================================

# New Button =========================================================================================
new_button = tk.Button(text='New wallet')#, command=get_wallet)
new_button.grid(row=row, column=0, padx=0, pady=(0, 15))
new_button.bind('<Button-1>', new_wallet)
#=====================================================================================================

# Del Button =========================================================================================
del_button = tk.Button(text='Delete wallet')#, command=get_wallet)
del_button.grid(row=row, column=1, padx=0, pady=(0, 15))
del_button.bind('<Button-1>', del_wallet)
#=====================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 2++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                    Treeview of old transactions in a wallet
row+=1

# Tree View ===========================================================================================
old_transactions_tree_view = ttk.Treeview(columns=columns, show='headings', height=4)
old_transactions_tree_view.grid(row=row, column=0, columnspan=2, sticky='nsew', padx=(50, 0), pady=(20, 0))
old_transactions_tree_view.column("coin", anchor=tk.CENTER, stretch=tk.NO, width=250)
old_transactions_tree_view.heading("coin", text="Moeda")
old_transactions_tree_view.column("amount", anchor=tk.CENTER, stretch=tk.NO, width=150)
old_transactions_tree_view.heading("amount", text="Quantidade")
old_transactions_tree_view.column("value",anchor=tk.CENTER, stretch=tk.NO, width=150)
old_transactions_tree_view.heading("value", text=f"Valor({general_symbol()})")
old_transactions_tree_view.column("total", anchor=tk.CENTER, stretch=tk.NO, width=200)
old_transactions_tree_view.heading("total", text=f"Total({general_symbol()})")

old_transactions_tree_view.bind('<Double-1>', coin_profit_data)

scrollbar = ttk.Scrollbar(orient=tk.VERTICAL, command=old_transactions_tree_view.yview)
old_transactions_tree_view.configure(yscroll=scrollbar.set)
scrollbar.grid(row=row, column=2, sticky='nsew', padx=(0, 50), pady=20)

#=========================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 3++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                               Sum of total
row+=1

# Total ==================================================================================================
total_label = tk.Label()
total_label.grid(row=row, column=1, sticky='ne', padx=(0, 50), pady=(5, 25))
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

value_label = tk.Label(text=f'Valor({pair_symbol()})', font=('Arial', 13))
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
pair.bind('<<ComboboxSelected>>', update_pair_fiat)
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
coins_listbox = tk.Listbox(height=5, width=28)
coins_listbox.bind("<<ListboxSelect>>", fill_coin_value)
for name in coins_name_key: coins_listbox.insert('end', name)
tk.Label(text='', height=5).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 0)) # Fill space
#===================================================================================================================

# Button ===========================================================================================================
add_button = ttk.Button(text='Adicionar')
add_button.grid(row=row, column=1, sticky='nsew', padx=0, pady=(30, 20))
add_button.bind('<Button-1>', add_to_treeview)
#===================================================================================================================
row+=1
error_row = row

tk.Label(text='', height=1).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 15)) # Fill space

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
index = fiats_list.index(current_general_fiat)
fiat_combobox.current(index)
fiat_combobox.bind('<<ComboboxSelected>>', update_general_fiat)

if __name__ == '__main__':
    app.mainloop()

