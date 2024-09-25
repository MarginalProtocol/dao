from ape import reverts


def test_multirewards_factory_add_reward__adds_reward_when_not_initialized(
    multirewards_factory, multirewards, staking_token, mrgl, admin
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )

    reward_data = multirewards.rewardData(mrgl.address)
    assert reward_data.rewardsDistributor == multirewards_factory.address
    assert reward_data.rewardsDuration == multirewards_factory.rewardsDuration()


def test_multirewards_factory_add_reward__stores_reward_info_when_not_initialized(
    multirewards_factory, multirewards, staking_token, mrgl, admin
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )

    info = multirewards_factory.rewardsInfoByStakingAndRewardsToken(
        staking_token.address, mrgl.address
    )
    assert info.rewardAmount == reward_amount
    assert info.initialized is True


def test_multirewards_factory_add_reward__updates_reward_info_when_initialized(
    multirewards_factory, multirewards, staking_token, mrgl, admin, alice, chain
):
    # first round of rewards
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    # notify first round of rewards in multirewards
    multirewards_factory.notifyRewardAmounts(mrgl.address, sender=alice)

    info = multirewards_factory.rewardsInfoByStakingAndRewardsToken(
        staking_token.address, mrgl.address
    )
    assert info.rewardAmount == 0
    assert info.initialized is True

    # mine the chain half rewards duration for some time
    rewards_duration = multirewards_factory.rewardsDuration()
    dt = rewards_duration // 2
    chain.mine(deltatime=dt)

    # second round of rewards
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    info = multirewards_factory.rewardsInfoByStakingAndRewardsToken(
        staking_token.address, mrgl.address
    )
    assert info.rewardAmount == reward_amount
    assert info.initialized is True


def test_multirewards_factory_add_reward__emits_add_reward(
    multirewards_factory, multirewards, staking_token, mrgl, admin
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    tx = multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )

    events = tx.decode_logs(multirewards_factory.AddReward)
    assert len(events) == 1

    event = events[0]
    assert event.stakingToken == staking_token.address
    assert event.rewardsToken == mrgl.address
    assert event.rewardAmount == reward_amount


def test_multirewards_factory_add_reward__reverts_when_not_owner(
    multirewards_factory, multirewards, staking_token, mrgl, alice
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    with reverts("Ownable: caller is not the owner"):
        multirewards_factory.addReward(
            staking_token.address, mrgl.address, reward_amount, sender=alice
        )


def test_multirewards_factory_add_reward__reverts_when_not_deployed(
    multirewards_factory, multirewards, token_a, mrgl, admin
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    with reverts("MultiRewardsFactory::addReward: not deployed"):
        multirewards_factory.addReward(
            token_a.address, mrgl.address, reward_amount, sender=admin
        )


def test_multirewards_factory_add_reward__reverts_when_already_added(
    multirewards_factory, multirewards, staking_token, mrgl, admin
):
    reward_amount = int(0.0105 * 100 * 1e6) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    with reverts("MultiRewardsFactory::addReward: already added"):
        multirewards_factory.addReward(
            staking_token.address, mrgl.address, reward_amount, sender=admin
        )


def test_multirewards_factory_add_reward__reverts_when_exceeds_max_reward_tokens(
    multirewards_factory, multirewards, mrgl, staking_token, create_token, admin
):
    max_reward_tokens = multirewards.maxRewardTokens()

    # all should pass
    for i in range(max_reward_tokens):
        reward_amount = int((i + 1) * 100 * 1e6) * int(1e18)
        token = create_token(f"token-{i}", decimals=18)
        multirewards_factory.addReward(
            staking_token.address, token.address, reward_amount, sender=admin
        )

    # should revert since would exceed max
    reward_amount = int((max_reward_tokens + 1) * 100 * 1e6) * int(1e18)
    with reverts("MultiRewards::addReward: Cannot add more than max"):
        multirewards_factory.addReward(
            staking_token.address, mrgl.address, reward_amount, sender=admin
        )
