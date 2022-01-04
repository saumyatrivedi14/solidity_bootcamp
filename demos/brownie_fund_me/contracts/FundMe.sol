// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

/*
 *   Interfaces compile down to ABI (Application Binary Interface).
 *   The ABI tells solidity and ither programming languages how
 *   it can interact with another contract.
 *   Below "AggregatorV3Interface" is a Chainlink interface which compile down to an ABI.
 *   Note: Anytime you want to interact with an already deployed smart contract you will need an ABI
 */
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
// for version below 0.8 comipler for Solidity
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    // for version below 0.8 comipler for Solidity, to avoid overflow of uint256 use below:
    using SafeMathChainlink for uint256;

    // mapping to keep track of who send us funds and how much
    mapping(address => uint256) public addressToAmountFunded;

    // array of funders address
    address[] public funders;

    // we need constructor (function called during first instance of deployment)
    // In this case we want to store owner (which is address of the sender = me)
    address public owner;
    AggregatorV3Interface public priceFeed;

    // we need to add constructor parameters to avoid hard-coding the address
    // to collect price feed below
    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    // payable -> its a fallback function to transfer ETH
    function fund() public payable {
        // threshold min USD amt
        uint256 minUSD = 50 * 10**18;

        require(
            getConversionRate(msg.value) >= minUSD,
            "Min Threshold of Amt required is $50!"
        );
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    function getVersion() public view returns (uint256) {
        // to initialize the price feed we need address to
        // AggregatorV3Interface interface on mainnet or testnet
        // https://docs.chain.link/docs/ethereum-addresses/

        /*
         *   Here we are getting the price feed of ETH from chainlink Oracle for Rinkeby Testnet
         *   address. These price feed data doesn't exist on a local Ganache chain.
         *   To test it with a Ganache simulated chain, we will have two option.
         *   1. Fork the simulated chain and work with it. (Discussed later)
         *   2. Mock the price feed value insert it in the contract
         */
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //     0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // );
        return priceFeed.version();
    }

    function getPrice() public view returns (uint256) {
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //     0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // );
        /*
         *   A Tuple is returned when calling latestRoundData()
         *   ref link - https://docs.chain.link/docs/price-feeds-api-reference/
         *   Tuple element details:
         *       roundId: The round ID.
         *       answer: The price.
         *       startedAt: Timestamp of when the round started.
         *       updatedAt: Timestamp of when the round was updated.
         *       answeredInRound: The round ID of the round in which the answer was computed.
         */
        (, int256 answer, , , ) = priceFeed.latestRoundData();

        // its a good practice to keep the value in ETH denominations
        // 1 ETH = 10^18 Wei
        // 1 ETH = 10^9 Gwei
        return uint256(answer * 10000000000);
    }

    function getConversionRate(uint256 ethAmt) public view returns (uint256) {
        uint256 ethPrice = getPrice();
        uint256 ethAmtInUSD = (ethPrice * ethAmt) / 1000000000000000000;
        return ethAmtInUSD;
    }

    function getEntranceFee() public view returns (uint256) {
        // minimumUSD
        uint256 minUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return ((minUSD * precision) / price);
    }

    /*
     *   Modifiers => a modifier is used to change the
     *   behavior of a function in a declarative way
     */
    modifier onlyOwner() {
        require(msg.sender == owner);
        _; // "_" is where compiler adds the rest of the function (in this case withdraw()
    }

    // before this function gets called we will run the modifier to check the requirement
    // by defining the modifier in the function definition
    function withdraw() public payable onlyOwner {
        /*
         *   transfer() is used to send ETH from one address to another
         *   "this" is the keyword in Solidity for your current contract (in this case FundMe)
         *   address(this) returns the address of your current contract
         *   balance is an attribute of the contract.
         */
        //require(msg.sender == owner);
        payable(msg.sender).transfer(address(this).balance);

        // reset all the funders after withdrawal
        for (uint256 funderIdx = 0; funderIdx < funders.length; funderIdx++) {
            address funder = funders[funderIdx];
            // updating our mapping
            addressToAmountFunded[funder] = 0;
        }

        funders = new address[](0);
    }
}
