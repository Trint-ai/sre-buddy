import os
import ast
from datetime import datetime, timedelta
from milvus.main import milvus
from datadog.main import datadog
from llm.main import openai
from messaging.main import send_to_slack
from aws.main import aws

def morningbrew_datadog(slack_message):
    milvus_client = milvus()
    openai_client = openai()

    # Get Datadog alerts from the last 12 hours
    current_time = datetime.utcnow()
    time_12_hours_ago = current_time - timedelta(hours=12)
    epoch_12_hours_ago = int(time_12_hours_ago.timestamp())
    # expression = "alert_triggered_on > 1734939300 and title like '%P2%'"
    expression = f"alert_triggered_on >= {epoch_12_hours_ago}"
    result = milvus_client.query(1000, expression, "datadog_alerts")

    # Generate a summary of the alerts
    response = openai_client.generate_summary_datadog_events(result)
    response = response.choices[0].message.content
    datadog_events_summary = ast.literal_eval(response)

    # Get ongoing alerts from Datadog
    datadog_client = datadog()
    ongoing_alerts_warn, ongoing_alerts_alert = datadog_client.ongoing_alerts()

    past_alerts = ""

    for i in range(5):
        if datadog_events_summary[f'summary_alert_{i + 1}'] != "":
            past_alerts += f"""
    🔰 {datadog_events_summary[f'summary_alert_{i + 1}']}
                    """

    if past_alerts != "":
        slack_message += f"""
    Here is a summary of Datadog alerts from the last 12 hours:
                {past_alerts}
                """
    else:
        slack_message += f"""
    There were no Datadog alerts from the last 12 hours.
                """

    if ongoing_alerts_warn['metadata']['total_count'] > 0:
        slack_message += f"""
    There are currently {ongoing_alerts_warn['metadata']['total_count']} ongoing WARNING alerts:
                """
    for alert in ongoing_alerts_warn['monitors']:
        slack_message += f"""
    ⚠️ {alert['name']} <https://app.datadoghq.eu/monitors/{alert['id']}|More information>
                """

    if ongoing_alerts_alert['metadata']['total_count'] > 0:
        slack_message += f"""
    There are currently {ongoing_alerts_alert['metadata']['total_count']} ongoing ALERT alerts:
                """
    for alert in ongoing_alerts_alert['monitors']:
        slack_message += f"""
    🚨 {alert['name']} <https://app.datadoghq.eu/monitors/{alert['id']}|More information>
                """

    return slack_message


def morningbrew_aws_health(slack_message):
    openai_client = openai()
    aws_client = aws()
    aws_events = aws_client.main()

    # Generate a summary of the alerts
    response = openai_client.generate_summary_aws_events(aws_events)
    response = response.choices[0].message.content
    aws_events_summary = ast.literal_eval(response)

    slack_message += f"\n\n"

    if len(aws_events_summary['summary_open_events']) > 0:

        slack_message += f"""
☁️ Here is a summary of AWS Health OPEN events:
        """

        for event in aws_events_summary['summary_open_events']:
            slack_message += f"""

🔰 Region: {event['region']}
📅 Start time: {event['start_time']}
📅 End time: {event['end_time']}
📦 Affected Resources: {event['affected_resources']}
📄 Details: {event['details']}

            """

    if len(aws_events_summary['summary_upcoming']) > 0:
        slack_message += f"""
☁️ Here is a summary of AWS Health UPCOMING events:
        """

        for event in aws_events_summary['summary_upcoming']:
            slack_message += f"""
            
🔰 Region: {event['region']}
📅 Start time: {event['start_time']}
📅 End time: {event['end_time']}
📦 Affected Resources: {event['affected_resources']}
📄 Details: {event['details']}
            
            """
    return slack_message


def morningbrew():
    slack_message = "☕ Here is your morning Brew\n"

    # DATADOG ALERTS
    if os.getenv('ENABLE_DATADOG') == "True":
        slack_message = morningbrew_datadog(slack_message)

    # AWS HEALTH DASHBOARD
    if os.getenv('ENABLE_AWS') == "True":
        slack_message = morningbrew_aws_health(slack_message)

    if os.getenv('ENABLE_DATADOG') == "False" and os.getenv('ENABLE_AWS') == "False":
        slack_message += f"""
    There are no services enabled for the Morning Brew.
        """


    # Send the message to Slack
    print(slack_message)
    send_to_slack(slack_message)
