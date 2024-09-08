// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.0;

/// @title IAPR
/// @notice Interface for APR calculations with MultiRewards staking contract
interface IAPR {
    /// @notice Returns the address of the MultiRewards factory
    /// @return The address of the MultiRewards factory
    function multiRewardsFactory() external view returns (address);

    /// @notice Quotes the instantaneous percentage reward rate received by the account extended over duration for the LP token staked in MultiRewards
    /// @dev Assumes stakingToken for MultiRewards contract is a Marginal v1 LP pool token
    /// @param stakingToken The address of the staking token in the MultiRewards contract
    /// @param rewardsToken The address of the rewards token for the MultiRewards contract
    /// @param rewardsPoolWithWETH9 The address of the Marginal v1 pool for the rewards token paired with WETH9
    /// @return rate The percentage rate over duration multiplied by 1e18
    function quotePercentageRate(
        address stakingToken,
        address rewardsToken,
        address rewardsPoolWithWETH9,
        address account,
        uint32 duration
    ) external view returns (uint256 rate);

    /// @notice Quotes the value of the rewards in WETH9 terms
    /// @param pool The address of the Marginal v1 pool for the rewards token paired with WETH9
    /// @param token The address of the reward token
    /// @param amount The amount of reward token to quote in WETH9 terms
    /// @return value The value of the rewards in WETH9 terms
    function quoteRewardInWETH9(
        address pool,
        address token,
        uint128 amount
    ) external view returns (uint256 value);

    /// @notice Quotes the value of the LP pool token in WETH9 terms
    /// @param pool The address of the Marginal v1 pool LP token
    /// @param shares The shares held in the LP token
    /// @return value The value of the LP token in WETH9 terms
    function quotePoolTokenInWETH9(
        address pool,
        uint256 shares
    ) external view returns (uint256 value);
}
