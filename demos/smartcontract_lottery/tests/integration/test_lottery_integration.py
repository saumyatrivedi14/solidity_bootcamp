from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.utilities import (
    LOCAL_BLOCKCHAIN_ENV,
    get_account,
    fund_with_link,
)
import pytest
import time


def test_can_pick_winner():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("only for Testnet (Rinkeby) testing")
    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # Here, we re working with actual Testnet and Chainlink, so no mocking is required.
    time.sleep(180)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
