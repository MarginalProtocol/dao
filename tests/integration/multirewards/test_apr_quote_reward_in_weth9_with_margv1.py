import pytest


@pytest.mark.integration
def test_apr_quote_reward_in_weth9_with_margv1__returns_value_when_token1_WETH9(
    margv1_apr,
    margv1_multirewards_initialized,
    another_margv1_pool,
    WETH9,
    margv1_staking_token,
    margv1_rewards_token,
    margv1_reward_amount,
):
    data = margv1_multirewards_initialized.rewardData(margv1_rewards_token.address)
    amount = data.rewardRate
    result = margv1_apr.quoteRewardInWETH9(
        another_margv1_pool.address, margv1_rewards_token.address, amount
    )

    state = another_margv1_pool.state()
    value = (
        (amount * (state.sqrtPriceX96**2)) // (1 << 192)
        if another_margv1_pool.token0() == margv1_rewards_token.address
        else (amount * (1 << 192)) // (state.sqrtPriceX96**2)
    )
    assert value == result


# TODO: test returns value when token0 == WETH9
