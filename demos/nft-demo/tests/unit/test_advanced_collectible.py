from brownie import network, AdvancedCollectible
import pytest
from scripts.utilities import LOCAL_BLOCKCHAIN_ENV, get_account, get_contract
from scripts.advanced_collectible.deploy_and_create import deploy_and_create


def test_can_create_advanced_collectible():
    # deploy the contract
    # create an NFT
    # get a random breed back
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("Only for local testing")
    # Act
    advanced_collectible, creation_txn = deploy_and_create()
    requestId = creation_txn.events["requestedCollectible"]["requestId"]
    exp_random_number = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId,
        exp_random_number,
        advanced_collectible.address,
        {"from": get_account()},
    )
    # Assert
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.tokenIdToBreed(0) == exp_random_number % 3
