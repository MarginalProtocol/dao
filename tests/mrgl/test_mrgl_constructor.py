def test_mrgl_constructor__sets_roles(mrgl, admin):
    assert mrgl.owner() == admin.address
