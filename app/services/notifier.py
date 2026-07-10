from app.models.alert import Alert


async def send_notification(alert: Alert, price: float) -> None:
	print(
		f"[STUB] Alert {alert.id} triggered: "
		f"{alert.symbol} = {price}"
	)
