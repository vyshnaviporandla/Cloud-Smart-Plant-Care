from backend.app import app, db, WateringEvent, Alert

with app.app_context():
    old_events = WateringEvent.query.filter(
        (WateringEvent.moisture_before == 0.0) |
        (WateringEvent.moisture_after == 0.0)
    ).all()

    deleted_events = len(old_events)

    for event in old_events:
        db.session.delete(event)

    old_alerts = Alert.query.filter(
        Alert.message.like("%0.0%")
    ).all()

    deleted_alerts = len(old_alerts)

    for alert in old_alerts:
        db.session.delete(alert)

    db.session.commit()

    print(f"Deleted incorrect watering events: {deleted_events}")
    print(f"Deleted incorrect alerts: {deleted_alerts}")
    print("Cleanup completed successfully.")