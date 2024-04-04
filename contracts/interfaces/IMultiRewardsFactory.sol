// SPDX-License-Identifier: MIT
pragma solidity >=0.4.24;

/// @title IMultiRewardsFactory
/// @notice Interface for factory of Curve.fi MultiRewards
interface IMultiRewardsFactory {
    function stakingRewardsGenesis() external view returns (uint256);

    function rewardsDuration() external view returns (uint256);

    function stakingTokens(uint256 i) external view returns (address);

    function multiRewardsByStakingToken(
        address stakingToken
    ) external view returns (address);

    function rewardsInfoByStakingAndRewardsToken(
        address stakingToken,
        address rewardsToken
    ) external view returns (uint256 rewardAmount, bool initialized);

    function deploy(address stakingToken) external;

    function addReward(
        address stakingToken,
        address rewardsToken,
        uint256 rewardAmount
    ) external;

    function notifyRewardAmounts(address rewardsToken) external;

    function notifyRewardAmount(
        address stakingToken,
        address rewardsToken
    ) external;
}
