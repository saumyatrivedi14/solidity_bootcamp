## Swap some ETH for WETH (ERC20 Token for Ethereum)
# to interact easily with other ERC20 tokens on AAVE protocol
# https://kovan.etherscan.io/token/0xd0a1e359811322d97991e03f863a0c30c2cf029c#writeContract
from scripts.utilities import get_account
from brownie import interface, config, network


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    txn = weth.deposit({"from": account, "value": (0.1 * 10 ** 18)})
    txn.wait(1)
    print("Received 0.1 WETH")
    return txn


def main():
    get_weth()
