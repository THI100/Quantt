For this 0.1.1 version update: The plan is mainly to add support to the supposely suported exchanges, and do optimizing of the qdata folder and the profiles present on it, instead of different .json files, change it to the database and add support for multiple profiles and selection of those by the UI.

  1. Add Support for exchanges, fix on execution folder (X)
  2. Make optimizations on the API timing. (X)
    2.1. Usual keywords to optimize: time.sleep, .reset(), safe_exchange_call, client (X)
    2.2. Substitute with universal API timer gen_limiter.wait() from utils.rate_lim.py (X)
  3. Optimization of .json system, fix on config and persistance folder
  4. Add the profiles into the database, fix on persistance folder
  5. Add DEXs to the app (dydx, lighter, aster, hyperliquid) (X)
  6. If a order is taken out by the user, this position is now open.
  7. Update that MEXC doesnt have an demo trading mode on the UI.

Generalized goals:

  1. Make a CI/CD with github actions to compile the Backend, Frontend, and wrap both in electron.
