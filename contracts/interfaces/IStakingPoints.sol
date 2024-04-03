// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.0;

/// @title IStakingPoints
/// @notice Interface for points staking tracked off-chain using events and snapshots.
interface IStakingPoints {
    /// @notice The address of the staking token
    function token() external view returns (address);

    /// @notice `msg.sender` current balance of staking token in the contract
    function stakes(
        address account
    ) external view returns (uint224 balance, uint32 blockTimestamp);

    /// @notice Locks staking token in contract updating stake snapshot
    /// @dev amount should always fit in uint224 given Marginal DAO token supply
    /// @param amount The amount of staking token to lock
    function lock(uint256 amount) external;

    /// @notice Frees staking token from contract updating stake snapshot
    /// @param amount The amount of staking token to free
    function free(uint256 amount) external;
}
