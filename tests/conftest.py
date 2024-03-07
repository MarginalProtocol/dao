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
def points(project, mrgl, admin):
    return project.PointsStaking.deploy(mrgl.address, sender=admin)
