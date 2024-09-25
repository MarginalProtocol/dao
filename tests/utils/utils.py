def calc_amounts_from_liquidity_sqrt_price_x96(
    liquidity: int, sqrt_price_x96: int
) -> (int, int):
    amount0 = (liquidity << 96) // sqrt_price_x96
    amount1 = (liquidity * sqrt_price_x96) // (1 << 96)
    return (amount0, amount1)
