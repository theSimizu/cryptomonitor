from .models import Wallets, session

class Wallet:
    def get_wallet_by_id(self, id) -> Wallets:
        return session.query(Wallets).get(id)

    def get_wallet_by_name(self, name) -> Wallets:
        return session.query(Wallets).filter_by(name=name).first()
    
    def get_all_wallets(self):
        return session.query(Wallets).all()

    def new_wallet(self, name) -> Wallets:
        wallet = Wallets(name=name)
        session.add(wallet)
        session.commit()
        return wallet

    @staticmethod
    def build_table(wallet: Wallets, cg):
        coins_info = cg.get_coins_info_from_wallet(wallet)
        brl = cg._dolar_cotation('BRL')
        total = 0
        size = 60
        equals = f'+{"="*size}+'
        pluses = f'|{"+"*size}|'

        # Title
        print(equals)
        print(f'|{wallet.name.center(size)}|')
        print(equals)
        #

        # Coins
        for coin_info in coins_info:
            name = coin_info["name"]
            symbol = f' ({coin_info["symbol"]})'
            amount = str(coin_info["amount"])
            price = f' (${coin_info["price"]})'
            dolar_total = coin_info["amount"] * coin_info["price"]
            brl_total = dolar_total * brl
            total += dolar_total
            print(pluses)
            print(f'|{str(name + symbol).ljust(size)}|')
            print(f'|{str(amount + price).ljust(size//2)}{str(f"${dolar_total:.2f} | R${brl_total:.2f}").rjust(size//2)}|')
        print(equals)
        #

        # Sum
        print(f'|{f"USD: ${total:.2f}".center(size)}|')
        print(f'|{"".center(size)}|')
        print(f'|{f"BRL: R${total*brl:.2f}".center(size)}|')
        print(equals)
        print()
        #



    
# wallet = Wallet().get_wallet_by_name('Electrum')

    
if __name__ == '__main__':
    wallet = Wallet().get_wallet_by_name('Electrum')
    
    
