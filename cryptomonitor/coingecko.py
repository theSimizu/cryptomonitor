import requests
import json
from datetime import datetime

class CoinGecko:
    def __init__(self) -> None:
        self.URL = 'https://api.coingecko.com/api/v3/'

    def _searched_coin_table(self, coins):
        print(' =============================================================== ')
        print(f'|{"INDEX".center(7)}|{"NAME".center(48)}|{"RANK".center(6)}|')
        for index, coin in enumerate(coins):
            print(' =============================================================== ')
            print('|{}|{}|{}|'.\
                format(str(index+1).center(7),
                       str(f'{coin["name"]} ({coin["symbol"].upper()})').center(48),
                       str(coin['market_cap_rank']).center(6)
                )
            )
        print(' =============================================================== ')
        return int(input('Qual a moeda?\n\n> '))-1

    def _get(self, path):
        return requests.get(f'{self.URL}{path}')

    def _dolar_cotation(self, fiat):
        r = requests.get(f'http://economia.awesomeapi.com.br/json/last/USD-{fiat}')
        return float(r.json()[f'USD{fiat}']['bid'])

    def _wait(self):
        now = datetime.timestamp(datetime.utcnow())
        try:
            o = open('last_update.txt', 'x')
            o.close()
        except:
            file = open('last_update.txt', 'r')
            last = file.read()
            file.close()
            if not last: 
                file = open('last_update.txt', 'w')
                file.write(str(now))
                file.close()
            else:
                last = float(last)
                if now-last < 60: return False
                else: 
                    file = open('last_update.txt', 'w')
                    file.write(str(now))
                    file.close()
        return True

    def update_coins_list(self):
        conti = self._wait()
        if not conti: return

        r = self._get('coins/markets?vs_currency=usd&per_page=250')
        if not r.status_code == 200: return
        with open('coins_list.json', 'w') as file:
            json.dump(r.json(), file)

    def search_coin_by_name_or_symbol(self, name):
        with open('coins_list.json', 'r') as file:
            json_list = json.loads(file.read())
            filtered_coins = list(filter(lambda coin: name.lower() in ' '.join((coin['id'].lower(), 
                                                                                coin['symbol'].lower(), 
                                                                                coin['name'].lower())), json_list))
            index = self._searched_coin_table(filtered_coins)
            return filtered_coins[index]
            
    def get_coins_info_from_wallet(self, wallet):
        with open('coins_list.json', 'r') as file:
            cp = wallet.sum_coins()
            cg_data = json.load(file)
            coins = [
                {
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'cg_id': coin['id'],
                    'price': coin['current_price']
                }
                for coin in cg_data if coin['id'] in map(lambda x: x[0], cp)
            ]

            for c in range(len(coins)):
                coins[c]['amount'] = tuple(x[1] for x in cp if x[0] == coins[c]['cg_id'])[0]

            return coins

    def coin_name_to_cg_id(self, coin_name):
        with open('coins_list.json', 'r') as file:
            cg_data = json.load(file)
            coin = tuple(filter(lambda x: x['name'] == coin_name, cg_data))[0]
            return coin['id']

    # def coin_cg_id_to_name(self, coin_id):
    #     with open('coins_list.json', 'r') as file:
    #         cg_data = json.load(file)
    #         coin = tuple(filter(lambda x: x['id'] == coin_id, cg_data))[0]
    #         return coin['name']

if __name__ == '__main__':
    cg = CoinGecko()
    cg.update_coins_list()
    # cg.get_coins_info_from_wallet(test)
    # cg.search_coin_by_name_or_symbol('btc')
