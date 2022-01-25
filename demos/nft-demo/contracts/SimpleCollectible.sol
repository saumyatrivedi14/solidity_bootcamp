// SPDX-Lincense-Identifier: MIT

pragma solidity 0.6.6;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract SimpleCollectible is ERC721 {
    /*
     * Our NFT is a sort of factory contract.
     * There will be many NFTs, but they are all contained in this one contract.
     * Creating a new NFT, is just mapping a tokenId to a new address / owner
     * _safeMint function is used to create a new NFT.
     * Basically it mints 'tokenId' and transfers it to an address.
     * Here tokenId starts with zero and increment whenever we have new tokenId.
     */

    uint256 public tokenCounter;

    constructor() public ERC721("Dogie", "DOG") {
        tokenCounter = 0;
    }

    /*
     * Since pushing videos and photos on blockchain consumes more gas, the concept
     * of Metadata is incorporated in EIP-721. A distinct Uniform Resource Identifier (URI)
     * is assigned for a given asset. They point to a JSON file that conforms to ERC721 Metadata JSON Schema
     * The metadata extension is OPTIONAL for ERC-721 smart contracts.
     */
    // Note - NFT marketplaces are a little clueless with on-chain attributes and metadata
    //        Currently, they can only pull attirbutes from the metadata. We cannot store these in token URIs.
    //        The blockchain has no idea about these token URIs. Hence, we have to store these attirbutes on chain.

    function createCollectible(string memory tokenURI)
        public
        returns (uint256)
    {
        uint256 newTokenID = tokenCounter;
        _safeMint(msg.sender, newTokenID);
        _setTokenURI(newTokenID, tokenURI);
        tokenCounter = tokenCounter + 1;
        return newTokenID;
    }
}
