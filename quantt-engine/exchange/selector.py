from config import settings

def get_exchange_client(exchange_name: str = settings.EXCHANGE):
    if exchange_name == "bybit":
        from exchange.bybit import bb_client
        return bb_client
    elif exchange_name == "binance":
        from exchange.binance import bi_client
        return bi_client
    elif exchange_name == "coinbase":
        from exchange.coinbase import cb_client
        return cb_client
    elif exchange_name == "okx":
        from exchange.okx import okx_client
        return okx_client
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")