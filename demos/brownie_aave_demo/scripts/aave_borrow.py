from brownie import network, config, interface
from scripts.utilities import get_account
from scripts.get_weth import get_weth
from web3 import Web3


def main():
    test_amount = Web3.toWei(0.1, "ether")
    dai_borrowable_per = 0.80

    account = get_account()
    erc20_addr = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # We'll need ABI and Address of the AAVE - Lending Pool Contract
    # https://docs.aave.com/developers/the-core-protocol/lendingpool
    lending_pool = get_lending_pool()

    # In order to first deposit ERC20 Token (WETH) in this contract, we need to approve
    # sending these token. This is done using the approve() function
    approve_erc20(test_amount, lending_pool.address, erc20_addr, account)

    # Once approved, we can deposit()
    # deposit(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)
    print("Depositing...")
    txn = lending_pool.deposit(
        erc20_addr, test_amount, account.address, 0, {"from": account}
    )
    txn.wait(1)
    print("Deposited!")

    # Once deposited, we need information to our account data,
    # so that we understand our liquidation limits and borrow accordingly
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)

    # Borrow DAI in terms of ETH
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )

    # borrowable_eth -> borrowable_dai * 80%
    amt_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * dai_borrowable_per)
    print(f"DAI to be borrowed: {amt_dai_to_borrow}")

    # Cmd to borrow dai
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    borrow_txn = lending_pool.borrow(
        dai_address,
        Web3.toWei(amt_dai_to_borrow, "ether"),
        1,  # stable / fixed interest rate
        0,
        account.address,
        {"from": account},
    )
    borrow_txn.wait(1)
    print(f"Borrowed DAI: {amt_dai_to_borrow}")
    get_borrowable_data(lending_pool, account)

    # repay all the DAI back to get WETH back
    # repay_all(test_amount, lending_pool, account)

    # print("Account balance after repayment!")
    # get_borrowable_data(lending_pool, account)
    # print("Deposited, Borrowed and Repayed with AAVE, Brownie and Chainlink!")


## User-defined Functions


def get_lending_pool():
    lending_pool_addr_provider_contract = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addr_provider"]
    )
    # Contract Address
    lending_pool_addr = lending_pool_addr_provider_contract.getLendingPool()
    # Contract ABI
    lending_poll = interface.ILendingPool(lending_pool_addr)
    return lending_poll


def approve_erc20(amount, spender, erc20_addr, account):
    # Contract ABI
    # Contract Address
    print("approving ERC20 token...")
    erc20_contract = interface.IERC20(erc20_addr)
    txn = erc20_contract.approve(spender, amount, {"from": account})
    txn.wait(1)
    print("Approved!")
    return txn


# We want to run this on lending_pool from our account
def get_borrowable_data(lending_pool_contract, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool_contract.getUserAccountData(account.address)
    total_collateral_eth = Web3.fromWei(totalCollateralETH, "ether")
    print(f"Total Collateral worth of ETH deposited: {total_collateral_eth}")
    total_debt_eth = Web3.fromWei(totalDebtETH, "ether")
    print(f"Total Debt worth of ETH borrowed: {total_debt_eth}")
    available_borrow_eth = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"Total available worth of ETH: {available_borrow_eth}")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed_contract = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed_contract.latestRoundData()[1]
    conv_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The latest DAI/ETH price: {conv_latest_price}")
    return float(conv_latest_price)


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token_address"],
        account,
    )
    repay_txn = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token_address"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_txn.wait(1)
    print("Repayed all!")
