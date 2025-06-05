# Flask-Limiter Rate Limiting Strategy Fix

## Issue Summary

The BDC backend was experiencing a configuration error with Flask-Limiter rate limiting due to an invalid strategy name. The application was configured to use `"sliding-window"` strategy, but this is not a valid strategy name in Flask-Limiter 3.5.0.

## Root Cause

Flask-Limiter 3.5.0 uses the `limits` library for rate limiting strategies. The available strategies are:
- `"sliding-window-counter"` ✓ (was incorrectly configured as `"sliding-window"`)
- `"fixed-window"` ✓
- `"moving-window"` ✓

The configuration was using `"sliding-window"` which is not a valid strategy name, causing a `ConfigurationError` when initializing Flask-Limiter.

## Files Modified

The following configuration files were updated to use the correct strategy name:

### 1. `/server/config.py`
**Line 124:** Changed from `"sliding-window"` to `"sliding-window-counter"`
```python
# Before
RATELIMIT_STRATEGY = "sliding-window"

# After  
RATELIMIT_STRATEGY = "sliding-window-counter"
```

### 2. `/server/app_config/production_security.py`
**Line 83:** Changed from `"sliding-window"` to `"sliding-window-counter"`
```python
# Before
RATELIMIT_STRATEGY = "sliding-window"

# After
RATELIMIT_STRATEGY = "sliding-window-counter"
```

### 3. `/server/app_config/production.py`
**Line 50:** Updated environment variable default
```python
# Before
RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'sliding-window')

# After
RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'sliding-window-counter')
```

### 4. `/server/k8s/configmap.yaml`
**Line 16:** Updated Kubernetes configuration
```yaml
# Before
RATELIMIT_STRATEGY: "sliding-window"

# After
RATELIMIT_STRATEGY: "sliding-window-counter"
```

## Verification

A test script was created (`/server/test_rate_limiting_fix.py`) to verify:

1. ✅ Flask-Limiter can be initialized with `"sliding-window-counter"` strategy
2. ✅ All available strategies are correctly identified
3. ✅ All configuration files contain the correct strategy name
4. ✅ No references to the invalid `"sliding-window"` strategy remain

## Strategy Behavior

The `sliding-window-counter` strategy provides:
- **Sliding Window**: Rate limits are calculated using a sliding time window rather than fixed intervals
- **Counter-based**: Uses counters to track request counts within time windows
- **Redis Support**: Works efficiently with Redis storage for distributed systems
- **Precise Limiting**: More accurate than fixed-window for burst protection

## Deployment Impact

This fix resolves the Flask-Limiter initialization error and enables proper rate limiting functionality:

- **Before**: Flask-Limiter would fail to initialize, causing application startup errors
- **After**: Rate limiting works correctly with sliding window behavior for better protection

## Environment Variables

If using environment variables to override the strategy, ensure they use the correct value:
```bash
export RATELIMIT_STRATEGY="sliding-window-counter"
```

## Testing

Run the verification script to confirm the fix:
```bash
cd /server
python test_rate_limiting_fix.py
```

All tests should pass, confirming that:
- Flask-Limiter can initialize correctly
- The strategy is properly configured
- All configuration files are updated
- No invalid strategy references remain

## Additional Notes

- The fix maintains the same sliding window behavior that was intended
- No changes to rate limiting logic or performance
- Backward compatible with existing rate limit configurations
- The invalid strategy name was the only issue preventing proper functionality

This fix ensures robust rate limiting protection for the BDC application using the correct Flask-Limiter strategy configuration.