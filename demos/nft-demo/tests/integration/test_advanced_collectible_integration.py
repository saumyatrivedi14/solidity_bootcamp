from brownie import network, AdvancedCollectible
import pytest
from scripts.utilities import LOCAL_BLOCKCHAIN_ENV
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
import time


def test_can_create_advanced_collectible_integration():
    # deploy the contract
    # create an NFT
    # get a random breed back
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Only for local testing")
    # Act
    advanced_collectible, creation_txn = deploy_and_create()
    time.sleep(60)
    # Assert
    assert advanced_collectible.tokenCounter() == 1
