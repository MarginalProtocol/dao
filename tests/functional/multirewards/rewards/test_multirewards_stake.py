def test_multirewards_stake__updates_reward(
    multirewards_initialized, staking_token, admin, mrgl, chain
):
    # first stake to update
    timestamp0 = chain.pending_timestamp
    amount0 = int(100) * int(1e18)
    reward0_per_token = multirewards_initialized.rewardPerToken(mrgl.address)
    multirewards_initialized.stake(amount0, sender=admin)

    earned0 = multirewards_initialized.earned(admin.address, mrgl.address)
    reward_data0 = multirewards_initialized.rewardData(mrgl.address)
    rewards0 = multirewards_initialized.rewards(admin.address, mrgl.address)
    user_reward_per_token_paid0 = multirewards_initialized.userRewardPerTokenPaid(
        admin.address, mrgl.address
    )

    assert reward_data0.lastUpdateTime == timestamp0
    assert reward_data0.rewardPerTokenStored == reward0_per_token
    assert rewards0 == earned0
    assert user_reward_per_token_paid0 == reward_data0.rewardPerTokenStored

    # mine chain forward to earn rewards
    dt = reward_data0.rewardsDuration // 4
    chain.mine(deltatime=dt)

    # second stake to update
    timestamp1 = chain.pending_timestamp
    amount1 = int(10) * int(1e18)

    multirewards_initialized.stake(amount1, sender=admin)

    reward1_per_token = multirewards_initialized.rewardPerToken(mrgl.address)
    earned1 = multirewards_initialized.earned(admin.address, mrgl.address)
    reward_data1 = multirewards_initialized.rewardData(mrgl.address)
    rewards1 = multirewards_initialized.rewards(admin.address, mrgl.address)
    user_reward_per_token_paid1 = multirewards_initialized.userRewardPerTokenPaid(
        admin.address, mrgl.address
    )

    assert reward_data1.lastUpdateTime == timestamp1
    assert reward_data1.rewardPerTokenStored == reward1_per_token
    assert rewards1 == earned1
    assert user_reward_per_token_paid1 == reward_data1.rewardPerTokenStored


def test_multirewards_stake__updates_balance(
    multirewards_initialized, staking_token, admin, mrgl, chain
):
    amount = int(100) * int(1e18)
    multirewards_initialized.stake(amount, sender=admin)
    assert multirewards_initialized.balanceOf(admin.address) == amount
    assert multirewards_initialized.totalSupply() == amount


def test_multirewards_stake__transfers_funds(
    multirewards_initialized, staking_token, admin, mrgl, chain
):
    amount = int(100) * int(1e18)
    balance_user = staking_token.balanceOf(admin.address)
    balance_rewards = staking_token.balanceOf(multirewards_initialized.address)

    multirewards_initialized.stake(amount, sender=admin)
    assert staking_token.balanceOf(admin.address) == balance_user - amount
    assert (
        staking_token.balanceOf(multirewards_initialized.address)
        == balance_rewards + amount
    )
