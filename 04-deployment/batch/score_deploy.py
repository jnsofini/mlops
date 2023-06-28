from prefect.deployments import Deployment
from score import ride_duration_prediction
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=ride_duration_prediction,
    name="ride_duration_prediction",
    parameters={
        "taxi_type": "green",
        "run_id": "1dfce710dc824ecab012f7d910b190f6"
    },
    schedule=(CronSchedule(cron="0 3 2 * *", timezone="America/Chicago")),
    work_queue_name="ml"
)

deployment.apply()
