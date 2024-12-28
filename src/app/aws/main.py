import os
import boto3

class aws:
    def __init__(self):
        self.aws_open_events = []
        self.aws_upcoming_events = []
        self.aws_events = ""

    def describe_events(self):
        health_client = boto3.client('health', region_name='us-east-1')  # global region

        regions = os.getenv('AWS_REGIONS').split(',')

        try:
            # Describe events
            response = health_client.describe_events(
                filter={
                    'eventStatusCodes': ['open', 'upcoming'],
                    'regions': regions
                },
                maxResults=100
            )

            # # Filter out ACM-related events
            # events = [
            #     event for event in response.get('events', [])
            #     if event.get('service') != 'ACM'
            # ]


            # Output the events
            for event in response.get('events', []):
                details = self.get_event_details(event['arn'])
                affected_resources = self.get_affected_resources(event['arn'])

                # print(f"Event ARN: {event['arn']}")
                # print(f"Service: {event['service']}")
                # print(f"Event Type: {event['eventTypeCode']}")
                # print(f"Region: {event.get('region', 'N/A')}")
                # print(f"Start Time: {event.get('startTime', 'N/A')}")
                # print(f"End Time: {event.get('endTime', 'N/A')}")
                # print(f"Status: {event.get('statusCode', 'N/A')}")
                # print(f"Details: {details}")
                # print(f"Affected Resources: {affected_resources}")
                # print("-" * 40)

                if event.get('statusCode') == 'open':
                    self.aws_open_events.append({
                        'event_arn': event['arn'],
                        'service': event['service'],
                        'event_type': event['eventTypeCode'],
                        'region': event.get('region', 'N/A'),
                        'start_time': event.get('startTime', 'N/A'),
                        'end_time': event.get('endTime', 'N/A'),
                        'status': event.get('statusCode', 'N/A'),
                        'details': details,
                        'affected_resources': affected_resources
                    })

                elif event.get('statusCode') == 'upcoming':
                    self.aws_upcoming_events.append({
                        'event_arn': event['arn'],
                        'service': event['service'],
                        'event_type': event['eventTypeCode'],
                        'region': event.get('region', 'N/A'),
                        'start_time': event.get('startTime', 'N/A'),
                        'end_time': event.get('endTime', 'N/A'),
                        'status': event.get('statusCode', 'N/A'),
                        'details': details,
                        'affected_resources': affected_resources
                    })



        except Exception as e:
            print(f"An error occurred: {e}")


    def get_event_details(self, event_arn):
        # Initialize the AWS Health client
        health_client = boto3.client('health', region_name='us-east-1')  # Use a global region like us-east-1

        try:
            # Fetch event details
            response = health_client.describe_event_details(
                eventArns=[event_arn]  # Pass the ARN of the event
            )

            # Output the event details
            for event in response.get('successfulSet', []):
                details = {event.get('eventDescription', {}).get('latestDescription', 'No description available')}

                # print(f"Event ARN: {event['event']['arn']}")
                # print(f"Service: {event['event']['service']}")
                # print(f"Event Type: {event['event']['eventTypeCode']}")
                # print(f"Region: {event['event'].get('region', 'N/A')}")
                # print(f"Start Time: {event['event'].get('startTime', 'N/A')}")
                # print(f"End Time: {event['event'].get('endTime', 'N/A')}")
                # print(f"Status: {event['event'].get('statusCode', 'N/A')}")
                # print(
                #     f"Details: {event.get('eventDescription', {}).get('latestDescription', 'No description available')}")
                # print("-" * 40)
                return details

            # Handle any failed ARNs
            for failed_event in response.get('failedSet', []):
                print(f"Failed to retrieve details for Event ARN: {failed_event['arn']}")
                print(f"Error Message: {failed_event['errorMessage']}")

        except Exception as e:
            print(f"An error occurred: {e}")

    def get_affected_resources(self, event_arn):
        # Initialize the AWS Health client
        health_client = boto3.client('health', region_name='us-east-1')  # Use a global region like us-east-1

        try:
            # Fetch affected entities (resources)
            response = health_client.describe_affected_entities(
                filter={
                    'eventArns': [event_arn]
                }
            )

            # Output the affected entities
            entities = response.get('entities', [])
            if entities:
                affected_resources = []
                # print(f"Affected Resources for Event ARN: {event_arn}")
                for entity in entities:
                    # print(f"  - Entity ARN: {entity.get('entityArn', 'N/A')}")
                    # print(f"    Entity Value: {entity.get('entityValue', 'N/A')}")
                    # print(f"    Status: {entity.get('statusCode', 'N/A')}")
                    # print(f"    Last Updated: {entity.get('lastUpdatedTime', 'N/A')}")
                    # print("-" * 40)
                    affected_resources.append({entity.get('entityValue', 'N/A')})
                return affected_resources
            else:
                print(f"No affected resources found for Event ARN: {event_arn}")
                return []

        except Exception as e:
            print(f"An error occurred: {e}")

    def parse_events(self):
        print("Parsing AWS events...")
        self.aws_events = "Open Events: "

        for event in self.aws_open_events:
            self.aws_events += f"""

'start_time': {event['start_time']},
'end_time': {event['end_time']},
'region': {event['region']},
'affected_resources': {event['affected_resources']},
'details': {event['details']}

            """

        self.aws_events += "Upcoming Events: "

        for event in self.aws_upcoming_events:
            self.aws_events += f"""

'start_time': {event['start_time']},
'end_time': {event['end_time']},
'region': {event['region']},
'affected_resources': {event['affected_resources']},
'details': {event['details']}

            """



    def main(self):
        self.describe_events()
        self.parse_events()

        return self.aws_events
