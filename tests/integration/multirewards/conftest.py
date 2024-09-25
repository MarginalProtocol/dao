import pytest


@pytest.fixture(scope="module")
def assert_mainnet_fork(networks):
    assert (
        networks.active_provider.network.name == "mainnet-fork"
    ), "network not set to mainnet-fork"


@pytest.fixture(scope="module")
def whale(assert_mainnet_fork, accounts):
    return accounts["0x5bdf85216ec1e38D6458C870992A69e38e03F7Ef"]  # bitget


@pytest.fixture(scope="module")
def WETH9(assert_mainnet_fork, Contract):
    return Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="module")
def MOG(assert_mainnet_fork, Contract):
    return Contract("0xaaeE1A9723aaDB7afA2810263653A34bA2C21C7a")


@pytest.fixture(scope="module")
def BITCOIN(assert_mainnet_fork, Contract):
    return Contract("0x72e4f9F808C49A2a61dE9C5896298920Dc4EEEa9")


@pytest.fixture(scope="module")
def margv1_factory(assert_mainnet_fork, Contract):
    return Contract("0x95D95C41436C15b50217Bf1C0f810536AD181C13")


@pytest.fixture(scope="module")
def margv1_router(assert_mainnet_fork, Contract):
    return Contract("0xD8FDd7357cBD8b88e690c9266608092eEFE7123b")


@pytest.fixture(scope="module")
def margv1_pool(assert_mainnet_fork, Contract):
    # MOG/WETH 5x pool
    return Contract("0x3A6C55Ce74d940A9B5dDDE1E57eF6e70bC8757A7")


@pytest.fixture(scope="module")
def another_margv1_pool(assert_mainnet_fork, Contract):
    # BITCOIN/WETH 5x pool
    return Contract("0x781563be135D827D7eA23d918711bE2D92F20166")


@pytest.fixture(scope="module")
def margv1_staking_token(assert_mainnet_fork, margv1_pool):
    return margv1_pool


@pytest.fixture(scope="module")
def margv1_reward_amount():
    return int(4.5 * 1e5) * int(1e8)


@pytest.fixture(scope="module")
def margv1_rewards_token(
    assert_mainnet_fork, BITCOIN, margv1_reward_amount, whale, admin
):
    BITCOIN.transfer(admin.address, margv1_reward_amount, sender=whale)
    return BITCOIN


@pytest.fixture(scope="module")
def margv1_apr(project, admin, margv1_factory, WETH9, multirewards_factory):
    return project.APR.deploy(
        margv1_factory.address,
        WETH9.address,
        multirewards_factory.address,
        sender=admin,
    )


@pytest.fixture(scope="module")
def margv1_multirewards(
    assert_mainnet_fork, project, admin, margv1_staking_token, multirewards_factory
):
    # MOG/WETH pool as staking token with BITCOIN as rewards token
    tx = multirewards_factory.deploy(margv1_staking_token.address, sender=admin)
    multirewards_address = tx.decode_logs(multirewards_factory.Deploy)[0].multiRewards
    return project.MultiRewards.at(multirewards_address)


@pytest.fixture(scope="module")
def margv1_multirewards_initialized(
    assert_mainnet_fork,
    multirewards_factory,
    margv1_multirewards,
    margv1_staking_token,
    margv1_rewards_token,
    margv1_reward_amount,
    admin,
    chain,
):
    multirewards_factory.addReward(
        margv1_staking_token.address,
        margv1_rewards_token.address,
        margv1_reward_amount,
        sender=admin,
    )
    margv1_rewards_token.transfer(
        multirewards_factory.address, margv1_reward_amount, sender=admin
    )

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    multirewards_factory.notifyRewardAmount(
        margv1_staking_token.address, margv1_rewards_token.address, sender=admin
    )
    margv1_staking_token.approve(
        margv1_multirewards.address, 2**256 - 1, sender=admin
    )
    return margv1_multirewards


@pytest.fixture(scope="module")
def margv1_pool_initialized_with_liquidity(
    assert_mainnet_fork, margv1_pool, margv1_router, MOG, whale, admin
):
    amount = MOG.balanceOf(whale.address)
    MOG.transfer(admin.address, amount, sender=whale)
    MOG.approve(margv1_router.address, 2**256 - 1, sender=admin)

    state = margv1_pool.state()
    amount0_desired = amount // 10
    amount1_desired = (amount0_desired * state.sqrtPriceX96**2) // (1 << 192)
    params = (
        margv1_pool.token0(),
        margv1_pool.token1(),
        margv1_pool.maintenance(),
        margv1_pool.oracle(),
        admin.address,
        amount0_desired,
        amount1_desired,
        0,
        0,
        2**256 - 1,
    )
    margv1_router.addLiquidity(params, sender=admin, value=amount1_desired)
    return margv1_pool
