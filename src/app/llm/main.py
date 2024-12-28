import os
from typing import List
from pydantic import BaseModel
from openai import OpenAI


class openai:
    def __init__(self):
        self.openai_client = OpenAI()

    def generate_summary_datadog_events(self, datadog_events):
        class DataDogAlertEvent(BaseModel):
            summary_alert_1: str
            summary_alert_2: str
            summary_alert_3: str
            summary_alert_4: str
            summary_alert_5: str

        question = ("""Provide a short summary of the most 5 alerts that have been triggered in the last 12 hours. 
        The importance of the alert is based on the priority P1 > P2 > P3 > P4 > P5. 
        If there are not enough alerts to fill the 5 slots, leave the remaining slots empty. Order the alerts based on priority.
        Include only the title of the alert.
        """
                    )

        context = "\n".join(datadog_events[i]["text"] for i in range(len(datadog_events)))

        system_prompt = """
        Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
        """

        user_prompt = f"""
        Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.
        <context>
        {context}
        </context>
        <question>
        {question}
        </question>
        """

        response = self.openai_client.beta.chat.completions.parse(
            model=os.getenv('OPENAI_MODEL_LLM'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=DataDogAlertEvent,
        )

        return response

    def generate_summary_aws_events(self, aws_events):
        class SummaryEvent(BaseModel):
            start_time: str
            end_time: str
            region: str
            affected_resources: str
            details: str

        class AWSEvent(BaseModel):
            summary_open_events: List[SummaryEvent]
            summary_upcoming: List[SummaryEvent]

        question = ("""Provide a summary of the of the open events and upcoming events from AWS.
        
        For the open events provided the top 5 events based on the oldest 'start_time'.
        
        For the upcoming events only provided those that starts within 3 months based on 'start_time'. 
        If there is not upcoming events in the next 3 months, leave the field empty.
        
        order the events based on the 'start_time' from oldest to newest.
        
        For both summaries provided the start time, region, affected resources and details of the event using the 
        response format"""
        )

        context = aws_events

        system_prompt = """
        Human: You are an AI assistant. You are able to find answers to the questions from the contextual passage snippets provided.
        """

        user_prompt = f"""
        Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.
        <context>
        {context}
        </context>
        <question>
        {question}
        </question>
        """

        response = self.openai_client.beta.chat.completions.parse(
            model=os.getenv('OPENAI_MODEL_LLM'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=AWSEvent,
        )

        return response
