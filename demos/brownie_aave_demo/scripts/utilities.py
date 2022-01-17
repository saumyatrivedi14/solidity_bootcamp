from brownie import (
    network,
    config,
    accounts,
)

LOCAL_BLOCKCHAIN_ENV = [
    "development",
    "ganache",
    "hardhat",
    "ganache-local",
    "mainnet-fork",
]

DECIMALS = 8
STARTING_ETH_PRICE = 200000000000


def get_account(idx=0, id=None):
    if idx:
        return accounts[idx]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        # to get address of local Ganache account
        return accounts[0]
    # to get address of MetaMask account
    return accounts.add(config["wallets"]["from_key"])
