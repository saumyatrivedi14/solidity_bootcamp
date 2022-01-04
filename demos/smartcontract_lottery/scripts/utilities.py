from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)

FORKED_LOCAL_ENV = ["mainnet-fork"]
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]

DECIMALS = 8
STARTING_ETH_PRICE = 200000000000


def get_account(idx=0, id=None):
    if idx:
        return accounts[idx]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        # to get address of local Ganache account
        return accounts[0]
    # to get address of MetaMask account
    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks(decimals=DECIMALS, init_eth_val=STARTING_ETH_PRICE):
    print("Deploying Mocks...")
    account = get_account()
    MockV3Aggregator.deploy(decimals, init_eth_val, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token, {"from": account})

    print("Mocks Deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie config
    if defines, otherwise, it will deplot a mock version of that contract, and
    return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:
            # MockV3Aggregator.length
            deploy_mocks()
        # MockV3Aggregator[-1]
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=1000000000000000000
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    txn = link_token.transfer(contract_address, amount, {"from": account})
    ##
    # Instead of doing transfer directly with the contract,
    #  we can use Chainlink-Mix/Interfaces for LinkToken
    # (https://github.com/smartcontractkit/chainlink-mix/blob/master/interfaces/LinkTokenInterface.sol)
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # txn = link_token_contract.transfer(contract_address, amount, {"from": account})
    txn.wait(1)
    print("Funded contract with LINK!")
    return txn
