import tkinter as tk
import json
import numpy as np
from tkinter import ACTIVE, ANCHOR, SINGLE, Label, ttk
from .wallets import Wallet


############################################ VARIABLES #############################################
wallets = Wallet().get_all_wallets()
cur_wallet = None
row = 0
f = open('coins_list.json', 'r')
coin_json = json.load(f)
f.close()
coins_id_key = {coin['id']: coin for coin in coin_json}
coins_name_key = {coin['name']: coin for coin in coin_json}


wallets_names = list(wallet.name for wallet in wallets)
test = [x for x in range(100)]
columns = ('coin', 'amount', 'value', 'total')

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

    Label(text=err, fg='red').grid(row=error_row, column=0, columnspan=2, sticky='new')

    if err: 
        return 1

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

def show_wallets(_):
    wallets_listbox.grid(row=wallet_lb_row, column=1,columnspan=1, sticky='new', padx=0, pady=(0, 0))

def show_coins(_):
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
    selected_wallet = tuple(filter(lambda x: x.name == wn, wallets))[0]
    cur_wallet = selected_wallet
    coins = tuple(selected_wallet.sum_coins())
    for coin in coins: 
        value = coins_id_key[coin[0]]['current_price']
        old_transactions_tree_view.insert('', 'end',text="8",values=(
                                                                        coins_id_key[coin[0]]['name'], 
                                                                        str(f'{coin[1]:.8f}'), 
                                                                        str(f'{value:.2f}'), 
                                                                        str(f'{coin[1]*value:.2f}')
                                                                    )
        )

    wallets_listbox.grid_remove()

def fill_coin_items_tree_view(_):
    val = _fill_entry(coins_listbox, coins_entry)
    value_entry.delete(0, 'end')
    value_entry.insert(0, _sn_format(coins_name_key[val]['current_price']))
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
        coin_name = coin[0]
        coin_symbol = coins_name_key[coin_name]['symbol']
        coin_buy = transaction == 'buy'
        coin_amount = coin[1]
        coin_value = coin[2]
        coin_wallet_id = cur_wallet.id
        coin_cg_id = coins_name_key[coin_name]['id']
        data = \
            {
                'name': coin_name,
                'symbol': coin_symbol,
                'buy': coin_buy,
                'amount': coin_amount,
                'value': coin_value,
                'wallet_id': coin_wallet_id,
                'cg_id': coin_cg_id,
                'date': None
            }
        cur_wallet.add_coin(data)
    for item in new_transactions_tree_view.get_children(): new_transactions_tree_view.delete(item)
    fill_wallet_items_tree_view('')


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
select = tk.Label(text='Selecione uma carteira: ', borderwidth=2)
select.grid(row=row, column=0, sticky='nsew', padx=0, pady=(15, 3))
#==================================================================================================

# Wallets Entry ===================================================================================
wallets_entry = tk.Entry()
wallets_entry.grid(row=row, column=1,columnspan=1, sticky='nsew', padx=0, pady=(15, 0))
wallets_entry.bind('<Button-1>', show_wallets)
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
for item in wallets_names:
    wallets_listbox.insert('end', item)

space = Label(text='', height=4).grid(row=row, column=0, sticky='nsew', padx=0, pady=(0, 0)) # Just for space the row height

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
old_transactions_tree_view.heading("value", text="Valor($)")
old_transactions_tree_view.column("total", anchor=tk.CENTER, stretch=tk.NO, width=200)
old_transactions_tree_view.heading("total", text="Total($)")

scrollbar = ttk.Scrollbar(orient=tk.VERTICAL, command=old_transactions_tree_view.yview)
old_transactions_tree_view.configure(yscroll=scrollbar.set)
scrollbar.grid(row=row, column=2, sticky='nsew', padx=(0, 50), pady=20)
#=========================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 3++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                               Sum of total
row+=1

# Total ==================================================================================================
total_label = tk.Label(text='Total: ')
total_label.grid(row=row, column=1, sticky='nsew', padx=0, pady=0)
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
coin_label = ttk.Label(text='Moeda: ', font=('Arial', 13))
coin_label.grid(row=row, column=0, columnspan=2, sticky='nsw', padx=(50, 0), pady=0)

amount_label = ttk.Label(text='Quantidade: ', font=('Arial', 13))
amount_label.grid(row=row, column=0, columnspan=2, sticky='ns', padx=(0, 65), pady=0)

value_label = ttk.Label(text='Valor: ', font=('Arial', 13))
value_label.grid(row=row, column=0, columnspan=2, sticky='nse', padx=(0, 170), pady=0)
#================================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++ROW 7++++++++++++++++++++++++++++++++++++++++++++++++++++
#                                         New transactions entries
row+=1

# Coin name entry ================================================================================================
coins_entry = ttk.Entry(width=28)
coins_entry.grid(row=row, column=0, columnspan=2, sticky='nsw', padx=(50, 0), pady=0)
coins_entry.bind('<KeyRelease>', check_coin_entry)
coins_entry.bind('<Button-1>', show_coins)
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
coins_listbox.bind("<<ListboxSelect>>", fill_coin_items_tree_view)
for item in coins_name_key:
    coins_listbox.insert('end', item)

space = Label(text='', height=5).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 0))
#===================================================================================================================

# Button ===========================================================================================================
add_button = ttk.Button(text='Adicionar')
add_button.grid(row=row, column=1, sticky='nsew', padx=0, pady=(30, 20))
add_button.bind('<Button-1>', add_to_treeview)
#===================================================================================================================
row+=1
error_row = row

space = Label(text='', height=1).grid(row=row, column=2, sticky='nsew', padx=0, pady=(0, 15))

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
new_transactions_tree_view.heading("value", text="Valor($)")


# for c in range(15):
#     new_transactions_tree_view.insert('', 'end',text="8",values=('BTC', '1', c))

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
#===================================================================================================================

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

app.bind("<Button-1>", hide_listboxes)

app.grid_columnconfigure(0, weight=1, pad=15)
app.grid_columnconfigure(1, weight=1, pad=15)

if __name__ == '__main__':
    app.mainloop()

