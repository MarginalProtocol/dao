// SPDX-License-Identifier: MIT
pragma solidity 0.5.17;

import "@openzeppelin-solidity-2.3.0/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin-solidity-2.3.0/contracts/ownership/Ownable.sol";

import "./MultiRewards.sol";

/// @title MultiRewardsFactory
/// @author Noah Zinsmeister
/// @dev Fork of Uniswap liquidity staker StakingRewardsFactory adapted for Curve.fi MultiRewards
contract MultiRewardsFactory is Ownable {
    using SafeERC20 for IERC20;

    // immutables
    uint256 public stakingRewardsGenesis;
    uint256 public rewardsDuration = 60 days;

    // the staking tokens for which the rewards contract has been deployed
    address[] public stakingTokens;

    // registry of deployed multi rewards staking contracts by staking token
    mapping(address => address) public multiRewardsByStakingToken;

    // info about rewards for a particular staking token and rewards token
    struct RewardsInfo {
        uint256 rewardAmount;
        bool initialized;
    }

    // rewards info by staking token and rewards token
    mapping(address => mapping(address => RewardsInfo))
        public rewardsInfoByStakingAndRewardsToken;

    constructor(uint256 _stakingRewardsGenesis) public Ownable() {
        require(
            _stakingRewardsGenesis >= block.timestamp,
            "MultiRewardsFactory::constructor: genesis too soon"
        );
        stakingRewardsGenesis = _stakingRewardsGenesis;
    }

    ///// permissioned functions

    // deploy a staking reward contract for the staking token, and store the reward amount
    // the reward will be distributed to the staking reward contract no sooner than the genesis
    function deploy(address stakingToken) public onlyOwner {
        require(
            multiRewardsByStakingToken[stakingToken] == address(0),
            "MultiRewardsFactory::deploy: already deployed"
        );
        multiRewardsByStakingToken[stakingToken] = address(
            new MultiRewards(stakingToken)
        );
        stakingTokens.push(stakingToken);
    }

    // adds reward in a particular rewards token to a staking token
    function addReward(
        address stakingToken,
        address rewardsToken,
        uint256 rewardAmount
    ) public onlyOwner {
        address multiRewards = multiRewardsByStakingToken[stakingToken];
        require(
            multiRewards != address(0),
            "MultiRewardsFactory::addReward: not deployed"
        );

        RewardsInfo storage info = rewardsInfoByStakingAndRewardsToken[
            stakingToken
        ][rewardsToken];
        require(
            info.rewardAmount == 0,
            "MultiRewardsFactory::addReward: already added"
        );
        info.rewardAmount = rewardAmount;

        if (!info.initialized) {
            info.initialized = true;
            MultiRewards(multiRewards).addReward(
                rewardsToken,
                address(this),
                rewardsDuration
            );
        }
    }

    ///// permissionless functions

    // call notifyRewardAmount for all staking tokens with given reward.
    function notifyRewardAmounts(address rewardsToken) public {
        require(
            stakingTokens.length > 0,
            "MultiRewardsFactory::notifyRewardAmounts: called before any deploys"
        );
        for (uint256 i = 0; i < stakingTokens.length; i++) {
            notifyRewardAmount(stakingTokens[i], rewardsToken);
        }
    }

    // notify reward amount for an individual staking token in a given rewards token.
    // this is a fallback in case the notifyRewardAmounts costs too much gas to call for all contracts
    function notifyRewardAmount(
        address stakingToken,
        address rewardsToken
    ) public {
        require(
            block.timestamp >= stakingRewardsGenesis,
            "MultiRewardsFactory::notifyRewardAmount: not ready"
        );

        address multiRewards = multiRewardsByStakingToken[stakingToken];
        require(
            multiRewards != address(0),
            "MultiRewardsFactory::notifyRewardAmount: not deployed"
        );

        RewardsInfo storage info = rewardsInfoByStakingAndRewardsToken[
            stakingToken
        ][rewardsToken];
        require(
            info.rewardAmount > 0,
            "MultiRewardsFactory::notifyRewardAmount: not added"
        );

        uint256 rewardAmount = info.rewardAmount;
        info.rewardAmount = 0;

        require(
            IERC20(rewardsToken).transfer(multiRewards, rewardAmount),
            "MultiRewardsFactory::notifyRewardAmount: transfer failed"
        );
        MultiRewards(multiRewards).notifyRewardAmount(
            rewardsToken,
            rewardAmount
        );
    }
}
