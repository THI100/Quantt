from persistance.connection import SessionLocal, ensure_config_schema
from persistance.models import Last as LastRecord


class LastConfigManager:
    """Persist and retrieve the currently active trading and risk profiles."""

    nominal_key = "last"

    def get_last(self) -> dict[str, str]:
        """Read the active profile values from the database on every call."""
        ensure_config_schema()
        defaults = self._default_values()
        created = False
        with SessionLocal() as session:
            record = session.get(LastRecord, self.nominal_key)
            if record is None:
                session.add(LastRecord(nominal_key=self.nominal_key, **defaults))
                session.commit()
                created = True

        if created:
            # Re-run migrations now that the active row exists so legacy order
            # records can be associated with its exchange.
            ensure_config_schema()

        # Use a fresh session so callers always receive the persisted values.
        with SessionLocal() as session:
            record = session.get(LastRecord, self.nominal_key)
            if record is None:
                raise RuntimeError("Could not initialize the active profile record")
            return self._as_dict(record)

    def set_trading_profile(self, trading_name: str) -> dict[str, str]:
        from config import trading

        trading_config = trading.watcher.get_config(trading_name)
        return self._update(
            trading_name=trading_name,
            exchange=trading_config.exchange,
        )

    def set_risk_profile(self, risk_name: str) -> dict[str, str]:
        from config import risk

        risk.watcher.get_config(risk_name)
        return self._update(risk_name=risk_name)

    def _update(self, **values: str) -> dict[str, str]:
        ensure_config_schema()
        self.get_last()
        with SessionLocal() as session:
            record = session.get(LastRecord, self.nominal_key)
            if record is None:
                raise RuntimeError("Could not initialize the active profile record")

            for key, value in values.items():
                setattr(record, key, value)
            session.add(record)
            session.commit()

        return self.get_last()

    @staticmethod
    def _default_values() -> dict[str, str]:
        from config import risk, trading

        trading_config = LastConfigManager._ensure_base_trading_profile(trading)
        risk_config = LastConfigManager._ensure_base_risk_profile(risk)
        return {
            "exchange": trading_config.exchange,
            "trading_name": trading_config.name,
            "risk_name": risk_config.name,
        }

    @staticmethod
    def _ensure_base_trading_profile(trading_module):
        try:
            return trading_module.load_trading_config("base")
        except FileNotFoundError:
            from config.trading import TradingConfigPYD

            config = TradingConfigPYD(name="base")
            error = trading_module.save_trading_config(config)
            if error:
                raise RuntimeError(error)
            return config

    @staticmethod
    def _ensure_base_risk_profile(risk_module):
        try:
            return risk_module.load_risk_config("base")
        except FileNotFoundError:
            from config.risk import RiskConfigPYD

            config = RiskConfigPYD(name="base")
            error = risk_module.save_risk_config(config)
            if error:
                raise RuntimeError(error)
            return config

    @staticmethod
    def _as_dict(record: LastRecord) -> dict[str, str]:
        return {
            "nominal_key": record.nominal_key,
            "exchange": record.exchange,
            "trading_name": record.trading_name,
            "risk_name": record.risk_name,
        }


last = LastConfigManager()
