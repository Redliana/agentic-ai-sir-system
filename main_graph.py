# main_graph.py

# Import libraries
import sys

from langgraph.graph import StateGraph

from agents.ui_agent import UIAgent
from agents.model_agent import ModelAgent
from agents.rag_agent import RAGAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent

# Initialize agents
interface = UIAgent()
runner = ModelAgent()
analyzer = AnalyzerAgent(state_logs="logs/all_agent_logs.csv")
rag = RAGAgent()
reporter = ReporterAgent()

# Graph State
class State(dict): pass

def user_input_node(state: State):
    state["user_input"] = interface.get_user_input()
    state["user_intent"] = interface.classify_intent(state["user_input"])
    return state

def get_model_parameters_node(state: State):
    params = interface.get_user_params()
    state["user_params"] = params
    return state

def run_model_node(state: State):
    default_params = {
        "seed": 42,
        "num_runs": 3,
        "num_agents": 1000,
        "num_steps": 28,
        "num_contacts": 10,
        "infection_prob": 0.3,
        "infection_duration": 3,
        "recovery_prob": 0.1
    }
    params = interface.prompt_for_parameters(default_params)
    runner.run(params)
    print("[UI Agent]: Model runs are complete")
    return state

def ask_analysis_question_node(state: State):
    state["user_question"] = interface.ask_analysis_question()
    return state

def analyze_node(state: State):
    question = state["user_question"]
    result = analyzer.analyze(question)
    state["analysis_result"] = result
    return state

def report_results_node(state: State):
    question = state["user_question"]
    result = state["analysis_result"]
    response = reporter.report(question, result)
    print(f"[Reporter Agent]: {response}")
    return state

def ask_assumption_question_node(state: State):
    question = state["user_input"]
    response = rag.answer(question)
    print(f"[RAG Agent]: {response}")
    return state

def fallback_node(state: State):
    print("\n[UI Agent]: Sorry, I didn't understand that. Try asking to run a model, analyze results, or about how the model works.")
    return state

def route_by_intent(state: State) -> str:
    return state["user_intent"]

def follow_up_node(state: State):
    state["follow_up"] = interface.follow_up()
    state["user_intent"] = interface.classify_followup(state["follow_up"])
    return state

def exit_node(state: State):
    print("[UI Agent]: Exiting the program. Goodbye!")
    sys.exit(0)

# Build LangGraph
graph_builder = StateGraph(State)

# Build nodes
graph_builder.add_node("user_input", user_input_node)
graph_builder.add_node("run_model", run_model_node)
graph_builder.add_node("ask_analysis_question", ask_analysis_question_node)
graph_builder.add_node("analyze", analyze_node)
graph_builder.add_node("report_results", report_results_node)
graph_builder.add_node("ask_assumption_question", ask_assumption_question_node)
graph_builder.add_node("follow_up", follow_up_node)
graph_builder.add_node("fallback", fallback_node)
graph_builder.add_node("exit", exit_node)

# Build transitions
graph_builder.set_entry_point("user_input")

# Conditional for Control Agent to handle task assignment
graph_builder.add_conditional_edges(
    "user_input",
    route_by_intent,
    {
        "run": "run_model",
        "analyze": "ask_analysis_question",
        "learn": "ask_assumption_question",
        "parameters": "ask_assumption_question",
        "exit": "exit",
        "unknown": "fallback"
    }
)

# Conditional for follow-up to guide interactions
graph_builder.add_conditional_edges(
    "follow_up",
    route_by_intent,
    {
        "yes": "user_input",
        "no": "exit",
        "unknown": "fallback"
    }
)

graph_builder.add_edge("run_model", "user_input")
graph_builder.add_edge("ask_analysis_question", "analyze")
graph_builder.add_edge("analyze", "report_results")
graph_builder.add_edge("report_results", "follow_up") 
graph_builder.add_edge("ask_assumption_question", "follow_up")
graph_builder.add_edge("fallback", "user_input")

graph_builder.set_finish_point("exit")

graph = graph_builder.compile()

if __name__ == "__main__":
    graph.invoke(State())

