from datetime import datetime, timedelta, timezone

from app.models.alert import Alert
from app.services.evaluator import evaluate_alert


def make_alert(**changes) -> Alert:
	alert_data = {
		"owner_id": 1,
		"symbol": "BTC",
		"condition": ">",
		"threshold": 100,
		"channel": "webhook",
		"channel_target": "http://example.com",
		"cooldown_seconds": 300,
		"state": "armed",
		"is_active": True,
		"last_triggered_at": None,
	}

	alert_data.update(changes)

	return Alert(**alert_data)


def test_alert_triggers_when_price_is_above_threshold():
	alert = make_alert()

	result = evaluate_alert(alert, current_price=101.0)

	assert result is True
	assert alert.state == "triggered"
	assert alert.last_triggered_at is not None


def test_alert_triggers_when_price_is_below_threshold():
	alert = make_alert(condition="<")

	result = evaluate_alert(alert, current_price=99.0)

	assert result is True
	assert alert.state == "triggered"


def test_triggered_alert_does_not_trigger_twice():
	alert = make_alert()

	assert evaluate_alert(alert, current_price=101.0) is True
	assert evaluate_alert(alert, current_price=102.0) is False
	assert alert.state == "triggered"


def test_triggered_alert_rearms_when_price_returns_below_threshold():
	alert = make_alert(
		state="triggered",
		last_triggered_at=datetime.now(timezone.utc),
	)

	result = evaluate_alert(alert, current_price=99.0)

	assert result is False
	assert alert.state == "armed"


def test_alert_does_not_trigger_during_cooldown():
	alert = make_alert(
		last_triggered_at=datetime.now(timezone.utc),
	)

	result = evaluate_alert(alert, current_price=101.0)

	assert result is False
	assert alert.state == "armed"


def test_alert_triggers_after_cooldown():
	alert = make_alert(
		last_triggered_at=datetime.now(timezone.utc) - timedelta(seconds=301),
	)

	result = evaluate_alert(alert, current_price=101.0)

	assert result is True
	assert alert.state == "triggered"
