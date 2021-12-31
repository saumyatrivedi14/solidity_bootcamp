// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    // without initialization it get null or zero
    // default visibility is set to internal
    uint256 favoriteNumber;

    struct People {
        uint256 favoriteNumber;
        string name;
    }

    // dynamic array
    People[] public people;
    // mapping -> A dictionary like data structure with 1 value per key
    mapping(string => uint256) public nameToFavoritenumber;

    function store(uint256 _favoriteNumber) public {
        favoriteNumber = _favoriteNumber;
    }

    /*
     *   View & Pure identifiers
     *   these are non-state changing functions hence no transaction is required.
     *   view -> it is used to read off the blockchain.
     *   pure -> it is used for purely mathematical calc.
     *   Note: "public" variables are automotically assigned as "view" functions
     */
    function retrieve() public view returns (uint256) {
        return favoriteNumber;
    }

    /*
     *   Memory & Storage identifiers
     *   memory -> memory will only be stored during execution of the function and will delete after execution
     *   storage -> storage will persist the value after function execution
     */
    function addPerson(string memory _name, uint256 _favoriteNumber) public {
        // add to array
        people.push(People(_favoriteNumber, _name));
        // establish mapping
        nameToFavoritenumber[_name] = _favoriteNumber;
    }
}
