from __future__ import annotations

from datetime import datetime, timezone

from ..core.models import HealthReport


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_report(
    *,
    db_ok: bool,
    mqtt_client_id: str,
    db_error_count: int,
    db_attempt_count: int,
    mqtt_error_count: int,
    mqtt_attempt_count: int,
    api_error_count: int = 0,
    api_attempt_count: int = 0,
    debug_overall_status: str | None = None,
    uptime: float = 0.0,
) -> HealthReport:
    db_failure_rate: float = (db_error_count / db_attempt_count) * 100.0 if db_attempt_count > 0 else 0.0
    mqtt_failure_rate: float = (mqtt_error_count / mqtt_attempt_count) * 100.0 if mqtt_attempt_count > 0 else 0.0
    api_failure_rate: float = (api_error_count / api_attempt_count) * 100.0 if api_attempt_count > 0 else 0.0

    if debug_overall_status is not None:
        overall_status: str = debug_overall_status
    elif not db_ok:
        overall_status = "unavailable"
    elif db_failure_rate >= 20.0 or mqtt_failure_rate >= 20.0 or api_failure_rate >= 20.0:
        overall_status = "degraded"
    else:
        overall_status = "operational"

    return HealthReport(
        database_status="ok" if db_ok else "failed",
        mqtt_client_id=mqtt_client_id,
        timestamp=iso_utc_now(),
        db_error_count=db_error_count,
        mqtt_error_count=mqtt_error_count,
        db_failure_rate=round(db_failure_rate, 2),
        mqtt_failure_rate=round(mqtt_failure_rate, 2),
        overall_status=overall_status,
        api_error_count=api_error_count,
        api_failure_rate=round(api_failure_rate, 2),
        uptime=uptime,
    )


