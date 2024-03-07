def test_points_constructor__sets_token(points, mrgl):
    assert points.token() == mrgl.address
