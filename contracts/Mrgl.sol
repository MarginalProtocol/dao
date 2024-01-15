// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.17;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Mrgl is ERC20 {
    address public owner;
    event OwnerChanged(address indexed oldOwner, address indexed newOwner);

    constructor() ERC20("Marginal DAO Token", "MRGL") {
        owner = msg.sender;
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == owner);
        _mint(to, amount);
    }

    function setOwner(address _owner) external {
        require(msg.sender == owner);
        emit OwnerChanged(owner, _owner);
        owner = _owner;
    }
}
