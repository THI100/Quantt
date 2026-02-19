risk_reward_ratio = 2.0
maximum_loss = 0.15
profile = "moderate"
porcentage_of_capital_per_trade = 0

if porcentage_of_capital_per_trade == 0 and profile == "conservative":
    porcentage_of_capital_per_trade = 0.01
elif porcentage_of_capital_per_trade == 0 and profile == "moderate":
    porcentage_of_capital_per_trade = 0.02
elif porcentage_of_capital_per_trade == 0 and profile == "aggressive":
    porcentage_of_capital_per_trade = 0.03
