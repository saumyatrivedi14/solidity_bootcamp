from brownie import MockV3Aggregator, network, config, accounts

FORKED_LOCAL_ENV = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]

DECIMALS = 8
STARTING_ETH_PRICE = 200000000000

## Working with mainnet fork
# when working with mainnet fork we don't have any ETH on mainnet
# so, we need to tell brownie to create us fake account with 100 ETH.
# However, we don't want to deploy any mocks (deploy_mocks)


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        # to get address of local Ganache account
        return accounts[0]
    else:
        # to get address of MetaMask account
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print(f"the active network is {network.show_active()}")
    print("Deploying Mocks...")
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(DECIMALS, STARTING_ETH_PRICE, {"from": get_account()})
    print("Mocks Deployed!")
