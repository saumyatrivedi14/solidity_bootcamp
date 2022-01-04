from brownie import network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.utilities import (
    LOCAL_BLOCKCHAIN_ENV,
    get_account,
    fund_with_link,
    get_contract,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    # Act
    # 2000 ETH / USD
    # usdEntryFee is $50
    # Amt in ETH = 50/2000
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 2


def test_choosing_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for local testing")
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(idx=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(idx=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    txn = lottery.endLottery({"from": account})
    # Since we used an Event to emit the requestID,
    # we can grab it from our transaction object
    requestID = txn.events["RequestedRandomness"]["requestID"]
    # With this requestID, we can use callBackWithRandomness() from VRFCoordinatorMock.sol
    # to get a random number
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestID, STATIC_RNG, lottery.address, {"from": account}
    )

    starting_balance_account0 = account.balance()
    balance_of_lottery = lottery.balance()

    # Assert
    # 777 % 3 = 0 => Winner should be account_0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_account0 + balance_of_lottery
    assert lottery.lottery_state() == 1  # CLOSED
