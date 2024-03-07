from ape import reverts


def test_points_lock__updates_stake(points, mrgl, admin, chain):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)
    stake = points.stakes(admin.address)
    balance = stake.balance

    timestamp = chain.pending_timestamp
    amount = (mrgl.balanceOf(admin.address) * 1) // 100
    points.lock(amount, sender=admin)

    stake_after = points.stakes(admin.address)
    assert stake_after.balance == balance + amount
    assert stake_after.blockTimestamp == timestamp % 2**32


def test_point_lock__updates_stake_multiple(points, mrgl, admin, chain):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)
    stake = points.stakes(admin.address)
    balance = stake.balance

    amount = (mrgl.balanceOf(admin.address) * 1) // 100
    points.lock(amount, sender=admin)

    chain.mine(deltatime=86400)
    timestamp = chain.pending_timestamp
    points.lock(amount, sender=admin)

    stake_after = points.stakes(admin.address)
    assert stake_after.balance == balance + 2 * amount
    assert stake_after.blockTimestamp == timestamp % 2**32


def test_points_lock__transfers_funds(points, mrgl, admin, chain):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)
    balance_admin = mrgl.balanceOf(admin.address)
    balance_points = mrgl.balanceOf(points.address)

    amount = (mrgl.balanceOf(admin.address) * 1) // 100
    points.lock(amount, sender=admin)

    balance_admin_after = mrgl.balanceOf(admin.address)
    balance_points_after = mrgl.balanceOf(points.address)

    assert balance_admin_after == balance_admin - amount
    assert balance_points_after == balance_points + amount


def test_points_lock__emits_lock(points, mrgl, admin, chain):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)

    amount = (mrgl.balanceOf(admin.address) * 1) // 100
    tx = points.lock(amount, sender=admin)
    stake = points.stakes(admin.address)

    events = tx.decode_logs(points.Lock)
    assert len(events) == 1

    event = events[0]
    assert event.sender == admin.address
    assert event.blockTimestampAfter == stake.blockTimestamp
    assert event.balanceAfter == stake.balance


def test_points_lock__reverts_when_stake_balance_greater_than_uint224_max(
    points, mrgl, admin, chain
):
    mrgl.approve(points.address, 2**256 - 1, sender=admin)
    amount = 2**224
    with reverts("SafeCast: value doesn't fit in 224 bits"):
        points.lock(amount, sender=admin)
