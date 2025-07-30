# main.py

from memory.json_memory import JSONMemory
from langgraph.graph import StateGraph, END
from agents.control_agent import ControlAgent
from agents.runner_agent import RunnerAgent
from agents.analyzer_agent import AnalyzerAgent

memory = JSONMemory()

control = ControlAgent(memory=memory, test_mode=True)
runner = RunnerAgent(memory=memory)
analyzer = AnalyzerAgent(memory=memory)


class State(dict): pass

# Node Setup 

def control_prompt_node(state):
    print("\nDEBUG: Received state in control_prompt_node:")
    print("Type of state:", type(state))
    print("State contents:", state)

    # Proceed if it’s a dict-like structure
    user_input = control.get_user_input()
    state["user_params"] = user_input
    return state

def run_sim_node(state):
    print("\nDEBUG: Received state in run_sim_node:")
    print("Type of state:", type(state))
    print("State contents:", state)
    params = state["user_params"]
    print(type(params)) # should be dict
    runner.run(params)
    return state

def notify_complete_node(state):
    print("\nDEBUG: Received state in notify_complete_node:")
    print("Type of state:", type(state))
    print("State contents:", state)
    control.notify_sim_complete()
    return state

def get_analysis_question_node(state):
    print("\nDEBUG: Received state in get_analysis_question_node:")
    print("Type of state:", type(state))
    print("State contents:", state)
    # Simulated input for now
    question = "What was peak infection?"
    state["user_question"] = question
    return state

def analyze_node(state):
    print("\nDEBUG: Received state in analyze_node:")
    print("Type of state:", type(state))
    print("State contents:", state)
    answer = analyzer.analyze(state["user_question"])
    print(f"\nAnalysis Result: {answer}")
    return state, END

# Build the graph
builder = StateGraph(State)
builder.add_node("control_prompt", control_prompt_node)
builder.add_node("run_sim", run_sim_node)
builder.add_node("notify_complete", notify_complete_node)
builder.add_node("get_analysis_question", get_analysis_question_node)
builder.add_node("analyze", analyze_node)

#Transitions
builder.set_entry_point("control_prompt")
builder.add_edge("control_prompt", "run_sim")
builder.add_edge("run_sim", "notify_complete")
builder.add_edge("notify_complete", "get_analysis_question")
builder.add_edge("get_analysis_question", "analyze")
builder.set_finish_point("analyze")

graph = builder.compile()

# Run it
graph.invoke(State())