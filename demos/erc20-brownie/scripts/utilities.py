from brownie import network, accounts, config

LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local", "mainnet-fork"]


def get_account(idx=0, id=None):
    if idx:
        return accounts[idx]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        # to get address of local Ganache account
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        # to get address of MetaMask account
        return accounts.add(config["wallets"]["from_key"])
    return None
