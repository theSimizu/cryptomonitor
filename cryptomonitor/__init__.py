from .startfunctions import wai, si, wallet_actions_interface, start_interface, cg


def run():
    cg.update_coins_list()
    current_wallet = None
    while True:
        if current_wallet:
            choice = wallet_actions_interface()
            current_wallet = wai[choice](current_wallet)
        else:
            start = start_interface()
            current_wallet = si[start]()



if __name__ == '__main__':
    pass