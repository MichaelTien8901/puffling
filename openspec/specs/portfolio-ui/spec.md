# portfolio-ui Specification

## Purpose
Frontend page for portfolio weight optimization, performance tearsheet generation, and factor analysis.

## Requirements

### Requirement: Portfolio optimization panel
The system SHALL provide a `/portfolio` page with a form to run mean-variance portfolio optimization for a set of symbols over a date range.

#### Scenario: Run portfolio optimization
- **WHEN** user enters symbols (AAPL, GOOGL, MSFT, AMZN), date range, and method="mean_variance"
- **THEN** system calls `POST /api/portfolio/optimize` and displays optimal weights as a table with symbol and weight columns

#### Scenario: Optimization error handling
- **WHEN** the optimization API returns an error (e.g., insufficient data)
- **THEN** the page displays the error message without crashing

### Requirement: Performance tearsheet panel
The system SHALL provide a panel on the Portfolio page to generate a performance tearsheet from a set of returns.

#### Scenario: Generate tearsheet
- **WHEN** user enters or uploads a series of returns and clicks "Generate"
- **THEN** system calls `POST /api/portfolio/tearsheet` and displays metrics as key-value cards (total return, CAGR, Sharpe, max drawdown, etc.)

### Requirement: Factor analysis panel
The system SHALL provide a panel on the Portfolio page to compute factors for a symbol set and view PCA risk factors.

#### Scenario: Compute factors
- **WHEN** user enters symbols and date range and clicks "Compute Factors"
- **THEN** system calls `POST /api/factors/compute` and displays factor values in a table

#### Scenario: PCA risk factors
- **WHEN** user enters symbols, date range, n_components=5, and clicks "Risk Factors"
- **THEN** system calls `POST /api/factors/risk-factors` and displays principal components ranked by explained variance

### Requirement: Sidebar includes Portfolio link
The system SHALL add a "Portfolio" link to the sidebar navigation that navigates to the `/portfolio` page.

#### Scenario: Navigate to Portfolio page
- **WHEN** user clicks "Portfolio" in the sidebar
- **THEN** browser navigates to `/portfolio` and the link shows active state
