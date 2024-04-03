from ape import reverts


def test_multirewards_add_reward__reverts_when_not_owner(multirewards, alice, mrgl):
    with reverts("Ownable: caller is not the owner"):
        multirewards.addReward(mrgl.address, alice.address, 86400, sender=alice)
