from ape import reverts


def test_multirewards_factory_constructor__reverts_when_genesis_too_soon(
    project, chain, admin
):
    genesis = chain.pending_timestamp - 1
    with reverts("MultiRewardsFactory::constructor: genesis too soon"):
        project.MultiRewardsFactory.deploy(genesis, sender=admin)
