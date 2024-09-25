from ape import reverts


def test_multirewards_notify_reward_amount__reverts_when_not_distributor(
    multirewards_factory, multirewards, staking_token, mrgl, admin, project
):
    reward_amount = int(100000) * int(1e18)
    multirewards_factory.addReward(
        staking_token.address, mrgl.address, reward_amount, sender=admin
    )
    reward_data = multirewards.rewardData(mrgl.address)
    assert reward_data.rewardsDistributor == multirewards_factory.address

    with reverts():
        multirewards.notifyRewardAmount(mrgl.address, reward_amount, sender=admin)
