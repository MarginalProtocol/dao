// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.17;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {SafeCast} from "@openzeppelin/contracts/utils/math/SafeCast.sol";

import {IStakingPoints} from "../interfaces/IStakingPoints.sol";

/// @title StakingPoints
/// @notice Placeholder staking contract for the Marginal DAO token until escrowed token live.
/// @dev Points tracked off-chain using events and snapshots.
contract StakingPoints is IStakingPoints {
    using SafeERC20 for IERC20;
    using SafeCast for uint256;

    /// @inheritdoc IStakingPoints
    address public immutable token;

    struct Stake {
        // balance at last update to stake
        uint224 balance;
        // timestamp of last update to stake
        uint32 blockTimestamp;
    }
    /// @inheritdoc IStakingPoints
    mapping(address => Stake) public stakes;

    event Lock(
        address indexed sender,
        uint32 blockTimestampAfter,
        uint224 balanceAfter
    );
    event Free(
        address indexed sender,
        uint32 blockTimestampAfter,
        uint224 balanceAfter
    );

    constructor(address _token) {
        token = _token;
    }

    /// @dev Use before Feb 7, 2106 or infer effect of unsafe cast
    function _blockTimestamp() internal view returns (uint32) {
        return uint32(block.timestamp);
    }

    /// @inheritdoc IStakingPoints
    function lock(uint256 amount) external {
        Stake memory stake = stakes[msg.sender];
        stake.balance = (uint256(stake.balance) + amount).toUint224();
        stake.blockTimestamp = _blockTimestamp();
        stakes[msg.sender] = stake;

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        emit Lock(msg.sender, stake.blockTimestamp, stake.balance);
    }

    /// @inheritdoc IStakingPoints
    function free(uint256 amount) external {
        Stake memory stake = stakes[msg.sender];
        require(amount <= uint256(stake.balance), "amount > stake balance");
        stake.balance -= uint224(amount);
        stake.blockTimestamp = _blockTimestamp();
        stakes[msg.sender] = stake;

        IERC20(token).safeTransfer(msg.sender, amount);
        emit Free(msg.sender, stake.blockTimestamp, stake.balance);
    }
}
