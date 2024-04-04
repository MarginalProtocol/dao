from ape import reverts
from ape.utils import ZERO_ADDRESS


def test_multirewards_factory_deploy__deploys_multirewards(
    project, multirewards_factory, token_a, admin
):
    multirewards_factory.deploy(token_a.address, sender=admin)

    multirewards_address = multirewards_factory.multiRewardsByStakingToken(
        token_a.address
    )
    assert multirewards_address != ZERO_ADDRESS
    assert (
        project.MultiRewards.at(multirewards_address).stakingToken() == token_a.address
    )


def test_multirewards_factory_deploy__emits_deploy(
    multirewards_factory, token_a, admin
):
    tx = multirewards_factory.deploy(token_a.address, sender=admin)
    multirewards_address = multirewards_factory.multiRewardsByStakingToken(
        token_a.address
    )

    events = tx.decode_logs(multirewards_factory.Deploy)
    assert len(events) == 1

    event = events[0]
    assert event.stakingToken == token_a.address
    assert event.multiRewards == multirewards_address


def test_multirewards_factory_deploy__reverts_when_not_owner(
    multirewards_factory, token_a, alice
):
    with reverts("Ownable: caller is not the owner"):
        multirewards_factory.deploy(token_a, sender=alice)


def test_multirewards_factory_deploy__reverts_when_already_deployed(
    multirewards_factory, multirewards, staking_token, admin
):
    assert (
        multirewards_factory.multiRewardsByStakingToken(staking_token.address)
        == multirewards.address
    )
    with reverts("MultiRewardsFactory::deploy: already deployed"):
        multirewards_factory.deploy(staking_token.address, sender=admin)
