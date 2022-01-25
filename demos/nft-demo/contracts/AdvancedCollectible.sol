// SPDX-Lincense-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract AdvancedCollectible is ERC721, VRFConsumerBase {
    uint256 public tokenCounter;
    bytes32 public keyHash;
    uint256 public fee;
    enum Breed {
        PUB,
        SHIBA_INU,
        ST_BERNARD
    }

    // create mapping btw breed and tokenId
    mapping(uint256 => Breed) public tokenIdToBreed;
    // create mapping btw requestId and address(sender)
    mapping(bytes32 => address) public requestIdToSender;

    // emit events when updating mappings below
    event requestedCollectible(bytes32 indexed requestId, address requester);
    event breedAssigned(uint256 indexed tokenId, Breed breed);

    constructor(
        address _vrfCoordinator,
        address _link,
        bytes32 _keyHash,
        uint256 _fee
    ) public VRFConsumerBase(_vrfCoordinator, _link) ERC721("Dogie", "DOG") {
        tokenCounter = 0;
        fee = _fee;
        keyHash = _keyHash;
    }

    // tokenURI is created after the random number is generated
    function createCollectible() public returns (bytes32) {
        /*
         * Here the tokenId needs to be assigned to
         * the user randomly out of three breeds available i.e PUG, SHIBA_INU, ST_BERNARD
         */
        bytes32 requestId = requestRandomness(keyHash, fee);
        /*
         * There needs to be a mapping btw the original caller of createCollectible to requestID
         * to use that in _safeMint() step
         */
        requestIdToSender[requestId] = msg.sender;
        emit requestedCollectible(requestId, msg.sender);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomNumber)
        internal
        override
    {
        Breed breed = Breed(randomNumber % 3);
        uint256 newTokenID = tokenCounter;
        tokenIdToBreed[newTokenID] = breed;
        emit breedAssigned(newTokenID, breed);
        address owner = requestIdToSender[requestId];
        _safeMint(owner, newTokenID);
        // TODO - Use fulfillRandomness() to _setTokenURI() instead of below custom function
        //_setTokenURI(newTokenID, tokenURI);
        tokenCounter = tokenCounter + 1;
    }

    /*
     * we can only knowonce the random number is returned to use _setTokenURI() function.
     * Below is the implementation of function to set TokenURI based of above three choices of Dogs.
     */
    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        // only owner of tokenId (3 of the dog pics) can update the token URI
        require(
            _isApprovedOrOwner(_msgSender(), tokenId),
            "ERC721 Error: caller is not owner, not approved!"
        );
        _setTokenURI(tokenId, _tokenURI);
    }
}
