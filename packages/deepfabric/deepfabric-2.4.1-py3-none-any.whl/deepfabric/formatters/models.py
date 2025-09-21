"""
Pydantic models for the formatter system.

These models provide type safety, validation, and better IDE support
for formatter configurations and data structures.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """A single message in a conversation."""

    role: Literal["system", "user", "assistant", "function", "tool"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(..., min_length=1, description="The content of the message")

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("content cannot be empty or whitespace only")
        return v


class ConversationSample(BaseModel):
    """A dataset sample with conversation messages."""

    messages: list[Message] = Field(..., description="list of conversation messages")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")


class QASample(BaseModel):
    """A dataset sample with question-answer structure."""

    question: str = Field(..., min_length=1, description="The question or prompt")
    answer: str | None = Field(None, description="The answer or response")
    final_answer: str | None = Field(None, description="Alternative field for final answer")
    chain_of_thought: str | None = Field(None, description="Reasoning process")
    context: str | None = Field(None, description="Additional context")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")

    @field_validator("final_answer")
    @classmethod
    def must_have_answer(cls, v, info):
        answer = info.data.get("answer")
        if not v and not answer:
            raise ValueError("Must have either answer or final_answer")
        return v


class InstructionSample(BaseModel):
    """A dataset sample with instruction-following structure."""

    instruction: str = Field(..., min_length=1, description="The instruction or task")
    input: str | None = Field(None, description="Optional input context")
    output: str = Field(..., min_length=1, description="The expected output")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")


class GenericSample(BaseModel):
    """A generic dataset sample that can contain any fields."""

    data: dict[str, Any] = Field(..., description="The sample data")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def get(self, key, default=None):
        return self.data.get(key, default)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()


class FormatterConfigModel(BaseModel):
    """Configuration for a formatter instance."""

    name: str = Field(..., min_length=1, description="Unique name for this formatter instance")
    template: str = Field(..., min_length=1, description="Template path (builtin:// or file://)")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Formatter-specific configuration"
    )
    output: str | None = Field(None, description="Output file path for formatted dataset")

    @field_validator("template")
    @classmethod
    def validate_template_format(cls, v):
        if not (v.startswith("builtin://") or v.startswith("file://")):
            raise ValueError('Template must start with "builtin://" or "file://"')
        return v


class AlpacaOutput(BaseModel):
    """Pydantic model for Alpaca formatter output."""

    instruction: str = Field(..., min_length=1, description="The instruction or task")
    input: str | None = Field(None, description="Optional input context")
    output: str = Field(..., min_length=1, description="The expected response")


class GrpoOutput(BaseModel):
    """Pydantic model for GRPO formatter output."""

    messages: list[Message] = Field(..., description="Conversation messages with GRPO formatting")

    @field_validator("messages")
    @classmethod
    def messages_must_have_at_least_one(cls, v):
        if not v or len(v) < 1:
            raise ValueError("messages must contain at least one item")
        return v


class ChatmlStructuredOutput(BaseModel):
    """Pydantic model for ChatML structured output."""

    messages: list[Message] = Field(..., description="Conversation messages")

    @field_validator("messages")
    @classmethod
    def messages_must_have_at_least_one(cls, v):
        if not v or len(v) < 1:
            raise ValueError("messages must contain at least one item")
        return v


class ChatmlTextOutput(BaseModel):
    """Pydantic model for ChatML text output."""

    text: str = Field(..., min_length=1, description="ChatML formatted text")


class FormatterMetadata(BaseModel):
    """Metadata for formatted samples."""

    formatter_name: str = Field(..., description="Name of the formatter used")
    formatter_version: str = Field(..., description="Version of the formatter")
    original_format: str | None = Field(None, description="Original input format detected")
    processing_timestamp: str | None = Field(None, description="When the formatting was applied")
    validation_passed: bool = Field(True, description="Whether output validation passed")


class FormatterStats(BaseModel):
    """Statistics about formatter processing."""

    total_samples: int = Field(..., ge=0, description="Total number of input samples")
    processed_samples: int = Field(
        ..., ge=0, description="Number of successfully processed samples"
    )
    failed_samples: int = Field(..., ge=0, description="Number of failed samples")
    skipped_samples: int = Field(..., ge=0, description="Number of skipped samples")
    processing_time_seconds: float = Field(..., ge=0, description="Total processing time")

    @property
    def success_rate(self) -> float:
        """Calculate the success rate as a percentage."""
        if self.total_samples == 0:
            return 0.0
        return (self.processed_samples / self.total_samples) * 100


class ValidationResult(BaseModel):
    """Result of formatter validation."""

    is_valid: bool = Field(..., description="Whether the sample passed validation")
    errors: list[str] = Field(default_factory=list, description="list of validation errors")
    warnings: list[str] = Field(default_factory=list, description="list of validation warnings")


class FormatterResult(BaseModel):
    """Result of formatter processing."""

    samples: list[dict[str, Any]] = Field(..., description="Formatted samples")
    metadata: FormatterMetadata = Field(..., description="Formatter metadata")
    stats: FormatterStats = Field(..., description="Processing statistics")
    errors: list[str] = Field(default_factory=list, description="Processing errors")


# Configuration models for specific formatters


class GrpoConfig(BaseModel):
    """Configuration for GRPO formatter."""

    reasoning_start_tag: str = Field(
        default="<start_working_out>", description="Start tag for reasoning"
    )
    reasoning_end_tag: str = Field(default="<end_working_out>", description="End tag for reasoning")
    solution_start_tag: str = Field(default="<SOLUTION>", description="Start tag for solution")
    solution_end_tag: str = Field(default="</SOLUTION>", description="End tag for solution")
    system_prompt: str | None = Field(None, description="Custom system prompt")
    validate_numerical: bool = Field(
        default=True, description="Whether to validate numerical answers"
    )


class AlpacaConfig(BaseModel):
    """Configuration for Alpaca formatter."""

    instruction_field: str = Field(default="instruction", description="Field name for instructions")
    input_field: str = Field(default="input", description="Field name for input")
    output_field: str = Field(default="output", description="Field name for output")
    include_empty_input: bool = Field(
        default=True, description="Whether to include empty input fields"
    )
    instruction_template: str | None = Field(
        None, description="Template for instruction formatting"
    )


class ChatmlConfig(BaseModel):
    """Configuration for ChatML formatter."""

    start_token: str = Field(default="<|im_start|>", description="Start token for messages")
    end_token: str = Field(default="<|im_end|>", description="End token for messages")
    output_format: Literal["structured", "text"] = Field(
        default="structured", description="Output format"
    )
    default_system_message: str = Field(
        default="You are a helpful assistant.", description="Default system message"
    )
    require_system_message: bool = Field(
        default=False, description="Whether to require system message"
    )


# Union type for all possible sample formats
DatasetSample = ConversationSample | QASample | InstructionSample | GenericSample


class DatasetInput(BaseModel):
    """Input dataset containing a list of samples."""

    samples: list[DatasetSample] = Field(..., min_length=0, description="list of dataset samples")

    def __len__(self) -> int:
        return len(self.samples)

    def __iter__(self):
        return iter(self.samples)

    def __getitem__(self, index):
        return self.samples[index]


class FormattedOutput(BaseModel):
    """Base class for formatted output samples."""

    class Config:
        extra = "allow"  # Allow additional fields for flexibility


class DatasetOutput(BaseModel):
    """Output dataset containing formatted samples."""

    samples: list[FormattedOutput] = Field(
        ..., min_length=0, description="list of formatted samples"
    )

    def __len__(self) -> int:
        return len(self.samples)

    def __iter__(self):
        return iter(self.samples)

    def __getitem__(self, index):
        return self.samples[index]
