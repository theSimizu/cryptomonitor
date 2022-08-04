from .coingecko import CoinGecko
from .wallets import Wallet

cg = CoinGecko()
    
def _transaction(wallet, _type):
    if _type == 'buy': buy = True
    if _type == 'sell': buy = False
    coin_data = {}
    coin_name = input('Coin: ')
    coin = cg.search_coin_by_name_or_symbol(coin_name)
    amount = float(input('Amount: '))
    value = input('Value($): ')
    value = float(value or coin['current_price'])
    coin_data['name'] = coin['name']
    coin_data['symbol'] = coin['symbol']
    coin_data['amount'] = amount
    coin_data['buy'] = buy
    coin_data['value'] = value
    coin_data['date'] = None
    coin_data['cg_id'] = coin['id']
    wallet.add_coin(coin_data)

# Wallet Functions
#########################################
def buy(current_wallet):
    _transaction(current_wallet, 'buy')
    return current_wallet

def sell(current_wallet):
    _transaction(current_wallet, 'sell')
    return current_wallet

def rename(current_wallet):
    new_name = input('New name: ')
    current_wallet.rename(new_name)
    return current_wallet

def delete(current_wallet):
    current_wallet.delete()
    return None

def back(_):
    return None
########################################

# Start Functions
##################################################################
def see_wallets():
    wallets = Wallet().get_all_wallets()
    for wallet in wallets:
        # if not wallet.coins: continue
        Wallet().build_table(wallet, cg)
    return None

def select_wallet():
    wallets = Wallet().get_all_wallets()
    for index, wallet in enumerate(wallets):
        print(f'{index+1} - {wallet.name}')
    choice = int(input('\n> '))
    return Wallet().get_wallet_by_name(wallets[choice-1].name)

def new_wallet():
    new_wallet_name = input('Nome: ')
    Wallet().new_wallet(new_wallet_name)
    return None
##################################################################


# Interfaces
#################################################################
def start_interface():
    return int(input('\nO que voce deseja fazer?\n\
                                \n1-Ver suas carteiras\
                                \n2-Selecionar carteira\
                                \n3-Adicionar carteira\
                                \n4-EXit\
                                \n\n> '))-1

def wallet_actions_interface():
    return int(input('\n1-Adicionar compra\
                      \n2-Adicionar venda\
                      \n3-Renomear carteira\
                      \n4-Excluir carteira\
                      \n5-Back\
                      \n\n> '))-1
#################################################################


wai = (buy, sell, rename, delete, back)
si = (see_wallets, select_wallet, new_wallet, quit)