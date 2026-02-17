"""Entrypoint for the current default workflow, now built from external config."""

import os
import sys

from agents.analyzer_agent import AnalyzerAgent
from agents.model_agent import ModelAgent
from agents.rag_agent import RAGAgent
from agents.reporter_agent import ReporterAgent
from agents.ui_agent import UIAgent
from core.orchestration.graph import build_graph
from core.orchestration.router import load_graph_config
from core.registry.domain_loader import load_active_domain
from core.orchestration.state import State

DEFAULT_PARAMS = {
    "seed": 42,
    "num_runs": 100,
    "num_agents": 1000,
    "num_steps": 28,
    "num_contacts": 10,
    "infection_prob": 0.3,
    "infection_duration": 3,
    "recovery_prob": 0.1,
}

DOMAIN_METADATA = load_active_domain()
DOMAIN_CONFIG = DOMAIN_METADATA.get("config", {})
DEFAULT_PARAMS = DOMAIN_CONFIG.get("model", {}).get("default_params", DEFAULT_PARAMS)
LOG_PATH_CANDIDATES = DOMAIN_CONFIG.get("analysis", {}).get(
    "log_path_candidates",
    ["src/logs/all_agent_logs.csv", "logs/all_agent_logs.csv"],
)

# Initialize agents
interface = UIAgent(domain_config=DOMAIN_CONFIG)
runner = ModelAgent(domain_config=DOMAIN_CONFIG)
rag = RAGAgent(domain_config=DOMAIN_CONFIG)
reporter = ReporterAgent(domain_config=DOMAIN_CONFIG)


def _resolve_logs_path() -> str:
    for candidate in LOG_PATH_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    return ""


def user_input_node(state: State):
    state["user_input"] = interface.get_user_input()
    state["user_intent"] = interface.classify_intent(state["user_input"])
    return state


def run_model_node(state: State):
    params = interface.prompt_for_parameters(DEFAULT_PARAMS)
    runner.run(params)
    print("[UI Agent]: Model runs are complete")
    return state


def ask_analysis_question_node(state: State):
    state["user_question"] = interface.ask_analysis_question()
    return state


def analyze_node(state: State):
    logs_path = _resolve_logs_path()
    if not logs_path:
        state["analysis_result"] = {
            "error": "No simulation logs found. Please run the model before requesting analysis."
        }
        return state

    question = state["user_question"]
    analyzer = AnalyzerAgent(state_logs=logs_path, domain_config=DOMAIN_CONFIG)
    state["analysis_result"] = analyzer.analyze(question)
    return state


def report_results_node(state: State):
    question = state["user_question"]
    result = state["analysis_result"]
    if "error" in result:
        print(f"\n[Reporter Agent]: {result['error']}")
        return state

    response = reporter.report(question, result)
    print(f"\n[Reporter Agent]: {response}")
    return state


def ask_assumption_question_node(state: State):
    question = state["user_input"]
    response = rag.answer(question)
    print(f"[RAG Agent]: {response}")
    return state


def fallback_node(state: State):
    print(f"\n[UI Agent]: {interface.get_fallback_message()}")
    return state


def follow_up_node(state: State):
    state["follow_up"] = interface.follow_up()
    state["user_intent"] = interface.classify_followup(state["follow_up"])
    return state


def exit_node(state: State):
    print("[UI Agent]: Exiting the program. Goodbye!")
    sys.exit(0)


NODE_HANDLERS = {
    "user_input": user_input_node,
    "run_model": run_model_node,
    "ask_analysis_question": ask_analysis_question_node,
    "analyze": analyze_node,
    "report_results": report_results_node,
    "ask_assumption_question": ask_assumption_question_node,
    "follow_up": follow_up_node,
    "fallback": fallback_node,
    "exit": exit_node,
}

GRAPH_CONFIG = load_graph_config()
graph = build_graph(State, NODE_HANDLERS, GRAPH_CONFIG)

if __name__ == "__main__":
    graph.invoke(State())
