# main.py

# Import libraries
from memory.json_memory import JSONMemory
from langgraph.graph import StateGraph, END
from agents.ui_agent import UIAgent
from agents.model_agent import ModelAgent
from agents.analyzer_agent import AnalyzerAgent

# Establish memory checkpointer
memory = JSONMemory()

# Initialize agents
control = UIAgent(memory=memory, test_mode=True)
runner = ModelAgent(memory=memory)
analyzer = AnalyzerAgent(memory=memory)

# Setup GraphState
class State(dict): pass
graph_builder = StateGraph(State)

# === Node Setup ===

def control_prompt_node(state: State):
    user_input = control.get_user_input()
    state["user_params"] = user_input
    return state

def run_sim_node(state: State):
    params = state["user_params"]
    print(type(params)) # should be dict
    runner.run()
    return state

def notify_complete_node(state: State):
    control.notify_sim_complete()
    return state

def get_analysis_question_node(state: State):
    question = "What was the peak infection?"
    state["user_question"] = question
    return state

def analyze_node(state: State):
    # TODO: make these variables, not hard-coded (should be saved to log file)
    analyzer.load_data("agent_states.csv", "infection_events.csv", "model/config.yaml")
    analyzer.load_column_descriptions("utils/dictionaries/data_desc_dict.yaml")
    answer = analyzer.analyze("agent_states.csv", "infection_events.csv", "model/config.yaml", state["user_question"])
    print(f"\nAnalysis Result: {answer}")
    return state, END

# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("control_prompt", control_prompt_node)
graph_builder.add_node("run_sim", run_sim_node)
graph_builder.add_node("notify_complete", notify_complete_node)
graph_builder.add_node("get_analysis_question", get_analysis_question_node)
graph_builder.add_node("analyze", analyze_node)

#Transitions
graph_builder.set_entry_point("control_prompt")
graph_builder.add_edge("control_prompt", "run_sim")
graph_builder.add_edge("run_sim", "notify_complete")
graph_builder.add_edge("notify_complete", "get_analysis_question")
graph_builder.add_edge("get_analysis_question", "analyze")
graph_builder.set_finish_point("analyze")

graph = graph_builder.compile()

# Run it
graph.invoke(State())