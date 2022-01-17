from toolz.itertoolz import get
from brownie import TRIToken
from scripts.utilities import get_account
from web3 import Web3
import time

initial_supply = Web3.toWei(1000, "ether")


def main():
    account = get_account()
    tri_token = TRIToken.deploy(initial_supply, {"from": account})
    time.sleep(1)
    token_name = tri_token.name()
    print(token_name)
    time.sleep(1)
    print(tri_token.symbol())
    print(tri_token.totalSupply())
