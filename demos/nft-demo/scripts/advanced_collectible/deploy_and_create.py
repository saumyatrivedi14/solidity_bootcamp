from brownie import AdvancedCollectible, network, config
from scripts.utilities import fund_with_link, get_account, get_contract, OPENSEA_URL


def deploy_and_create():
    account = get_account()
    # We want to be able to use the deployed contracts if we are on a testnet
    # Otherwise, we want to deploy some mocks and use those
    # Rinkeby
    advanced_collectible = AdvancedCollectible.deploy(
        get_contract("vrf_coordinator"),
        get_contract("link_token"),
        config["networks"][network.show_active()]["key_hash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
    )
    fund_with_link(advanced_collectible.address)
    creating_txn = advanced_collectible.createCollectible({"from": account})
    creating_txn.wait(1)
    print("New Token has been created!")
    return advanced_collectible, creating_txn


def main():
    deploy_and_create()
