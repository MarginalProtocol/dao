// SPDX-License-Identifier: AGPL-3.0
pragma solidity =0.8.15;

import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";
import {SafeCast} from "@openzeppelin/contracts/utils/math/SafeCast.sol";

import {FixedPoint64} from "@marginal/v1-core/contracts/libraries/FixedPoint64.sol";
import {FixedPoint96} from "@marginal/v1-core/contracts/libraries/FixedPoint96.sol";
import {FixedPoint128} from "@marginal/v1-core/contracts/libraries/FixedPoint128.sol";
import {IMarginalV1Pool} from "@marginal/v1-core/contracts/interfaces/IMarginalV1Pool.sol";

import {PeripheryImmutableState} from "@marginal/v1-periphery/contracts/base/PeripheryImmutableState.sol";
import {PoolAddress} from "@marginal/v1-periphery/contracts/libraries/PoolAddress.sol";

import {IMultiRewards} from "../interfaces/IMultiRewards.sol";
import {IMultiRewardsFactory} from "../interfaces/IMultiRewardsFactory.sol";
import {IAPR} from "../interfaces/IAPR.sol";

/// @title APR for MultiRewards staking contract
/// @notice Determines the APR for a MultiRewards staked token referencing Marginal v1 pools for LP token prices
contract APR is IAPR, PeripheryImmutableState {
    using SafeCast for uint256;

    /// @inheritdoc IAPR
    address public immutable multiRewardsFactory;

    error InvalidTokens();
    error InvalidPool();
    error PoolNotInitialized();
    error MultiRewardsNotInitialized();
    error MultiRewardsNotSupplied();

    constructor(
        address _factory,
        address _WETH9,
        address _multiRewardsFactory
    ) PeripheryImmutableState(_factory, _WETH9) {
        multiRewardsFactory = _multiRewardsFactory;
    }

    /// @inheritdoc IAPR
    function quotePercentageRate(
        address stakingToken,
        address rewardsToken,
        address rewardsPoolWithWETH9,
        uint32 duration
    ) external view returns (uint256 rate) {
        address multiRewards = IMultiRewardsFactory(multiRewardsFactory)
            .multiRewardsByStakingToken(stakingToken);
        if (multiRewards == address(0)) revert MultiRewardsNotInitialized();

        // reward rate is rewards per second
        (, , uint256 periodFinish, uint256 rewardRate, , ) = IMultiRewards(
            multiRewards
        ).rewardData(rewardsToken);
        if (block.timestamp > periodFinish) return 0;

        uint256 totalSupply = IMultiRewards(multiRewards).totalSupply();
        if (totalSupply == 0) revert MultiRewardsNotSupplied();

        uint256 rewards = (
            rewardsToken != WETH9
                ? quoteRewardInWETH9(
                    rewardsPoolWithWETH9,
                    rewardsToken,
                    rewardRate.toUint128()
                )
                : rewardRate
        );
        uint256 principal = quotePoolTokenInWETH9(stakingToken, totalSupply);
        rate = Math.mulDiv(rewards, (1e18 * uint256(duration)), principal);
    }

    /// @inheritdoc IAPR
    function quoteRewardInWETH9(
        address pool,
        address token,
        uint128 amount
    ) public view returns (uint256 value) {
        if (!PoolAddress.isPool(factory, pool)) revert InvalidPool();

        address token0 = IMarginalV1Pool(pool).token0();
        address token1 = IMarginalV1Pool(pool).token1();
        if (
            (token0 != WETH9 && token1 != WETH9) ||
            (token0 != token && token1 != token)
        ) revert InvalidTokens();

        // calculate the instantaneous value of the reward token amount in WETH9 terms
        (uint160 sqrtPriceX96, , , , , , , ) = IMarginalV1Pool(pool).state();
        if (sqrtPriceX96 == 0) revert PoolNotInitialized();

        value = (
            token0 == WETH9
                ? Math.mulDiv(
                    amount,
                    FixedPoint128.Q128,
                    Math.mulDiv(sqrtPriceX96, sqrtPriceX96, FixedPoint64.Q64)
                )
                : Math.mulDiv(
                    amount,
                    Math.mulDiv(sqrtPriceX96, sqrtPriceX96, FixedPoint64.Q64),
                    FixedPoint128.Q128
                )
        );
    }

    /// @inheritdoc IAPR
    function quotePoolTokenInWETH9(
        address pool,
        uint256 shares
    ) public view returns (uint256 value) {
        if (!PoolAddress.isPool(factory, pool)) revert InvalidPool();

        address token0 = IMarginalV1Pool(pool).token0();
        address token1 = IMarginalV1Pool(pool).token1();
        if (token0 != WETH9 && token1 != WETH9) revert InvalidTokens();

        // calculate the instantaneous value of the LP token in WETH9 terms
        (uint160 sqrtPriceX96, , uint128 liquidity, , , , , ) = IMarginalV1Pool(
            pool
        ).state();
        if (sqrtPriceX96 == 0) revert PoolNotInitialized();

        uint128 liquidityLocked = IMarginalV1Pool(pool).liquidityLocked();
        uint128 totalLiquidity = liquidity + liquidityLocked;

        uint256 totalValue = (
            token0 == WETH9
                ? 2 *
                    ((uint256(totalLiquidity) << FixedPoint96.RESOLUTION) /
                        sqrtPriceX96)
                : 2 *
                    Math.mulDiv(totalLiquidity, sqrtPriceX96, FixedPoint96.Q96)
        );
        uint256 totalSupply = IMarginalV1Pool(pool).totalSupply();
        value = Math.mulDiv(totalValue, shares, totalSupply);
    }
}
