from ape import reverts


def test_mrgl_mint__mints_tokens(mrgl, admin, alice):
    amount = 100000000000000000000000000  # 100M
    balance = mrgl.balanceOf(alice)
    total_supply = mrgl.totalSupply()
    mrgl.mint(alice, amount, sender=admin)
    assert mrgl.balanceOf(alice) == balance + amount
    assert mrgl.totalSupply() == total_supply + amount


def test_mrgl_mint__reverts_when_not_minter_role(mrgl, alice):
    amount = 100000000000000000000000000  # 100M
    with reverts():
        mrgl.mint(alice, amount, sender=alice)
