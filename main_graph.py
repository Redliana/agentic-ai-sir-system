# main.py

# Import libraries
from langgraph.graph import StateGraph
from agents.ui_agent import UIAgent
from agents.model_agent import ModelAgent
from agents.rag_agent import RAGAgent


# Initialize agents
control = UIAgent(test_mode=True)
runner = ModelAgent()
rag = RAGAgent()

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

def get_analysis_question_node(state: State):
    question = "What was the peak infection?"
    state["user_question"] = question
    return state

def retrieve_and_generate_node(state: State):
    query = state["user_question"]
    response = rag.run(query)
    state["rag_response"] = response
    print(f"\nRAG Response: {response}")
    return state

# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("control_prompt", control_prompt_node)
graph_builder.add_node("run_sim", run_sim_node)
graph_builder.add_node("get_analysis_question", get_analysis_question_node)
graph_builder.add_node("retrieve_and_generate", retrieve_and_generate_node)

#Transitions
graph_builder.set_entry_point("control_prompt")
graph_builder.add_edge("control_prompt", "run_sim")
graph_builder.add_edge("run_sim", "get_analysis_question")
graph_builder.add_edge("get_analysis_question", "retrieve_and_generate")
graph_builder.set_finish_point("retrieve_and_generate")

graph = graph_builder.compile()

# Run it
graph.invoke(State())