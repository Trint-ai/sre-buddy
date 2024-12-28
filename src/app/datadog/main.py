import os
from tqdm import tqdm
from datetime import datetime, timedelta
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.events_api import EventsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from openai import OpenAI


def emb_text(text):
    openai_client = OpenAI()
    return (
        openai_client.embeddings.create(input=text, model=os.getenv('OPENAI_EMBEDDED_MODEL_LLM'))
        .data[0]
        .embedding
    )


class datadog:
    def __init__(self):
        self.start_time = int((datetime.now() - timedelta(hours=int(os.getenv('DD_LAST_EVENTS_HOUR')))).timestamp())
        self.end_time = int(datetime.now().timestamp())
        self.events = []
        self.events_parsed = []
        self.configuration = Configuration()

    def fetch_events(self):

        with ApiClient(self.configuration) as api_client:
            api_instance = EventsApi(api_client)
            try:
                response = api_instance.list_events(
                    start=self.start_time,
                    end=self.end_time,
                    sources="alert"
                )
                self.events = response.events

            except Exception as e:
                print(f"Error fetching events: {e}")
                return None

    def parse_events(self):
        if self.events:
            data = []
            for event in self.events:
                if str(event.alert_type) != "success":
                    date_happened_converted = datetime.fromtimestamp(event.date_happened).strftime('%Y-%m-%d %H:%M:%S')

                    text = f"""
title: {event.title}
alert_type: {event.alert_type}
alert_triggered_on: {date_happened_converted}
device_name: {event.device_name}
host: {event.host}
priority: {event.priority}
resource: {event.resource}
tags: {event.tags}
                    """
                    print(f'{text}\n')
                    data.append({"text": text, "title": event.title, "alert_type": event.alert_type,
                                 "alert_triggered_on": event.date_happened, "device_name": event.device_name,
                                 "host": event.host, "priority": event.priority, "resource": event.resource,
                                 "tags": event.tags})
                    print(
                        "----------------------------------------------------------------------------------------------")

            print(f'Total events: {len(data)}')

            for i, line in enumerate(tqdm(data, desc="Creating embeddings")):
                self.events_parsed.append({"text": str(line["text"]), "dense": emb_text(line["text"]), "title": str(line["title"]),
                                           "alert_triggered_on": int(line["alert_triggered_on"]),
                                           "device_name": str(line["device_name"]), "host": str(line["host"]),
                                           "priority": str(line["priority"]), "resource": str(line["resource"]),
                                           "tags": str(line["tags"])})

        else:
            print("No events found.")

    def ongoing_alerts(self):
        with ApiClient(self.configuration) as api_client:
            api_instance = MonitorsApi(api_client)
            response_warn = api_instance.search_monitors(query="status:warn")
            response_alert = api_instance.search_monitors(query="status:alert")

            return response_warn, response_alert



    def main(self):
        self.fetch_events()
        self.parse_events()
        return self.events_parsed
