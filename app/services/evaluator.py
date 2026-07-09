from datetime import datetime, timezone
from app.models.alert import Alert

def check_condition(condition: str, price: float, threshold: float) -> bool:
	if condition == ">":
		return price > threshold
	return price < threshold


def evaluate_alert(alert: Alert, current_price: float) -> bool:
	condition_met = check_condition(alert.condition, current_price, alert.threshold)

	if condition_met and alert.state == "armed":
		now = datetime.now(timezone.utc)
		if alert.last_triggered_at is not None:
			elapsed = (now - alert.last_triggered_at).total_seconds()
			if elapsed < alert.cooldown_seconds:
				return False
		
		alert.state = "triggered"
		alert.last_triggered_at = now
		return True
	
	if not condition_met and alert.state == "triggered":
		alert.state = "armed"

	return False