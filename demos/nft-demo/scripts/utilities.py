from brownie import network, config, accounts, VRFCoordinatorMock, LinkToken, Contract
from web3 import Web3

LOCAL_BLOCKCHAIN_ENV = [
    "development",
    "ganache",
    "hardhat",
    "ganache-local",
    "mainnet-fork",
]
OPENSEA_URL = "https://testnets.opensea.io/assets/{}/{}"

DECIMALS = 8
STARTING_ETH_PRICE = 200000000000

contract_to_mock = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

BREED_MAPPING = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD"}


def get_breed(breed_num):
    return BREED_MAPPING[breed_num]


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


def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    print("All done!")


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
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=Web3.toWei(0.3, "ether")
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    funding_txn = link_token.transfer(contract_address, amount, {"from": account})
    funding_txn.wait(1)
    print(f"Funded {contract_address}")
    return funding_txn
