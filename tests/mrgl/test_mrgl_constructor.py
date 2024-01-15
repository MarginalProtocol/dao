import pytest


@pytest.fixture
def DEFAULT_ADMIN_ROLE(mrgl):
    return mrgl.DEFAULT_ADMIN_ROLE()


@pytest.fixture
def MINTER_ROLE(mrgl):
    return mrgl.MINTER_ROLE()


def test_mrgl_constructor__sets_roles(mrgl, admin, DEFAULT_ADMIN_ROLE, MINTER_ROLE):
    assert mrgl.hasRole(DEFAULT_ADMIN_ROLE, admin) is True
    assert mrgl.hasRole(MINTER_ROLE, admin) is True
