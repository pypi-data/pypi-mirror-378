#
# Copyright (c) 2024, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import os
import sys
from pathlib import Path
from typing import List, TypedDict

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.aws.llm import AWSBedrockLLMService
from pipecat.services.aws.stt import AWSTranscribeSTTService
from pipecat.services.aws.tts import AWSPollyTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.utils.text.markdown_text_filter import MarkdownTextFilter

from pipecat_flows import (
    ContextStrategy,
    ContextStrategyConfig,
    FlowArgs,
    FlowConfig,
    FlowManager,
    FlowResult,
    FlowsFunctionSchema,
)

sys.path.append(str(Path(__file__).parent.parent))
from runner import configure

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


# Type definitions
class Prescription(TypedDict):
    medication: str
    dosage: str


class Allergy(TypedDict):
    name: str


class Condition(TypedDict):
    name: str


class VisitReason(TypedDict):
    name: str


# Result types for each handler
class BirthdayVerificationResult(FlowResult):
    verified: bool


class PrescriptionRecordResult(FlowResult):
    count: int


class AllergyRecordResult(FlowResult):
    count: int


class ConditionRecordResult(FlowResult):
    count: int


class VisitReasonRecordResult(FlowResult):
    count: int


# Function handlers
async def verify_birthday(args: FlowArgs) -> tuple[BirthdayVerificationResult, str]:
    """Handler for birthday verification."""
    birthday = args["birthday"]
    # In a real app, this would verify against patient records
    is_valid = birthday == "1983-01-01"
    return BirthdayVerificationResult(verified=is_valid), "get_prescriptions"


async def record_prescriptions(args: FlowArgs) -> tuple[PrescriptionRecordResult, str]:
    """Handler for recording prescriptions."""
    prescriptions: List[Prescription] = args["prescriptions"]
    # In a real app, this would store in patient records
    return PrescriptionRecordResult(count=len(prescriptions)), "get_allergies"


async def record_allergies(args: FlowArgs) -> tuple[AllergyRecordResult, str]:
    """Handler for recording allergies."""
    allergies: List[Allergy] = args["allergies"]
    # In a real app, this would store in patient records
    return AllergyRecordResult(count=len(allergies)), "get_conditions"


async def record_conditions(args: FlowArgs) -> tuple[ConditionRecordResult, str]:
    """Handler for recording medical conditions."""
    conditions: List[Condition] = args["conditions"]
    # In a real app, this would store in patient records
    return ConditionRecordResult(count=len(conditions)), "get_visit_reasons"


async def record_visit_reasons(args: FlowArgs) -> tuple[VisitReasonRecordResult, str]:
    """Handler for recording visit reasons."""
    visit_reasons: List[VisitReason] = args["visit_reasons"]
    # In a real app, this would store in patient records
    return VisitReasonRecordResult(count=len(visit_reasons)), "verify"


async def revise_information(args: FlowArgs) -> tuple[None, str]:
    """Handler to restart the information-gathering process."""
    return None, "get_prescriptions"


async def confirm_information(args: FlowArgs) -> tuple[None, str]:
    """Handler to confirm all collected information."""
    return None, "confirm"


async def complete_intake(args: FlowArgs) -> tuple[None, str]:
    """Handler to complete the intake process."""
    return None, "end"


# Define the flow configuration with FlowsFunctionSchema
flow_config: FlowConfig = {
    "initial_node": "start",
    "nodes": {
        "start": {
            "role_messages": [
                {
                    "role": "system",
                    "content": "You are Jessica, an agent for Tri-County Health Services. You must ALWAYS use one of the available functions to progress the conversation. Be professional but friendly.",
                }
            ],
            "task_messages": [
                {
                    "role": "user",
                    "content": "Start by introducing yourself to Chad Bailey, then ask for their date of birth, including the year. Once they provide their birthday, use verify_birthday to check it. If verified (1983-01-01), proceed to prescriptions.",
                }
            ],
            "functions": [
                FlowsFunctionSchema(
                    name="verify_birthday",
                    description="Verify the user has provided their correct birthday. Once confirmed, the next step is to recording the user's prescriptions.",
                    properties={
                        "birthday": {
                            "type": "string",
                            "description": "The user's birthdate (convert to YYYY-MM-DD format)",
                        }
                    },
                    required=["birthday"],
                    handler=verify_birthday,
                )
            ],
        },
        "get_prescriptions": {
            "task_messages": [
                {
                    "role": "user",
                    "content": "This step is for collecting prescriptions. Ask them what prescriptions they're taking, including the dosage. After recording prescriptions (or confirming none), proceed to allergies.",
                }
            ],
            "context_strategy": ContextStrategyConfig(strategy=ContextStrategy.RESET),
            "functions": [
                FlowsFunctionSchema(
                    name="record_prescriptions",
                    description="Record the user's prescriptions. Once confirmed, the next step is to collect allergy information.",
                    properties={
                        "prescriptions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "medication": {
                                        "type": "string",
                                        "description": "The medication's name",
                                    },
                                    "dosage": {
                                        "type": "string",
                                        "description": "The prescription's dosage",
                                    },
                                },
                                "required": ["medication", "dosage"],
                            },
                        }
                    },
                    required=["prescriptions"],
                    handler=record_prescriptions,
                )
            ],
        },
        "get_allergies": {
            "task_messages": [
                {
                    "role": "user",
                    "content": "Collect allergy information. Ask about any allergies they have. After recording allergies (or confirming none), proceed to medical conditions.",
                }
            ],
            "functions": [
                FlowsFunctionSchema(
                    name="record_allergies",
                    description="Record the user's allergies. Once confirmed, then next step is to collect medical conditions.",
                    properties={
                        "allergies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "What the user is allergic to",
                                    },
                                },
                                "required": ["name"],
                            },
                        }
                    },
                    required=["allergies"],
                    handler=record_allergies,
                )
            ],
        },
        "get_conditions": {
            "task_messages": [
                {
                    "role": "user",
                    "content": "Collect medical condition information. Ask about any medical conditions they have. After recording conditions (or confirming none), proceed to visit reasons.",
                }
            ],
            "functions": [
                FlowsFunctionSchema(
                    name="record_conditions",
                    description="Record the user's medical conditions. Once confirmed, the next step is to collect visit reasons.",
                    properties={
                        "conditions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "The user's medical condition",
                                    },
                                },
                                "required": ["name"],
                            },
                        }
                    },
                    required=["conditions"],
                    handler=record_conditions,
                )
            ],
        },
        "get_visit_reasons": {
            "task_messages": [
                {
                    "role": "user",
                    "content": "Collect information about the reason for their visit. Ask what brings them to the doctor today. After recording their reasons, proceed to verification.",
                }
            ],
            "functions": [
                FlowsFunctionSchema(
                    name="record_visit_reasons",
                    description="Record the reasons for their visit. Once confirmed, the next step is to verify all information.",
                    properties={
                        "visit_reasons": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "The user's reason for visiting",
                                    },
                                },
                                "required": ["name"],
                            },
                        }
                    },
                    required=["visit_reasons"],
                    handler=record_visit_reasons,
                )
            ],
        },
        "verify": {
            "task_messages": [
                {
                    "role": "user",
                    "content": """Review all collected information with the patient. Follow these steps:
1. Summarize their prescriptions, allergies, conditions, and visit reasons
2. Ask if everything is correct
3. Use the appropriate function based on their response

Be thorough in reviewing all details and wait for explicit confirmation.""",
                }
            ],
            "context_strategy": ContextStrategyConfig(
                strategy=ContextStrategy.RESET_WITH_SUMMARY,
                summary_prompt=(
                    "Summarize the patient intake conversation, including their birthday, "
                    "prescriptions, allergies, medical conditions, and reasons for visiting. "
                    "Focus on the specific medical information provided."
                ),
            ),
            "functions": [
                FlowsFunctionSchema(
                    name="revise_information",
                    description="Return to prescriptions to revise information",
                    properties={},
                    required=[],
                    handler=revise_information,
                ),
                FlowsFunctionSchema(
                    name="confirm_information",
                    description="Proceed with confirmed information",
                    properties={},
                    required=[],
                    handler=confirm_information,
                ),
            ],
        },
        "confirm": {
            "task_messages": [
                {
                    "role": "user",
                    "content": "Once confirmed, thank them, then use the complete_intake function to end the conversation.",
                }
            ],
            "functions": [
                FlowsFunctionSchema(
                    name="complete_intake",
                    description="Complete the intake process",
                    properties={},
                    required=[],
                    handler=complete_intake,
                )
            ],
        },
        "end": {
            "task_messages": [
                {"role": "user", "content": "Thank them for their time and end the conversation."}
            ],
            "post_actions": [{"type": "end_conversation"}],
        },
    },
}


async def main():
    """Main function to set up and run the patient intake bot."""
    async with aiohttp.ClientSession() as session:
        (room_url, _) = await configure(session)

        transport = DailyTransport(
            room_url,
            None,
            "Patient Intake Bot",
            DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )

        stt = AWSTranscribeSTTService()
        tts = AWSPollyTTSService(
            region="us-west-2",
            voice_id="Joanna",
            text_filter=MarkdownTextFilter(),
            params=AWSPollyTTSService.InputParams(engine="generative", rate="1.1"),
        )
        llm = AWSBedrockLLMService(
            aws_region="us-west-2",
            model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            params=AWSBedrockLLMService.InputParams(temperature=0.8, latency="optimized"),
        )

        context = OpenAILLMContext()
        context_aggregator = llm.create_context_aggregator(context)

        pipeline = Pipeline(
            [
                transport.input(),  # Transport user input
                stt,  # STT
                context_aggregator.user(),  # User responses
                llm,  # LLM
                tts,  # TTS
                transport.output(),  # Transport bot output
                context_aggregator.assistant(),  # Assistant spoken responses
            ]
        )

        task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))

        # Initialize flow manager with LLM
        flow_manager = FlowManager(
            task=task,
            llm=llm,
            context_aggregator=context_aggregator,
            flow_config=flow_config,
        )

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            await transport.capture_participant_transcription(participant["id"])
            # Initialize the flow processor
            await flow_manager.initialize()

        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
