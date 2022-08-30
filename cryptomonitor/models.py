from requests import delete
from sqlalchemy import  create_engine, Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

engine = create_engine('sqlite+pysqlite:///database.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class CryptoCurrencies(Base):
    __tablename__ = 'cryptocurrencies'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    buy = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    date = Column(DateTime)
    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    cg_id = Column(String, nullable=False)


class Wallets(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    coins = relationship('CryptoCurrencies')
    
    def get_coins(self) -> list:
        return self.coins

    def add_coin(self, data):
        name = data['name']
        symbol = data['symbol']
        buy = data['buy']
        amount = data['amount']
        value = data['value']
        date = data['date'] or datetime.utcnow()
        cg_id = data['cg_id']
        coin = CryptoCurrencies(name=name, 
                                symbol=symbol,
                                buy=buy, 
                                amount=amount,
                                value=value, 
                                date=date, 
                                wallet_id=self.id, 
                                cg_id=cg_id)

        wallet = session.query(Wallets).get(self.id)
        wallet.coins.append(coin)
        session.commit()

    def sum_coins(self):
        unique_coins = set(coin.cg_id for coin in self.coins)
        coins_data = {k: 0 for k in unique_coins}
        for coin in self.coins:
            if not coin.buy: coins_data[coin.cg_id] -= float(coin.amount)
            if coin.buy: coins_data[coin.cg_id] += float(coin.amount)
        return coins_data.items()

    def rename(self, new_name):
        wallet = session.query(Wallets).get(self.id)
        wallet.name = new_name
        session.commit()

    def delete(self):
        session.query(Wallets).filter(Wallets.id == self.id).delete(synchronize_session=False)
        session.query(CryptoCurrencies).filter(CryptoCurrencies.wallet_id == self.id).delete(synchronize_session=False)
        session.commit()

    def coin_transactions(self, coin_name):
        return tuple(filter(lambda coin: coin_name.lower() in (coin.name.lower(), coin.cg_id.lower()), self.coins))

    def remove_transaction(self, transaction):
        session.query(CryptoCurrencies).filter(CryptoCurrencies.id == transaction.id).delete(synchronize_session=False)
        session.commit()


        


def get_wallets():
    print(session.query(Wallets).all())

Base.metadata.create_all(engine) #Create the database and tables




if __name__ == '__main__':
    wallet = session.query(Wallets).filter_by(name='Trezor').first()
    wallet.coin_transactions('bitcoin')
    # print(tuple(wallet.sum_coins()))