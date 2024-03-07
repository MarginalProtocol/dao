import pytest

from ape import reverts


@pytest.fixture
def points_initialized(points, mrgl, admin):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)
    amount = (mrgl.balanceOf(admin.address) * 1) // 100
    points.lock(amount, sender=admin)
    return points


def test_points_free__updates_stake(points_initialized, mrgl, admin, chain):
    stake = points_initialized.stakes(admin.address)
    amount = stake.balance // 2
    chain.mine(deltatime=86400)

    timestamp = chain.pending_timestamp
    points_initialized.free(amount, sender=admin)

    stake_after = points_initialized.stakes(admin.address)
    assert stake_after.balance == stake.balance - amount
    assert stake_after.blockTimestamp == timestamp % 2**32
    assert timestamp > stake.blockTimestamp


def test_points_free__transfers_funds(points_initialized, mrgl, admin, chain):
    stake = points_initialized.stakes(admin.address)
    amount = stake.balance // 2
    chain.mine(deltatime=86400)

    balance_admin = mrgl.balanceOf(admin.address)
    balance_points = mrgl.balanceOf(points_initialized.address)

    points_initialized.free(amount, sender=admin)

    balance_admin_after = mrgl.balanceOf(admin.address)
    balance_points_after = mrgl.balanceOf(points_initialized.address)

    assert balance_admin_after == balance_admin + amount
    assert balance_points_after == balance_points - amount


def test_points_free__emits_free(points_initialized, mrgl, admin, chain):
    stake = points_initialized.stakes(admin.address)
    amount = stake.balance // 2
    chain.mine(deltatime=86400)

    tx = points_initialized.free(amount, sender=admin)
    stake_after = points_initialized.stakes(admin.address)

    events = tx.decode_logs(points_initialized.Free)
    assert len(events) == 1

    event = events[0]
    assert event.sender == admin.address
    assert event.blockTimestampAfter == stake_after.blockTimestamp
    assert event.balanceAfter == stake_after.balance


def test_points_free__reverts_when_greater_than_stake_balance(
    points_initialized, mrgl, admin, chain
):
    stake = points_initialized.stakes(admin.address)
    amount = stake.balance + 1
    chain.mine(deltatime=86400)

    with reverts("amount > stake balance"):
        points_initialized.free(amount, sender=admin)
