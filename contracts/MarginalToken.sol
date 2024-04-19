// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.17;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";

/// @title MarginalToken
/// @notice The Marginal DAO token used for DAO operations of the Marginal protocol
contract MarginalToken is ERC20 {
    /// @notice Initial number of tokens in circulation
    uint256 public constant initialSupply = 1_000_000_000e18; // 1 billion

    /// @notice Minimum time between mints
    uint256 public constant minimumTimeBetweenMints = 1 days * 365;

    /// @notice Cap on the percentage of totalSupply that can be minted at each mint
    uint256 public constant mintCap = 2;

    /// @notice The timestamp after which the next minting may occur
    uint256 public mintingAllowedAfter;

    /// @notice The minter of Marginal DAO tokens
    address public owner;
    event OwnerChanged(address indexed oldOwner, address indexed newOwner);

    constructor() ERC20("Marginal DAO Token", "MARG") {
        owner = msg.sender;
        _mint(msg.sender, initialSupply);
        mintingAllowedAfter = block.timestamp + minimumTimeBetweenMints;
    }

    /// @notice Mints an amount of tokens to recipient
    /// @dev Supply schedule determined by owner of this contract
    /// @param to The address to mint tokens to
    /// @param amount The amount of tokens to mint
    function mint(address to, uint256 amount) external {
        require(msg.sender == owner, "not minter");
        require(
            block.timestamp >= mintingAllowedAfter,
            "minting not allowed yet"
        );
        require(to != address(0), "minting to zero address");

        mintingAllowedAfter = block.timestamp + minimumTimeBetweenMints;

        // check amount below inflation cap
        uint256 amountMax = Math.mulDiv(totalSupply(), mintCap, 100);
        require(amount <= amountMax, "exceeded mint cap");

        _mint(to, amount);
    }

    /// @notice Sets the owner of the Marginal DAO token contract
    /// @dev Can only be called by the current owner
    /// @param _owner The new owner of the contract
    function setOwner(address _owner) external {
        require(msg.sender == owner);
        emit OwnerChanged(owner, _owner);
        owner = _owner;
    }
}
