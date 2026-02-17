"""Provider- and domain-agnostic interfaces for pluggable components."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .schemas import AnalysisResult, EvidenceChunk, KGFact, RunArtifact, RunRequest


class IntentClassifier(ABC):
    """Classify user messages into configured intent labels."""

    @abstractmethod
    def classify(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def classify_followup(self, text: str) -> str:
        raise NotImplementedError


class ModelRunner(ABC):
    """Execute a domain-specific model run based on normalized parameters."""

    @abstractmethod
    def run(self, request: RunRequest) -> List[RunArtifact]:
        raise NotImplementedError


class Analyzer(ABC):
    """Compute metrics or diagnostics from domain artifacts."""

    @abstractmethod
    def analyze(self, question: str) -> AnalysisResult:
        raise NotImplementedError


class Retriever(ABC):
    """Retrieve relevant supporting evidence for answer generation."""

    @abstractmethod
    def retrieve(self, query: str, limit: int = 5) -> List[EvidenceChunk]:
        raise NotImplementedError


class Reporter(ABC):
    """Render structured results into human-readable responses."""

    @abstractmethod
    def report(self, question: str, analysis_results: Dict[str, Any]) -> str:
        raise NotImplementedError


class KGClient(ABC):
    """Write and query graph facts across any KG backend."""

    @abstractmethod
    def upsert_facts(self, facts: List[KGFact]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

