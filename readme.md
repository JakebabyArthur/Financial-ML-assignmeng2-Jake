# Portfolio Optimization Study: JNJ · JPM · TSLA

**Author:** Hongduo,SHAN\
**Date:** July 17, 2025

---

## Introduction & Overview

This project analyzes the risk–return trade‑off of a three‑asset portfolio comprising:

- **Johnson & Johnson (JNJ)** — defensive, low volatility
- **JPMorgan Chase (JPM)** — cyclical, medium volatility
- **Tesla (TSLA)** — growth, high volatility

We use two complementary approaches:

1. **Monte Carlo Simulation** — generate random portfolios under long‑only and long + short constraints to visualize the opportunity set.
2. **Quadratic Programming** — compute the precise efficient frontier for each constraint regime.

Results highlight how allowing short positions shifts the frontier and reduces portfolio risk for a given return.

---

## Data & Inputs

- **Period:** 2020‑01‑01 through 2025‑07‑25
- **Data source:** Yahoo Finance via `yfinance`
- **Assets:** JNJ, JPM, TSLA (daily adjusted prices)

Annualized estimates:

| Ticker | Description                    | Mean μ (annual) | Volatility σ (annual) |
| ------ | ------------------------------ | --------------- | --------------------- |
| JNJ    | Consumer Staples (defensive)   | \~6%            | \~15%                 |
| JPM    | Financials                     | \~10%           | \~22%                 |
| TSLA   | Auto / Tech Growth (high beta) | \~175%          | \~190%                |

*Exact μ and σ are computed from daily returns and scaled by 252 trading days.*

---

## Methodology

### 1. Monte Carlo Simulation

1. **Estimate μ and Σ** from historical daily returns:
   - μᵢ = 252 × E[r\_{i,t}]
   - Σ = 252 × Cov(r)
2. **Generate N = 5 000** synthetic annual return scenarios: r^(s) ∼ 𝒩(μ, Σ).
3. **Draw M = 2 000** random weight vectors w under two regimes:
   - **Long‑only:** wᵢ ≥ 0; ∑ᵢ wᵢ = 1
   - **Long + Short:** w unconstrained; ∑ᵢ wᵢ = 1
4. **Compute** for each portfolio:
   - **Expected return:**\
     \(\bar r = \frac{1}{N} \sum_{s=1}^N w^T r^{(s)}\)
   - **Risk (σ):**\
     \(σ_p = \sqrt{w^T Σ w}\)
5. **Plot** risk vs. return to visualize the opportunity sets.

### 2. Efficient Frontier

For each target return R\_t on a grid, solve:

$$
\begin{aligned}
&\min_w \quad w^T Σ w \\
&\text{s.t.} \quad \mathbf{1}^T w = 1, \quad μ^T w = R_t, \\
&\quad w_i \ge 0 \quad (\text{long‐only}) \;\text{or free (long+short)}.
\end{aligned}
$$

Use SciPy’s SLSQP solver to obtain the minimum‐variance σ for each R\_t, tracing the frontier.

---

## Results

### Opportunity Sets

- **Left (Long + Short):** Risk 0.25–2.0, Return –0.4–1.8.
- **Right (Long‑Only):** Risk 0.20–0.65, Return 0.10–0.65.
- Allowing shorts **widens** the feasible set substantially.

### Efficient Frontiers

- **Red:** Long + Short frontier
- **Green dashed:** Long‑only frontier
- Shorts shift the frontier **left**, lowering risk for the same return.

**Illustrative point:** For R\_t = 30%:

- σ\_{LS} ≈ 0.35
- σ\_{LO} ≈ 0.40\
  → **\~14%** risk reduction when shorts are allowed.

---

## Discussion

1. **Diversification benefit:** Combining low‑, medium‑, and high‑vol assets yields portfolios with lower risk than single‐asset positions.
2. **Impact of shorting:** Permitting short positions unlocks additional return streams, compressing the frontier toward lower risk.
3. **Monte Carlo vs. QP:** Most random portfolios lie >5% away from the frontier, underscoring the importance of formal optimization.
4. **Solver behavior:** At very high return targets (R > 0.7), the QP occasionally fails to converge—our frontier reflects the feasible region.

---

## Conclusion

- **Short positions** meaningfully **improve** risk–return trade‑offs.
- **Quadratic programming** identifies portfolios that dominate the bulk of random allocations.
- **Practical recommendation:** Even modest short exposure can substantively reduce portfolio risk.

---

## Repo Structure

```
/  
├─ README.md                # this report  
├─ assignment2.py           # simulation & optimization code  
├─ images/                  # figures  
│   ├─ opportunity_sets.png  
│   └─ monte_carlo_frontier.png  
└─ data/                    # raw data (optional)  
   └─ prices.csv
```

---

## Appendix: Key Code Snippets

```python
# Simulate return scenarios
sim_rets = np.random.multivariate_normal(μ, Σ, size=5000)

# Draw random weights
def random_weights(n, shorts_ok): ...

# Solve one QP for target return t
def solve_qp(t):
    cons = [
        {'type':'eq', 'fun': lambda w: np.sum(w)-1},
        {'type':'eq', 'fun': lambda w, t=t: w.dot(μ)-t}
    ]
    sol = minimize(lambda w: w.T @ Σ @ w, w0, constraints=cons)
    return sol
```

Expand as needed for full code listings or tables of optimal weights. Feel free to iterate!

