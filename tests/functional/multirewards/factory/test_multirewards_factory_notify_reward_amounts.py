def test_multirewards_factory_notify_reward_amounts__notifies_reward_amounts(
    project,
    multirewards_factory,
    multirewards,
    staking_token,
    mrgl,
    token_a,
    admin,
    alice,
    chain,
):
    reward0_amount = int(0.01 * 100 * 1e6) * int(1e18)
    reward1_amount = int(0.02 * 100 * 1e6) * int(1e18)
    reward_amount = reward0_amount + reward1_amount

    multirewards_factory.deploy(token_a.address, sender=admin)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward0_amount, sender=admin
    )
    multirewards_factory.addReward(
        token_a.address, mrgl.address, reward1_amount, sender=admin
    )
    mrgl.transfer(multirewards_factory.address, reward_amount, sender=admin)

    # mine the chain to move past staking genesis time
    genesis = multirewards_factory.stakingRewardsGenesis()
    dt = genesis - chain.pending_timestamp + 1
    chain.mine(deltatime=dt)

    timestamp = chain.pending_timestamp
    multirewards_factory.notifyRewardAmounts(mrgl.address, sender=alice)

    rewards_duration = multirewards_factory.rewardsDuration()
    reward_data = multirewards.rewardData(mrgl.address)  # staking token multirewards
    assert reward_data.rewardRate == reward0_amount // rewards_duration
    assert reward_data.lastUpdateTime == timestamp
    assert reward_data.periodFinish == timestamp + rewards_duration
    assert mrgl.balanceOf(multirewards.address) == reward0_amount

    multirewards_token_a_address = multirewards_factory.multiRewardsByStakingToken(
        token_a.address
    )
    multirewards_token_a = project.MultiRewards.at(multirewards_token_a_address)
    reward_data_token_a = multirewards_token_a.rewardData(
        mrgl.address
    )  # token A multirewards
    assert reward_data_token_a.rewardRate == reward1_amount // rewards_duration
    assert reward_data_token_a.lastUpdateTime == timestamp
    assert reward_data_token_a.periodFinish == timestamp + rewards_duration
    assert mrgl.balanceOf(multirewards_token_a.address) == reward1_amount
