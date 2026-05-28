from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


CodeVariant = Literal["raw", "clean", "canonical"]
CleanerStatus = Literal["ok", "warning", "failed", "unavailable"]


class SnippetRecord(BaseModel):
    record_id: str
    dataset: str
    dataset_version: str
    source_uri: str
    source_path: str
    task_id: str
    task_name: str
    task_category: str | None = None
    language: str
    language_version: str | None = None
    implementation_index: int = 0
    equivalence_group_id: str
    equivalence_confidence: str
    license: str | None = None
    code_raw: str
    code_raw_sha256: str
    ingested_at: datetime


class CodeVariantRecord(BaseModel):
    variant_id: str
    record_id: str
    variant: CodeVariant
    code: str
    char_count: int = Field(ge=0)
    byte_count: int = Field(ge=0)
    sloc: int = Field(ge=0)
    cleaner: str
    cleaner_status: CleanerStatus
    cleaner_warnings: list[str] = Field(default_factory=list)


class TokenCountRecord(BaseModel):
    token_count_id: str
    variant_id: str
    tokenizer_provider: str
    tokenizer_name: str
    tokenizer_package: str
    tokenizer_package_version: str
    model_reference: str | None = None
    token_count: int = Field(ge=0)
    counted_at: datetime


class AgentRunLog(BaseModel):
    run_id: str
    timestamp: datetime
    phase: str
    actor: Literal["coding_agent", "human", "hybrid"]
    model: str | None = None
    task: str
    prompt_hash: str | None = None
    input_artifacts: list[str] = Field(default_factory=list)
    commands: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    decisions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    human_intervention: str | None = None
    reflection_path: str | None = None
