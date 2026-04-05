Bot Control:
  @route.post("/bot/start")
  @route.post("/bot/stop")
  @route.post("/bot/restart")
  @route.post("/bot/pause")
  @route.post("/bot/resume")
  @route.get("/bot/status")

Control of position:
  @r_route.get("/positions/{symbol}")
  @r_route.delete("/positions/{symbol}")
  
Static (Direct usage):
  @r_route.get("/report/summary")
  @r_route.get("/report/best-worst")
  @r_route.get("/report/win-rate")
  @r_route.get("/report/hold-time")
  @r_route.get("/report/max-drawdown")
  @r_route.get("/report/sharpe")
  @r_route.get("/report/streaks")
  
Series (graph creation):
  @r_route.get("/report/trades")
  @r_route.get("/report/equity-curve")
  @r_route.get("/report/daily-pnl")
  @r_route.get("/report/drawdown")
  @r_route.get("/report/daily-trade-count")
  
Configuration setup (Trading):
  @s_route.get("/config/trading", response_model=settings.TradingConfig)
  @s_route.put("/config/trading", response_model=settings.TradingConfig)
  @s_route.patch("/config/trading", response_model=settings.TradingConfig)

Configuration setup (Risk):
  @s_route.get("/config/risk", response_model=risk.RiskConfig)
  @s_route.put("/config/risk", response_model=risk.RiskConfig)
  @s_route.patch("/config/risk", response_model=risk.RiskConfig)

Limits of margin and position (USDT or USDC):
  @s_route.get("/config/risk/limits")
