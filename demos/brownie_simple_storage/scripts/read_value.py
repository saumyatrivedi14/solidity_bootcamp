from brownie import SimpleStorage, accounts, config


def read_contract():
    # to work with latest deployment
    simple_storage = SimpleStorage[-1]

    # To interact with a contract we need these two things: ABI & Address
    print(simple_storage.retrieve())


def main():
    read_contract()
