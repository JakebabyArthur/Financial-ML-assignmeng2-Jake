import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize

#Download price data
tickers = ['JNJ','JPM','TSLA']
# Fetch from Jan 1, 2020 up through latest available date
prices = yf.download(
    tickers,
    start='2020-01-01',
    end='2025-07-25',
    auto_adjust=False 
)['Adj Close']

#Compute daily returns, then annualize
rets_daily = prices.pct_change().dropna()
μ_annual = rets_daily.mean() * 252
Σ_annual = rets_daily.cov() * 252

#Monte Carlo parameters
n_scenarios = 5_000
np.random.seed(123)
# simulate annual returns: shape (n_scenarios, 3)
sim_rets = np.random.multivariate_normal(μ_annual, Σ_annual, size=n_scenarios)

#generate weight vectors
def random_weights(n_assets, shorts_ok):
    if shorts_ok:
        # draw n-1 from U(-1,1), last = 1 - sum
        w = np.random.uniform(-1,1,size=n_assets-1)
        w = np.append(w, 1 - w.sum())
    else:
        w = np.random.rand(n_assets)
        w = w / w.sum()
    return w

#Monte Carlo portfolios
def mc_portfolios(sim_rets, n_portfolios, shorts_ok):
    results = np.zeros((n_portfolios, 2))  # columns: [risk, return]
    for i in range(n_portfolios):
        w = random_weights(sim_rets.shape[1], shorts_ok)
        # compute scenario returns: shape (n_scenarios,)
        port_scen_rets = sim_rets.dot(w)
        results[i,1] = port_scen_rets.mean()      # mean return
        results[i,0] = port_scen_rets.std(ddof=1) # std dev
    return results

np.random.seed(999)
mc_longshort = mc_portfolios(sim_rets, 2_000, shorts_ok=True)
np.random.seed(999)
mc_longonly  = mc_portfolios(sim_rets, 2_000, shorts_ok=False)

#Plot Monte Carlo scatter
plt.figure(figsize=(10,5))

plt.subplot(1,2,1)
plt.scatter(mc_longshort[:,0], mc_longshort[:,1], s=8, alpha=0.6)
plt.title('Long + Short Allowed')
plt.xlabel('Risk (σ)')
plt.ylabel('Return (μ)')

plt.subplot(1,2,2)
plt.scatter(mc_longonly[:,0], mc_longonly[:,1], s=8, alpha=0.6, color='orange')
plt.title('Long‑Only')
plt.xlabel('Risk (σ)')
plt.ylabel('Return (μ)')

plt.tight_layout()
plt.show()

#Efficient frontier via QP
n_assets = len(tickers)
ones = np.ones(n_assets)
μ = μ_annual.values
Σ = Σ_annual.values

def min_variance(w, Σ):
    return w.dot(Σ).dot(w)

# constraints: sum(w)=1, μ⋅w = target
def get_efficient_frontier(μ, Σ, returns_grid):
    frontier = []
    bounds = [(None,None)]*n_assets  # allow shorts; change to (0,1) for long-only
    for target in returns_grid:
        cons = (
            {'type':'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type':'eq', 'fun': lambda w: w.dot(μ) - target}
        )
        # init w0
        w0 = np.repeat(1/n_assets, n_assets)
        sol = minimize(min_variance, w0, args=(Σ,), method='SLSQP',
                       bounds=bounds, constraints=cons)
        if sol.success:
            σ = np.sqrt(sol.fun)
            frontier.append((σ, target))
    return np.array(frontier)

# grid of returns between min and max asset returns
ret_min, ret_max = μ.min(), μ.max()
rets_grid = np.linspace(ret_min, ret_max, 50)
ef = get_efficient_frontier(μ, Σ, rets_grid)

#Overlay efficient frontier
plt.figure(figsize=(6,4))
plt.scatter(mc_longshort[:,0], mc_longshort[:,1], s=6, alpha=0.4, label='MC Long+Short')
plt.plot(ef[:,0], ef[:,1], 'r-', linewidth=2, label='Efficient Frontier')
plt.xlabel('Risk (σ)')
plt.ylabel('Return (μ)')
plt.legend()
plt.title('Monte Carlo + Efficient Frontier')
plt.show()
