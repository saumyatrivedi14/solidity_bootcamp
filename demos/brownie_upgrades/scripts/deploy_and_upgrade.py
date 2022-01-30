#!/usr/bin/python3
from brownie import (
    Box,
    BoxV2,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    config,
    network,
    Contract,
)
from scripts.utilities import get_account, encode_function_data, upgrade
import time


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    # Optional, deploy the ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy(
        {"from": account},
    )

    # If we want an intializer function we can add
    # `initializer=box.store, 1`
    # to simulate the initializer being the `store` function
    # with a `newValue` of 1
    box_encoded_initializer_function = encode_function_data()
    # box_encoded_initializer_function = encode_function_data(initializer=box.store, 1)
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        # account.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy} ! You can now upgrade it to BoxV2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    time.sleep(1)
    proxy_box.store(1, {"from": account})
    print(f"Here is the initial value in the Box: {proxy_box.retrieve()}")

    # upgrade
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_txn = upgrade(account, proxy, box_v2, proxy_admin_contract=proxy_admin)
    time.sleep(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    time.sleep(1)
    print(f"Starting value {proxy_box.retrieve()}")
    proxy_box.increment({"from": account})
    time.sleep(1)
    print(f"Ending value {proxy_box.retrieve()}")
