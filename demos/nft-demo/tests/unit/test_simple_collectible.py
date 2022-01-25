from fcntl import LOCK_EX
from scripts.utilities import LOCAL_BLOCKCHAIN_ENV, get_account
from scripts.simple_collectible.deploy_and_create import deploy_and_create
from brownie import network
import pytest


def test_can_Create_simple_collectible():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    simple_collectible = deploy_and_create()
    assert simple_collectible.ownerOf(0) == get_account()
