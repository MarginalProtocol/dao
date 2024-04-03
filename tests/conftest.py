import pytest


@pytest.fixture(scope="session")
def admin(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def mrgl(project, admin):
    return project.MarginalToken.deploy(sender=admin)


@pytest.fixture(scope="session")
def create_token(project, accounts):
    def create_token(name, decimals=18):
        return project.Token.deploy(name, decimals, sender=accounts[0])

    yield create_token


@pytest.fixture(scope="session")
def token_a(create_token):
    return create_token("A", decimals=6)


@pytest.fixture(scope="session")
def token_b(create_token):
    return create_token("B", decimals=18)


@pytest.fixture(scope="session")
def staking_token(create_token):
    return create_token("STAKE", decimals=18)


@pytest.fixture(scope="session")
def points(project, mrgl, admin):
    return project.StakingPoints.deploy(mrgl.address, sender=admin)


@pytest.fixture(scope="session")
def multirewards_factory(project, admin, chain):
    genesis = chain.pending_timestamp + 3600  # genesis in an hour
    return project.MultiRewardsFactory.deploy(genesis, sender=admin)


@pytest.fixture(scope="session")
def multirewards(project, admin, staking_token, multirewards_factory):
    tx = multirewards_factory.deploy(staking_token.address, sender=admin)
    multirewards_address = tx.decode_logs(multirewards_factory.Deploy)[0].multiRewards
    return project.MultiRewards.at(multirewards_address)
