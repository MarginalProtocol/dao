import pytest

from utils.utils import calc_amounts_from_liquidity_sqrt_price_x96


@pytest.mark.integration
def test_apr_quote_pool_token_in_weth9_with_margv1__returns_value_when_token1_WETH9(
    margv1_apr,
    margv1_multirewards_initialized,
    margv1_pool,
    WETH9,
    margv1_staking_token,
    margv1_rewards_token,
    margv1_reward_amount,
):
    total_supply = margv1_staking_token.totalSupply()
    shares = total_supply // 2

    assert margv1_staking_token.address == margv1_pool.address
    result = margv1_apr.quotePoolTokenInWETH9(margv1_staking_token, shares)

    state = margv1_pool.state()
    liquidity_locked = margv1_pool.liquidityLocked()
    total_liquidity = state.liquidity + liquidity_locked

    (reserve0, reserve1) = calc_amounts_from_liquidity_sqrt_price_x96(
        total_liquidity, state.sqrtPriceX96
    )
    reserve = reserve1 if margv1_pool.token1() == WETH9.address else reserve0

    value = (2 * (reserve * shares)) // total_supply
    assert value == result


# TODO: test returns value when token0 == WETH9
