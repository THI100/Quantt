For this 0.1.1 version update: The plan is mainly to add support to the supposely suported exchanges, and do optimizing of the qdata folder and the profiles present on it, instead of different .json files, change it to the database and add support for multiple profiles and selection of those by the UI.

  1. Add Support for exchanges, fix on execution folder (X)
  2. Make optimizations on the API timing. (X)
    2.1. Usual keywords to optimize: time.sleep, .reset(), safe_exchange_call, client (X)
    2.2. Substitute with universal API timer gen_limiter.wait() from utils.rate_lim.py (X)
  3. Optimization of .json system, fix on config and persistance folder and api/set.py checkup (X)
    3.1. Needs to add the UI to support the new changes. (X)
    3.2. Needs to now support the new system, update on the watcher class.
    3.3. Add a return of the active profiles and exchange in the start of the trading session.
    3.4. Add dependency of a last.json, so that the options form the last trading session of the user gets saved and is used to show the last results to the user.
  4. Add the profiles into the database, fix on persistance folder (X)
  5. Add DEXs to the app (dydx, lighter, aster, hyperliquid) (X)
  6. If a order is taken out by the user, this position is now open. (X)
  7. Update that MEXC doesnt have an demo trading mode on the UI. (X)
  8. Correct the usage of get_orders for the functionability of bybit, utilizing other methods to cover the function: manage_open_symbols, update is located in line 33, the update will be executed within data.fetch. (X)
  9. Update the link of new relationship of exchange order code to exchange within persistance.models, and make sure it is working.

Generalized goals:

  1. Make a CI/CD with github actions to compile the Backend, Frontend, and wrap both in electron.
