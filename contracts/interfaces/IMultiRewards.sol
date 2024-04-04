// SPDX-License-Identifier: MIT
pragma solidity >=0.4.24;

/// @title IMultiRewards
/// @notice Interface for Curve.fi MultiRewards
interface IMultiRewards {
    function stakingToken() external view returns (address);

    function rewardData(
        address rewardsToken
    )
        external
        view
        returns (
            address rewardsDistributor,
            uint256 rewardsDuration,
            uint256 periodFinish,
            uint256 rewardRate,
            uint256 lastUpdateTime,
            uint256 rewardPerTokenStored
        );

    function rewardTokens(uint256 i) external view returns (address);

    function userRewardPerTokenPaid(
        address account,
        address rewardsToken
    ) external view returns (uint256);

    function rewards(
        address account,
        address rewardsToken
    ) external view returns (uint256);

    function addReward(
        address _rewardsToken,
        address _rewardsDistributor,
        uint256 _rewardsDuration
    ) external;

    function totalSupply() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function lastTimeRewardApplicable(
        address _rewardsToken
    ) external view returns (uint256);

    function rewardPerToken(
        address _rewardsToken
    ) external view returns (uint256);

    function earned(
        address account,
        address _rewardsToken
    ) external view returns (uint256);

    function getRewardForDuration(
        address _rewardsToken
    ) external view returns (uint256);

    function stake(uint256 amount) external;

    function withdraw(uint256 amount) external;

    function getReward() external;

    function exit() external;

    function notifyRewardAmount(address _rewardsToken, uint256 reward) external;
}
