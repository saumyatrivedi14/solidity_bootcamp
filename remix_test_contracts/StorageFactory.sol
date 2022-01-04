// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SimpleStorage.sol";

// Aim - to deploy and interact with functions o a contract from another contract
// Inheritance in solidity can be done using below line
contract StorageFactory is SimpleStorage {
// contract StorageFactory {

    SimpleStorage[] public simpleStorageArray;

    function createSimpleStorageContract() public {
        // create a new contract
        SimpleStorage simpleStorage = new SimpleStorage();
        // store address of above defined contract in an array
        // this way we can call contract from another contract
        simpleStorageArray.push(simpleStorage);
    }

    function sfStore(uint256 _simpleStorageIdx, uint256 _simpleStorageNum) public {
        // Address and ABI (Application Binary Interface) of the function from another contract
        SimpleStorage simpleStorage = SimpleStorage(address(simpleStorageArray[_simpleStorageIdx]));
        simpleStorage.store(_simpleStorageNum);
    }

    function sfGet(uint256 _simpleStorageIdx) public view returns (uint256) {
        // Address and ABI (Application Binary Interface) of the function from another contract
        SimpleStorage simpleStorage = SimpleStorage(address(simpleStorageArray[_simpleStorageIdx]));
        return simpleStorage.retrieve();
    }
}