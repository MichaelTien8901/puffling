## ADDED Requirements

### Requirement: Volatility regime detection
The system SHALL compute a rolling volatility ratio (20-day realized vol / 60-day realized vol) and trigger a regime change event when the ratio crosses configurable thresholds.

#### Scenario: High volatility regime detected
- **WHEN** the 20-day/60-day volatility ratio exceeds 1.5
- **THEN** system fires a regime change event with type="high_volatility" and the current ratio value

#### Scenario: Low volatility regime detected
- **WHEN** the volatility ratio drops below 0.5
- **THEN** system fires a regime change event with type="low_volatility"

#### Scenario: Normal volatility
- **WHEN** the volatility ratio is between 0.5 and 1.5
- **THEN** no regime change event is fired

### Requirement: Trend regime detection
The system SHALL compute a normalized linear regression slope of 20-day close prices and trigger a regime change event when the trend direction changes (sign flip).

#### Scenario: Trend reversal detected
- **WHEN** the 20-day trend slope changes from positive to negative
- **THEN** system fires a regime change event with type="trend_reversal" and the new slope value

#### Scenario: Stable trend
- **WHEN** the slope sign remains the same as the previous check
- **THEN** no regime change event is fired

### Requirement: Regime-triggered re-optimization
The system SHALL trigger an on-demand re-optimization when a regime change event fires, subject to the cooldown period and kill-switch checks.

#### Scenario: Regime change triggers re-optimization
- **WHEN** a regime change event fires and cooldown has elapsed
- **THEN** system starts a re-optimization with trigger_type="regime" and logs the event

#### Scenario: Regime change during cooldown
- **WHEN** a regime change event fires but cooldown is active
- **THEN** system logs the regime change but skips re-optimization

### Requirement: Configurable detection thresholds
The system SHALL allow users to customize volatility ratio thresholds and trend detection window via the LiveAdaptationConfig.

#### Scenario: Custom volatility thresholds
- **WHEN** user sets vol_ratio_high=2.0 and vol_ratio_low=0.3
- **THEN** system uses those thresholds instead of defaults (1.5 and 0.5)
