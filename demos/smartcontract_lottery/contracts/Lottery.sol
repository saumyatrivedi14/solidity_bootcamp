// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    address payable public recentWinner;
    uint256 public usdEntryFee;
    uint256 public randomness;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    /**
     * _keyHash ID of public key against which randomness is generated
     * _fee The amount of LINK to send with the request
     */
    uint256 public fee;
    bytes32 public keyHash;

    // Creating an event to collect random number using requestID
    event RequestedRandomness(bytes32 requestID);

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        // $50 min entrance fee
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Lottery is not opened by the Admin!"
        );
        require(msg.value >= getEntranceFee(), "Min Amt required is $50!");
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // the return value of rpice from Chainlink has 8 decimals
        // (https://docs.chain.link/docs/ethereum-addresses/)
        // So, we are adding 10 more to make it 18 decimal value
        uint256 adjustedPrice = uint256(price) * 10**10;
        // since entry fee is $50 and value of ETH we'll set is $2000 per ETH
        // entry fees in ETH = 50 / 2000 ETH. Since, we cannot do floating point in Solidity,
        // we'll add more decimals
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "Can't start a Lottery yet!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        /*
         *   1. Cast whatever we get to uint256 and pick a random index in the players
         *      array as winner
         *   2. keccack256 - hash all the variables same all the time for every instance
         *   3. abi.encodePacked - creates an ancoded packed of all the data mentioned
         *      within the function
         */
        // uint256(
        //     keccack256(
        //         abi.encodePacked(
        //             nonce,              // predictable
        //             msg.sender,         // predictable
        //             block.difficulty,   // This can be manupulated by the miners!
        //             block.timestamp     // predictable
        //         )
        //     )
        // ) % players.length;
        // Note - The below method cannot be used to gather random number bcoz miners
        // can use it for their advantage and win the lottery

        // In this transaction we end the lottery and request a random number
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;

        /*
         *  Because its difficult to return requestID from this function to python and
         *  test, we will add an Event to be emitted (print / store) to read requestID
         *  from our python unit tests.
         *  (https://docs.soliditylang.org/en/v0.8.11/abi-spec.html?highlight=Events#events)
         */
        bytes32 requestID = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestID);
    }

    /*
     *   fulfillRandomness is called by VRFCoordinator when it receives a valid VRF
     *   proof and we don't want anyone other than Chainlink to call this function.
     *
     *   That is the reason we define it as `internal`, so that only VRFCoordinator
     *   can call this function when it has a random number.
     *
     *   The `override` declaration means the original declaration of fulfillRandomness
     *   in VRFConsumerBase can be over-written to below function.
     *   (https://docs.soliditylang.org/en/v0.7.3/contracts.html#function-overriding)
     */
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Finding Winner, Please be Patient!"
        );
        require(_randomness > 0, "random-not-found!");
        uint256 winnerIdx = _randomness % players.length;
        recentWinner = players[winnerIdx];
        recentWinner.transfer(address(this).balance);

        // reset lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
