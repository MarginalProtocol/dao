import pytest


@pytest.fixture
def multirewards_initialized_with_stake(multirewards_initialized, admin):
    amount = int(100) * int(1e18)
    multirewards_initialized.stake(amount, sender=admin)
    return multirewards_initialized


def test_multirewards_withdraw__updates_reward(
    multirewards_initialized_with_stake, staking_token, admin, mrgl, chain
):
    # mine chain forward to earn rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    reward_per_token = multirewards_initialized_with_stake.rewardPerToken(mrgl.address)
    earned = multirewards_initialized_with_stake.earned(admin.address, mrgl.address)

    timestamp = chain.pending_timestamp
    amount = int(50) * int(1e18)
    multirewards_initialized_with_stake.withdraw(amount, sender=admin)

    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    rewards = multirewards_initialized_with_stake.rewards(admin.address, mrgl.address)
    user_reward_per_token_paid = (
        multirewards_initialized_with_stake.userRewardPerTokenPaid(
            admin.address, mrgl.address
        )
    )

    # @dev use pytest approx given 1s diff
    assert reward_data.lastUpdateTime == timestamp
    assert pytest.approx(reward_data.rewardPerTokenStored, rel=1e-6) == reward_per_token
    assert pytest.approx(rewards, rel=1e-6) == earned
    assert (
        pytest.approx(user_reward_per_token_paid, rel=1e-6)
        == reward_data.rewardPerTokenStored
    )


def test_multirewards_withdraw__updates_balance(
    multirewards_initialized_with_stake, staking_token, admin, mrgl, chain
):
    # mine chain forward to earn rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    balance = multirewards_initialized_with_stake.balanceOf(admin.address)
    total_supply = multirewards_initialized_with_stake.totalSupply()

    amount = int(50) * int(1e18)
    multirewards_initialized_with_stake.withdraw(amount, sender=admin)

    balance_after = multirewards_initialized_with_stake.balanceOf(admin.address)
    total_supply_after = multirewards_initialized_with_stake.totalSupply()

    assert balance_after == balance - amount
    assert total_supply_after == total_supply - amount


def test_multirewards_withdraw__transfers_funds(
    multirewards_initialized_with_stake, staking_token, admin, mrgl, chain
):
    # mine chain forward to earn rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    balance_rewards = staking_token.balanceOf(
        multirewards_initialized_with_stake.address
    )
    balance_user = staking_token.balanceOf(admin.address)

    amount = int(50) * int(1e18)
    multirewards_initialized_with_stake.withdraw(amount, sender=admin)

    balance_rewards_after = staking_token.balanceOf(
        multirewards_initialized_with_stake.address
    )
    balance_user_after = staking_token.balanceOf(admin.address)

    assert balance_rewards_after == balance_rewards - amount
    assert balance_user_after == balance_user + amount
