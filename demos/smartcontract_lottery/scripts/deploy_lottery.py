from brownie import Lottery, config, network
from scripts.utilities import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["key_hash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    txn = lottery.startLottery({"from": account})
    txn.wait(1)
    print("The Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You've entered The Lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # fund the contract
    txn = fund_with_link(lottery.address)
    txn.wait(1)
    # then end the lottery
    ending_txn = lottery.endLottery({"from": account})
    ending_txn.wait(1)
    time.sleep(180)
    print(f"{lottery.recentWinner()} is the winner of The Lottery!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
