"""BenchmarkCard schema, vendored from evaleval/auto-benchmarkcard v0.2.0.

Source: https://github.com/evaleval/auto-benchmarkcard at commit
342c1ac7d278a93be75de713c151142b25f635d0 (tag v0.2.0),
src/auto_benchmarkcard/tools/composer/composer_tool.py (models) and field_spec.py (vocabularies).
The models are copied verbatim except for the `provenance` fields, which upstream strips before
output. Update by re-copying from a new pinned commit and changing SCHEMA_ID.

MIT License

Copyright (c) 2026 EvalEval

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

SCHEMA_ID = "evaleval/auto-benchmarkcard@342c1ac7d278a93be75de713c151142b25f635d0"

DATA_TYPE_VOCAB = {
    "text", "image", "video", "audio", "tabular", "code", "interactive-environment",
}
AUDIENCE_VOCAB = {
    "AI researchers", "model developers", "safety evaluators",
    "industry practitioners", "policymakers", "educators",
}
# Not in EvalEval's vocabulary: the readers the humanities benchmarks are made for.
HUMBEN_AUDIENCE_VOCAB = {
    "humanities researchers", "archivists and librarians", "health services researchers",
}


class BenchmarkDetails(BaseModel):

    name: str = Field(
        ...,
        description="The official name of the benchmark as it appears in literature",
    )
    overview: str = Field(
        ...,
        description="2-3 sentence description of what the benchmark measures and its key characteristics",
    )
    data_type: str = Field(
        ...,
        description="The primary data modality (e.g., text, image, audio, multimodal, tabular)",
    )
    domains: List[str] = Field(
        ...,
        description="Specific application domains or subject areas (e.g., medical, legal, scientific, conversational AI)",
    )
    languages: List[str] = Field(
        ...,
        description="All languages supported in the dataset using full language names (e.g., 'English', 'Chinese', 'Spanish', 'Multilingual')",
    )
    similar_benchmarks: List[str] = Field(
        ...,
        description="Names of closely related or comparable benchmarks that measure similar capabilities",
    )
    resources: List[str] = Field(
        ...,
        description="URLs to official papers, datasets, leaderboards, and documentation",
    )
    authors: Optional[List[str]] = None
    logo: Optional[str] = None
    org_url: Optional[str] = None

    @field_validator("domains", "languages", "similar_benchmarks", "resources", mode="before")
    @classmethod
    def _coerce_str_to_list(cls, v):
        return [v] if isinstance(v, str) else v


class PurposeAndIntendedUsers(BaseModel):

    goal: str = Field(
        ...,
        description="The primary objective and research question this benchmark addresses, including what capabilities or behaviors it aims to measure",
    )
    audience: List[str] = Field(
        ...,
        description="Who the benchmark is designed for -- who runs it and who uses its results (controlled vocabulary; see field spec)",
    )
    tasks: List[str] = Field(
        ...,
        description="Specific evaluation tasks or subtasks the benchmark covers (e.g., 'question answering', 'code generation', 'factual accuracy')",
    )
    limitations: str = Field(
        ...,
        description="Known limitations, biases, or constraints of the benchmark that users should be aware of",
    )
    out_of_scope_uses: List[str] = Field(
        ...,
        description="Explicit examples of inappropriate or unsupported use cases for this benchmark",
    )

    @field_validator("audience", "tasks", "out_of_scope_uses", mode="before")
    @classmethod
    def _coerce_str_to_list(cls, v):
        return [v] if isinstance(v, str) else v


class DataInfo(BaseModel):

    source: str = Field(
        ...,
        description="Detailed information about data origins, collection methods, and any preprocessing steps applied",
    )
    size: str = Field(
        ...,
        description="Dataset size. Prefer number of examples from paper (e.g., '817 questions'). "
        "If only disk size from HuggingFace is available, use that (e.g., '1.24 GB')",
    )
    format: str = Field(
        ...,
        description="The data format as described in the paper or README "
        "(e.g., 'JSON with question-answer pairs'). If only the HuggingFace hosting "
        "format is known, note it as such (e.g., 'parquet (HuggingFace hosting format)')",
    )
    annotation: str = Field(
        ...,
        description="Annotation methodology, quality control measures, inter-annotator agreement, and any human involvement in labeling",
    )
    size_breakdown: Union[Dict[str, int], str] = Field(
        default="Not specified",
        description="Per-subset or per-domain item counts as {subset_name: count}; 'Not specified' if not reported",
    )
    collection_date: str = Field(
        default="Not specified",
        description="Data collection or cutoff date/range (e.g. '2023-06' or '2022-2024'); distinct from the card creation date",
    )
    contamination_controls: str = Field(
        default="Not specified",
        description="Train-test leakage protections described in the source: canary string, held-out/private split, encryption",
    )


class Methodology(BaseModel):

    methods: List[str] = Field(
        ...,
        description="Evaluation approaches and techniques applied within the benchmark (e.g., 'zero-shot evaluation', 'few-shot prompting', 'fine-tuning')",
    )
    metrics: List[str] = Field(
        ...,
        description="Specific quantitative metrics used, named in readable form (e.g., 'accuracy', "
        "'F1-score', 'BLEU', 'exact match'). Do not emit a bare '<benchmark>.score' proxy; use "
        "'Not specified' when the source names no real metric",
    )
    calculation: str = Field(
        ...,
        description="Detailed explanation of how metrics are computed, including any normalization or aggregation methods",
    )
    interpretation: str = Field(
        ...,
        description="What scores mean in practice: the score scale and direction (whether higher or "
        "lower is better) and concrete reference points drawn from the reported baseline or human "
        "results; do not invent thresholds the source does not state",
    )
    baseline_results: str = Field(
        ...,
        description="Performance of established models or baselines, with specific numbers and context for comparison",
    )
    validation: str = Field(
        ...,
        description="Quality assurance measures, validation procedures, and steps taken to ensure reliable and reproducible evaluations",
    )
    human_baseline: str = Field(
        default="Not specified",
        description="Human or reference baseline result plus its conditions (time limit, tool/web access, expertise); distinct from baseline_results (model scores)",
    )
    judge_uses_llm: Union[bool, str] = Field(
        default="Not specified",
        description="Whether scoring uses an LLM-as-judge (true/false); 'Not specified' if not reported",
    )
    judge_num: Union[int, str] = Field(
        default="Not specified",
        description="Number of judge models used for LLM-as-judge scoring; 'Not specified' if not reported",
    )
    judge_models: List[str] = Field(
        default_factory=lambda: ["Not specified"],
        description="Names of the judge model(s) used for scoring",
    )
    judge_score_consolidation: str = Field(
        default="Not specified",
        description="How multiple judge scores are consolidated (e.g. majority vote, mean, single judge)",
    )
    validity_justification: str = Field(
        default="Not specified",
        description="What the paper states about construct validity or justification of its metric choice (extract-only; distinct from validation)",
    )

    @field_validator("methods", "metrics", "judge_models", mode="before")
    @classmethod
    def _coerce_str_to_list(cls, v):
        return [v] if isinstance(v, str) else v


class EthicalAndLegalConsiderations(BaseModel):

    privacy_and_anonymity: str = Field(
        ...,
        description="Data protection measures, anonymization or de-identification techniques, and "
        "handling of personally identifiable information; or an explicit statement that the data "
        "contains no personal information or is synthetic",
    )
    data_licensing: str = Field(
        ...,
        description="Specific license terms, usage restrictions, and redistribution permissions",
    )
    consent_procedures: str = Field(
        ...,
        description="How human participants or annotators consented and were compensated: informed "
        "consent, the crowdsourcing platform, participant rights, and withdrawal procedures",
    )
    compliance_with_regulations: str = Field(
        ...,
        description="Adherence to relevant regulations (GDPR, IRB approval, etc.) and ethical review processes",
    )


class BenchmarkCard(BaseModel):

    benchmark_details: BenchmarkDetails
    purpose_and_intended_users: PurposeAndIntendedUsers
    data: DataInfo
    methodology: Methodology
    ethical_and_legal_considerations: EthicalAndLegalConsiderations
