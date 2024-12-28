import os
import time
from dotenv import load_dotenv
import schedule
from datadog.main import datadog
from milvus.main import milvus
from morningbrew import morningbrew

def fetch_datadog_events():
    datadog_client = datadog()
    datadog_events = datadog_client.main()
    milvus_client = milvus()
    milvus_client.insert(datadog_events, "datadog_alerts")
    print("Events fetched and inserted into Milvus")


def morning_brew():
    morningbrew()


def main():
    print("Starting...")

    # Load environment variables
    load_dotenv()
    print("Environment variables loaded")

    # Create collections if it does not exist
    milvus_client = milvus()
    milvus_client.create_collections()

    # Enable schedulers
    if os.getenv('ENABLE_DATADOG') == "True":
        print("Scheduler Datadog Alert Events enabled")
        schedule.every().day.at(os.getenv('SCHEDULER_DD_ALERT_EVENTS')).do(fetch_datadog_events)

    if os.getenv('ENABLE_MORNING_BREW') == "True":
        print("Scheduler Morning Brew enabled")
        schedule.every().day.at(os.getenv('SCHEDULER_MORNING_BREW')).do(morning_brew)

    print("Scheduler started")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
