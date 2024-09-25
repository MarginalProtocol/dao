def test_mrgl_constructor__sets_roles(mrgl, admin):
    deploy_time = mrgl.receipt.timestamp
    assert mrgl.owner() == admin.address
    assert mrgl.mintingAllowedAfter() == deploy_time + mrgl.minimumTimeBetweenMints()
    assert mrgl.totalSupply() == mrgl.initialSupply()
    assert mrgl.balanceOf(admin.address) == mrgl.initialSupply()
