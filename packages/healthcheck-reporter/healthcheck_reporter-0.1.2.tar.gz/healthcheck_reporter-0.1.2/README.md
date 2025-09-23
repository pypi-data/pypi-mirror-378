# healthcheck-reporter

Lightweight health reporter that periodically probes database TCP connectivity and publishes a JSON report to MQTT.

## Installation

```bash
pip install healthcheck-reporter
```

## Usage

```python
from healthcheck_reporter import Reporter, ReporterConfig

config = ReporterConfig(
    database_host="db.example.local",
    database_port=5432,
    database_name="appdb",
    database_password="secret",
    database_user="app",
    mqtt_host="mqtt.example.local",
    mqtt_port=1883,
    mqtt_client_id="service-A-health",
    mqtt_topic="services/health",
    mqtt_user=None,      # or "user"
    mqtt_password=None,  # or "password"
)

reporter = Reporter(
    config,
    interval_seconds=30.0,  # configurable, non-blocking
)

reporter.start()

# ... your service runs ...

# On shutdown
reporter.stop()
```

### Published payload

```json
{
  "database_status": "ok",
  "mqtt_client_id": "service-A-health",
  "timestamp": "2025-01-01T00:00:00+00:00"
}
```

### Notes
- A real PostgreSQL connection is attempted first (psycopg2 is required); otherwise it falls back to a TCP probe if the driver is unavailable in the environment.
- MQTT publish uses QoS 1 and reconnects if needed.
- `start()` runs a background thread (non-blocking). Use `stop()` on shutdown.