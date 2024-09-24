import pytest


@pytest.fixture(scope="module")
def mrgl_reward_amount():
    return int(0.0105 * 100 * 1e6) * int(1e18)


@pytest.fixture(scope="module")
def multirewards_initialized(
    multirewards_factory,
    multirewards,
    staking_token,
    mrgl,
    mrgl_reward_amount,
    admin,
    chain,
):
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, mrgl_reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, mrgl_reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=admin
    )
    staking_token.approve(multirewards.address, 2**256 - 1, sender=admin)
    return multirewards


# TODO: create marg v1 pools for stake, mrgl (reward) vs WETH9 from marg v1 factory
