from ape import reverts
from ape.utils import ZERO_ADDRESS


def test_mrgl_mint__mints_tokens(mrgl, admin, alice, chain):
    amount = 10000000000000000000000000  # 10M
    balance = mrgl.balanceOf(alice)
    total_supply = mrgl.totalSupply()

    minting_allowed_after = mrgl.mintingAllowedAfter()
    chain.mine(timestamp=minting_allowed_after)
    mrgl.mint(alice, amount, sender=admin)

    assert mrgl.balanceOf(alice) == balance + amount
    assert mrgl.totalSupply() == total_supply + amount


def test_mrgl_mint__sets_next_minting_allowed_time(mrgl, admin, alice, chain):
    amount = 10000000000000000000000000  # 10M
    minting_allowed_after = mrgl.mintingAllowedAfter()

    chain.mine(timestamp=minting_allowed_after)
    next_timestamp = chain.pending_timestamp

    mrgl.mint(alice, amount, sender=admin)
    assert mrgl.mintingAllowedAfter() == next_timestamp + mrgl.minimumTimeBetweenMints()


def test_mrgl_mint__reverts_when_not_minter_role(mrgl, alice, chain):
    amount = 10000000000000000000000000  # 10M
    minting_allowed_after = mrgl.mintingAllowedAfter()
    chain.mine(timestamp=minting_allowed_after)
    with reverts("not minter"):
        mrgl.mint(alice, amount, sender=alice)


def test_mrgl_mint__reverts_when_not_allowed_yet(mrgl, admin, alice):
    amount = 10000000000000000000000000  # 10M
    with reverts("minting not allowed yet"):
        mrgl.mint(alice, amount, sender=admin)


def test_mrgl_mint__reverts_when_to_zero_address(mrgl, admin, chain):
    amount = 10000000000000000000000000  # 10M
    minting_allowed_after = mrgl.mintingAllowedAfter()
    chain.mine(timestamp=minting_allowed_after)
    with reverts("minting to zero address"):
        mrgl.mint(ZERO_ADDRESS, amount, sender=admin)


def test_mrgl_mint__reverts_when_exceed_mint_cap(mrgl, admin, alice, chain):
    assert mrgl.initialSupply() == 1000000000000000000000000000
    assert mrgl.mintCap() == 2

    amount = 50000000000000000000000001  # 50M + 1 wei
    minting_allowed_after = mrgl.mintingAllowedAfter()
    chain.mine(timestamp=minting_allowed_after)

    with reverts("exceeded mint cap"):
        mrgl.mint(alice, amount, sender=admin)
