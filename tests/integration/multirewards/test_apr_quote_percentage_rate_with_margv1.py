import pytest


@pytest.mark.integration
def test_apr_quote_percentage_rate_with_margv1__returns_rate_when_rewards_token_not_WETH9(
    margv1_apr,
    margv1_multirewards_initialized,
    margv1_pool_initialized_with_liquidity,
    another_margv1_pool,
    WETH9,
    MOG,
    margv1_staking_token,
    margv1_rewards_token,
    margv1_reward_amount,
    margv1_router,
    admin,
):
    assert (
        margv1_staking_token.address == margv1_pool_initialized_with_liquidity.address
    )
    assert margv1_rewards_token.address == another_margv1_pool.token0()

    # stake admin shares in multirewards
    shares = margv1_pool_initialized_with_liquidity.balanceOf(admin.address)
    pool_total_supply = margv1_pool_initialized_with_liquidity.totalSupply()
    assert shares < pool_total_supply

    margv1_multirewards_initialized.stake(shares, sender=admin)
    multirewards_total_supply = margv1_multirewards_initialized.totalSupply()
    assert multirewards_total_supply == shares

    # look at 1 year
    duration = int(86400 * 365)
    result = margv1_apr.quotePercentageRate(
        margv1_staking_token.address,
        margv1_rewards_token.address,
        another_margv1_pool.address,
        duration,
    )

    data = margv1_multirewards_initialized.rewardData(margv1_rewards_token.address)
    rewards = margv1_apr.quoteRewardInWETH9(
        another_margv1_pool.address, margv1_rewards_token.address, data.rewardRate
    )
    principal = margv1_apr.quotePoolTokenInWETH9(margv1_staking_token.address, shares)
    rate = (rewards * duration * int(1e18)) // principal
    assert rate == result


# TODO: test when rewards token is WETH9
