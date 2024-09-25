from ape import reverts


def test_multirewards_factory_notify_reward_amount__notifies_reward_amount(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    timestamp = chain.pending_timestamp
    multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=alice
    )

    rewards_duration = multirewards_factory.rewardsDuration()
    reward_data = multirewards.rewardData(mrgl.address)
    assert reward_data.rewardRate == reward_amount // rewards_duration
    assert reward_data.lastUpdateTime == timestamp
    assert reward_data.periodFinish == timestamp + rewards_duration


def test_multirewards_factory_notify_reward_amount__updates_reward_info(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=alice
    )

    info = multirewards_factory.rewardsInfoByStakingAndRewardsToken(
        staking_token.address, mrgl.address
    )
    assert info.rewardAmount == 0
    assert info.initialized is True


def test_multirewards_factory_notify_reward_amount__transfers_funds(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    # cache balances before
    balance_factory = mrgl.balanceOf(multirewards_factory.address)
    balance_rewards = mrgl.balanceOf(multirewards.address)

    multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=alice
    )
    assert (
        mrgl.balanceOf(multirewards_factory.address) == balance_factory - reward_amount
    )
    assert mrgl.balanceOf(multirewards.address) == balance_rewards + reward_amount


def test_multirewards_factory_notify_reward_amount__emits_notify_reward_amount(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    tx = multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=alice
    )
    events = tx.decode_logs(multirewards_factory.NotifyRewardAmount)
    assert len(events) == 1

    event = events[0]
    assert event.stakingToken == staking_token.address
    assert event.rewardsToken == mrgl.address
    assert event.rewardAmount == reward_amount


def test_multirewards_factory_notify_reward_amount__reverts_when_not_ready(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    with reverts("MultiRewardsFactory::notifyRewardAmount: not ready"):
        multirewards_factory.notifyRewardAmount(
            staking_token.address, mrgl.address, sender=alice
        )


def test_multirewards_factory_notify_reward_amount__reverts_when_not_deployed(
    multirewards_factory, multirewards, token_b, mrgl, admin, alice, chain
):
    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    with reverts("MultiRewardsFactory::notifyRewardAmount: not deployed"):
        multirewards_factory.notifyRewardAmount(
            token_b.address, mrgl.address, sender=alice
        )


def test_multirewards_factory_notify_reward_amount__passes_when_not_added(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    info = multirewards_factory.rewardsInfoByStakingAndRewardsToken(
        staking_token.address, mrgl.address
    )
    assert info.rewardAmount == 0

    # should succeed with nothing happening
    multirewards_factory.notifyRewardAmount(
        staking_token.address, mrgl.address, sender=alice
    )
    reward_data = multirewards.rewardData(mrgl.address)

    assert mrgl.balanceOf(multirewards_factory.address) == reward_amount
    assert reward_data.lastUpdateTime == 0


def test_multirewards_factory_notify_reward_amount__reverts_when_not_funded(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    with reverts():
        multirewards_factory.notifyRewardAmount(
            staking_token.address, mrgl.address, sender=alice
        )
