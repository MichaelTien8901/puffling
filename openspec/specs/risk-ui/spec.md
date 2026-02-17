# risk-ui Specification

## Purpose
Frontend page for position sizing calculation and portfolio risk metrics analysis.

## Requirements

### Requirement: Risk page with position sizing calculator
The system SHALL provide a `/risk` page with a form to calculate position sizes using methods available from the backend (fixed, percent-risk, Kelly, volatility-based).

#### Scenario: Calculate position size with percent-risk method
- **WHEN** user selects method="percent_risk" and enters params (account_size, risk_pct, entry_price, stop_price)
- **THEN** system calls `POST /api/risk/position-size` and displays the recommended position size and dollar risk

#### Scenario: Switch sizing method
- **WHEN** user changes the method dropdown from "percent_risk" to "kelly"
- **THEN** form fields update to show Kelly-specific params (win_rate, avg_win, avg_loss)

### Requirement: Portfolio risk metrics panel
The system SHALL provide a panel on the Risk page to compute portfolio risk metrics for a set of symbols and weights over a date range.

#### Scenario: Compute portfolio risk
- **WHEN** user enters symbols (AAPL, GOOGL, MSFT), weights (0.4, 0.3, 0.3), and date range
- **THEN** system calls `POST /api/risk/portfolio` and displays VaR, max drawdown, Sharpe ratio, and annualized volatility

#### Scenario: Empty symbols validation
- **WHEN** user clicks compute with no symbols entered
- **THEN** form shows validation error and does not submit

### Requirement: Sidebar includes Risk link
The system SHALL add a "Risk" link to the sidebar navigation that navigates to the `/risk` page.

#### Scenario: Navigate to Risk page
- **WHEN** user clicks "Risk" in the sidebar
- **THEN** browser navigates to `/risk` and the link shows active state
