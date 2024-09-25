import pytest


@pytest.fixture
def multirewards_initialized_with_stake(multirewards_initialized, admin):
    amount = int(100) * int(1e18)
    multirewards_initialized.stake(amount, sender=admin)
    return multirewards_initialized


def test_multirewards_get_reward__updates_rewards(
    multirewards_initialized_with_stake, mrgl, chain, admin
):
    # mine chain forward to earn rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    # stake again so rewards != 0
    multirewards_initialized_with_stake.stake(1, sender=admin)
    rewards_before = multirewards_initialized_with_stake.rewards(
        admin.address, mrgl.address
    )
    assert rewards_before > 0

    # mine chain forward to earn more rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    earned = multirewards_initialized_with_stake.earned(admin.address, mrgl.address)
    assert earned > rewards_before
    multirewards_initialized_with_stake.getReward(sender=admin)
    rewards = multirewards_initialized_with_stake.rewards(admin.address, mrgl.address)
    assert rewards == 0


def test_multirewards_get_reward__transfers_funds(
    multirewards_initialized_with_stake, mrgl, chain, admin
):
    balance_rewards = mrgl.balanceOf(multirewards_initialized_with_stake.address)
    balance_user = mrgl.balanceOf(admin.address)

    # mine chain forward to earn rewards
    reward_data = multirewards_initialized_with_stake.rewardData(mrgl.address)
    dt = reward_data.rewardsDuration // 4
    chain.mine(deltatime=dt)

    earned = multirewards_initialized_with_stake.earned(admin.address, mrgl.address)
    multirewards_initialized_with_stake.getReward(sender=admin)

    balance_rewards_after = mrgl.balanceOf(multirewards_initialized_with_stake.address)
    balance_user_after = mrgl.balanceOf(admin.address)

    # use pytest approx since 1 sec off
    assert pytest.approx(balance_rewards_after, rel=1e-6) == balance_rewards - earned
    assert pytest.approx(balance_user_after, rel=1e-6) == balance_user + earned
