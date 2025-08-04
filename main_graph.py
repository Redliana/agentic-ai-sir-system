# main_graph.py

# Import libraries
from langgraph.graph import StateGraph
from agents.ui_agent import UIAgent
from agents.model_agent import ModelAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent

class State(dict): pass

def control_prompt_node(state: State):
    # Gets user parameters 
    user_input = control.get_user_input()
    state["user_params"] = user_input
    return state

def run_sim_node(state: State):
    # Runs the simulation
    params = state["user_params"]
    runner.run()
    return state

def get_analysis_question_node(state: State):
    # Poses a default question 
    question = "When was peak infection?"
    state["user_question"] = question
    return state

def analyzer_node(state: State):
    # Performs math on logs
    question = state["user_question"]
    results = analyzer.analyze(question)
    state["analysis_results"] = results
    return state

def reporter_node(state: State):
    # Generates user-friendly response
    user_question = state["user_question"]
    analysis_results = state["analysis_results"]
    report = reporter.summarize_results(user_question, analysis_results)
    print("\nFinal Analysis Report:\n", report)
    return state

# Initialize agents
control = UIAgent(test_mode=True)
runner = ModelAgent()
analyzer = AnalyzerAgent(logs_path="logs/all_agent_logs.csv")
reporter = ReporterAgent()

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("control_prompt", control_prompt_node)
graph_builder.add_node("run_sim", run_sim_node)
graph_builder.add_node("get_analysis_question", get_analysis_question_node)
graph_builder.add_node("analyzer", analyzer_node)
graph_builder.add_node("reporter", reporter_node)

graph_builder.set_entry_point("control_prompt")
graph_builder.add_edge("control_prompt", "run_sim")
graph_builder.add_edge("run_sim", "get_analysis_question")
graph_builder.add_edge("get_analysis_question", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.set_finish_point("reporter")

graph = graph_builder.compile()
graph.invoke(State())
