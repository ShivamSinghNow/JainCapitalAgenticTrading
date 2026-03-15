"""
Data Validation Utilities - Ensure Data Quality and Reliability

This module provides data validation, cross-source verification, and
anomaly detection to ensure high-quality data reaches the trading agents.

All functions are FREE - just code logic, no external services required.
"""

from typing import Annotated, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ===== PRICE DATA VALIDATION =====

def validate_price_data(
    data: pd.DataFrame,
    symbol: str,
    date_column: str = 'Date',
    price_columns: List[str] = None,
) -> Tuple[bool, List[str]]:
    """
    Validate price data for anomalies and data quality issues.

    Checks performed:
    - Missing values
    - Negative prices
    - Zero prices
    - Extreme price jumps (>50% in single period)
    - OHLC relationship validity (High >= Low, Close between High/Low)
    - Chronological date order
    - Duplicate dates

    Args:
        data: DataFrame with price data
        symbol: Symbol being validated (for logging)
        date_column: Name of date column
        price_columns: List of price columns to validate (default: ['Open', 'High', 'Low', 'Close'])

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    if price_columns is None:
        price_columns = ['Open', 'High', 'Low', 'Close']

    issues = []

    # Check if DataFrame is empty
    if data.empty:
        issues.append(f"{symbol}: DataFrame is empty")
        return False, issues

    # Check for missing columns
    missing_cols = [col for col in price_columns if col not in data.columns]
    if missing_cols:
        issues.append(f"{symbol}: Missing columns: {missing_cols}")

    # Check for missing values
    for col in price_columns:
        if col in data.columns:
            missing_count = data[col].isna().sum()
            if missing_count > 0:
                issues.append(f"{symbol}: {missing_count} missing values in {col}")

    # Check for negative prices
    for col in price_columns:
        if col in data.columns:
            negative_count = (data[col] < 0).sum()
            if negative_count > 0:
                issues.append(f"{symbol}: {negative_count} negative values in {col}")

    # Check for zero prices
    for col in price_columns:
        if col in data.columns:
            zero_count = (data[col] == 0).sum()
            if zero_count > 0:
                issues.append(f"{symbol}: {zero_count} zero values in {col}")

    # Check OHLC relationships
    if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
        # High should be >= Low
        invalid_hl = (data['High'] < data['Low']).sum()
        if invalid_hl > 0:
            issues.append(f"{symbol}: {invalid_hl} records where High < Low")

        # Close should be between High and Low
        invalid_close = ((data['Close'] > data['High']) | (data['Close'] < data['Low'])).sum()
        if invalid_close > 0:
            issues.append(f"{symbol}: {invalid_close} records where Close outside High/Low range")

        # Open should be between High and Low
        invalid_open = ((data['Open'] > data['High']) | (data['Open'] < data['Low'])).sum()
        if invalid_open > 0:
            issues.append(f"{symbol}: {invalid_open} records where Open outside High/Low range")

    # Check for extreme price jumps (>50% in single period)
    if 'Close' in data.columns and len(data) > 1:
        price_changes = data['Close'].pct_change().abs()
        extreme_jumps = (price_changes > 0.5).sum()
        if extreme_jumps > 0:
            issues.append(f"{symbol}: {extreme_jumps} periods with >50% price change (potential data error)")

    # Check date order if date column exists
    if date_column in data.columns:
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
            try:
                dates = pd.to_datetime(data[date_column])
            except Exception as e:
                issues.append(f"{symbol}: Cannot parse dates in {date_column}: {str(e)}")
                dates = None
        else:
            dates = data[date_column]

        if dates is not None:
            # Check chronological order
            if not dates.is_monotonic_increasing:
                issues.append(f"{symbol}: Dates are not in chronological order")

            # Check for duplicate dates
            duplicate_dates = dates.duplicated().sum()
            if duplicate_dates > 0:
                issues.append(f"{symbol}: {duplicate_dates} duplicate dates found")

    is_valid = len(issues) == 0

    return is_valid, issues


def detect_price_anomalies(
    data: pd.DataFrame,
    symbol: str,
    price_column: str = 'Close',
    std_threshold: float = 3.0,
) -> Dict:
    """
    Detect statistical anomalies in price data using z-score method.

    Args:
        data: DataFrame with price data
        symbol: Symbol being analyzed
        price_column: Column to analyze for anomalies
        std_threshold: Number of standard deviations for anomaly detection

    Returns:
        Dictionary with anomaly detection results
    """
    if price_column not in data.columns or len(data) < 10:
        return {
            'symbol': symbol,
            'anomalies_found': False,
            'anomaly_count': 0,
            'message': 'Insufficient data for anomaly detection'
        }

    # Calculate returns
    returns = data[price_column].pct_change().dropna()

    # Calculate z-scores
    mean_return = returns.mean()
    std_return = returns.std()

    if std_return == 0:
        return {
            'symbol': symbol,
            'anomalies_found': False,
            'anomaly_count': 0,
            'message': 'No variance in returns'
        }

    z_scores = np.abs((returns - mean_return) / std_return)

    # Find anomalies
    anomalies = z_scores > std_threshold
    anomaly_count = anomalies.sum()

    anomaly_indices = data.index[1:][anomalies]  # +1 because pct_change shifts
    anomaly_values = []

    for idx in anomaly_indices[:10]:  # Limit to first 10
        if idx < len(data):
            anomaly_values.append({
                'date': str(data.loc[idx, 'Date']) if 'Date' in data.columns else str(idx),
                'price': float(data.loc[idx, price_column]),
                'return': float(returns.loc[idx]),
                'z_score': float(z_scores.loc[idx]),
            })

    return {
        'symbol': symbol,
        'anomalies_found': anomaly_count > 0,
        'anomaly_count': int(anomaly_count),
        'anomaly_percentage': float(anomaly_count / len(returns) * 100),
        'anomalies': anomaly_values,
        'mean_return': float(mean_return),
        'std_return': float(std_return),
    }


# ===== CROSS-SOURCE VALIDATION =====

def cross_validate_prices(
    price1: float,
    price2: float,
    source1: str,
    source2: str,
    symbol: str,
    max_diff_pct: float = 5.0,
) -> Tuple[bool, Optional[str]]:
    """
    Cross-validate prices from two different sources.

    Args:
        price1: Price from source 1
        price2: Price from source 2
        source1: Name of source 1 (e.g., 'YFinance')
        source2: Name of source 2 (e.g., 'Binance')
        symbol: Trading symbol
        max_diff_pct: Maximum allowed percentage difference

    Returns:
        Tuple of (is_valid, warning_message)
    """
    if price1 <= 0 or price2 <= 0:
        return False, f"{symbol}: Invalid price data (negative or zero)"

    diff_pct = abs(price1 - price2) / price1 * 100

    if diff_pct > max_diff_pct:
        warning = f"{symbol}: Price discrepancy detected! {source1}=${price1:,.2f} vs {source2}=${price2:,.2f} ({diff_pct:.2f}% difference)"
        return False, warning

    return True, None


def cross_validate_volumes(
    volume1: float,
    volume2: float,
    source1: str,
    source2: str,
    symbol: str,
    max_diff_pct: float = 20.0,
) -> Tuple[bool, Optional[str]]:
    """
    Cross-validate trading volumes from two different sources.

    Volume differences are expected to be larger than price differences
    since different exchanges have different volumes.

    Args:
        volume1: Volume from source 1
        volume2: Volume from source 2
        source1: Name of source 1
        source2: Name of source 2
        symbol: Trading symbol
        max_diff_pct: Maximum allowed percentage difference

    Returns:
        Tuple of (is_valid, warning_message)
    """
    if volume1 <= 0 and volume2 <= 0:
        return True, None  # Both zero is acceptable

    if volume1 <= 0 or volume2 <= 0:
        warning = f"{symbol}: Volume discrepancy - {source1}={volume1:,.0f}, {source2}={volume2:,.0f}"
        return False, warning

    diff_pct = abs(volume1 - volume2) / max(volume1, volume2) * 100

    if diff_pct > max_diff_pct:
        warning = f"{symbol}: Volume discrepancy - {source1}={volume1:,.0f} vs {source2}={volume2:,.0f} ({diff_pct:.1f}% difference)"
        return False, warning

    return True, None


# ===== DATA FRESHNESS VALIDATION =====

def check_data_freshness(
    timestamp: datetime,
    symbol: str,
    max_age_minutes: int = 60,
) -> Tuple[bool, Optional[str]]:
    """
    Check if data is fresh enough for trading decisions.

    Args:
        timestamp: Timestamp of the data
        symbol: Trading symbol
        max_age_minutes: Maximum allowed age in minutes

    Returns:
        Tuple of (is_fresh, warning_message)
    """
    now = datetime.now()

    # Handle timezone-aware timestamps
    if timestamp.tzinfo is not None:
        if now.tzinfo is None:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)

    age = now - timestamp
    age_minutes = age.total_seconds() / 60

    if age_minutes > max_age_minutes:
        warning = f"{symbol}: Stale data detected - Last update {age_minutes:.1f} minutes ago (max allowed: {max_age_minutes})"
        return False, warning

    return True, None


def validate_timestamp_format(
    timestamp_str: str,
    symbol: str,
    expected_format: str = "%Y-%m-%d",
) -> Tuple[bool, Optional[datetime], Optional[str]]:
    """
    Validate timestamp string format.

    Args:
        timestamp_str: Timestamp string to validate
        symbol: Trading symbol
        expected_format: Expected datetime format

    Returns:
        Tuple of (is_valid, parsed_datetime, error_message)
    """
    try:
        dt = datetime.strptime(timestamp_str, expected_format)
        return True, dt, None
    except ValueError as e:
        error = f"{symbol}: Invalid timestamp format '{timestamp_str}'. Expected {expected_format}. Error: {str(e)}"
        return False, None, error


# ===== COMPLETENESS VALIDATION =====

def check_data_completeness(
    data: pd.DataFrame,
    symbol: str,
    required_columns: List[str],
    min_rows: int = 1,
) -> Tuple[bool, List[str]]:
    """
    Check if dataset is complete and has required columns/rows.

    Args:
        data: DataFrame to validate
        symbol: Trading symbol
        required_columns: List of required column names
        min_rows: Minimum number of rows required

    Returns:
        Tuple of (is_complete, list_of_issues)
    """
    issues = []

    if data.empty:
        issues.append(f"{symbol}: Dataset is empty")
        return False, issues

    if len(data) < min_rows:
        issues.append(f"{symbol}: Insufficient rows. Got {len(data)}, need at least {min_rows}")

    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        issues.append(f"{symbol}: Missing required columns: {missing_cols}")

    is_complete = len(issues) == 0

    return is_complete, issues


# ===== RANGE VALIDATION =====

def validate_value_range(
    value: float,
    symbol: str,
    field_name: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate that a value is within expected range.

    Args:
        value: Value to validate
        symbol: Trading symbol
        field_name: Name of the field
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if min_value is not None and value < min_value:
        error = f"{symbol}: {field_name}={value} is below minimum allowed value {min_value}"
        return False, error

    if max_value is not None and value > max_value:
        error = f"{symbol}: {field_name}={value} exceeds maximum allowed value {max_value}"
        return False, error

    return True, None


# ===== SUMMARY VALIDATION REPORT =====

def generate_validation_report(
    data: pd.DataFrame,
    symbol: str,
    source: str,
) -> str:
    """
    Generate a comprehensive validation report for a dataset.

    Args:
        data: DataFrame to validate
        symbol: Trading symbol
        source: Data source name

    Returns:
        Formatted validation report string
    """
    report = f"## Data Validation Report for {symbol} ({source})\n\n"

    # Basic info
    report += f"**Records**: {len(data)}\n"
    report += f"**Columns**: {', '.join(data.columns.tolist())}\n\n"

    # Completeness check
    is_complete, completeness_issues = check_data_completeness(
        data, symbol, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], min_rows=1
    )

    if is_complete:
        report += "✅ **Completeness**: PASSED\n"
    else:
        report += "❌ **Completeness**: FAILED\n"
        for issue in completeness_issues:
            report += f"  - {issue}\n"

    # Price validation
    is_valid, price_issues = validate_price_data(data, symbol)

    if is_valid:
        report += "✅ **Price Data**: VALID\n"
    else:
        report += "❌ **Price Data**: INVALID\n"
        for issue in price_issues:
            report += f"  - {issue}\n"

    # Anomaly detection
    if 'Close' in data.columns and len(data) >= 10:
        anomaly_results = detect_price_anomalies(data, symbol)

        if not anomaly_results['anomalies_found']:
            report += "✅ **Anomalies**: None detected\n"
        else:
            report += f"⚠️  **Anomalies**: {anomaly_results['anomaly_count']} detected ({anomaly_results['anomaly_percentage']:.1f}%)\n"
            for anomaly in anomaly_results.get('anomalies', [])[:3]:
                report += f"  - {anomaly['date']}: {anomaly['return']*100:.1f}% return (z-score: {anomaly['z_score']:.2f})\n"

    report += "\n**Validation Complete**\n"

    return report
