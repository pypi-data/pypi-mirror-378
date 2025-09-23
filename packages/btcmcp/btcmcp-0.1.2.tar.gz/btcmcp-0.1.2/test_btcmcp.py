from btcmcp import get_btc_price


def test_get_btc_price():
    """Test BTC price function"""
    price = get_btc_price()
    if price is not None:
        print(f"✅ BTC price: ${price:,.2f}")
    else:
        print("❌ Failed to get BTC price")


if __name__ == '__main__':
    test_get_btc_price()
