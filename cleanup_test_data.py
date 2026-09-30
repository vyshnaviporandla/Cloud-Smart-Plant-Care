from backend.app import app, db, WateringEvent, Alert

with app.app_context():
    deleted_events = WateringEvent.query.delete()
    deleted_alerts = Alert.query.delete()

    db.session.commit()

    print(f"Deleted watering events: {deleted_events}")
    print(f"Deleted alerts: {deleted_alerts}")
    print("Old test data cleaned successfully.")