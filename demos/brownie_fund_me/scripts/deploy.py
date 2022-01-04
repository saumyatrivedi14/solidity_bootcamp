from brownie import FundMe, MockV3Aggregator, config, network
from scripts.utilities import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENV


def deploy_fund_me():
    account = get_account()
    # Pass the price feed address to our FundMe contract
    # If we are on a persistent network like Rinkeby, use the associated
    # Oracle address to collect real world data otherwise, deploy mocks

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Contract deployed to {fund_me.address}")
    return fund_me


def main():
    deploy_fund_me()
