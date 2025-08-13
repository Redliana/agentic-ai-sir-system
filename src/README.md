# THE SIMPLEST, BUT NO SIMPLER, MULTI-AGENTIC-AI AGENT-BASED MODEL #

## Introduction ##
This repo contains all the source code for the simpliest, but no simplier, multi-agentic-AI, agent-based model. A stochastic SIR model is used as the prototype model for demonstrating the capabilities of agentic-AI in agent-based modeling systems.

## What is Agentic AI? ##
Agentic AI is an AI system that acts autonomously to achieve tasks, making decisions and taking actions with limited human oversight.

## What is Multi-Agentic AI? ##
Multi-Agentic AI systems are AI systems where multiple autonomous AI agents interact and collaborate to achieve complex objectives. Each AI agent is characterized by their unique capabilities: a combination of a unique task and access to tools that enable task completion.

Thus, in a multi-agentic AI system, we describe AI agents by their **tasks**, access to **tools**, and **communication** with each other AI agents such that, through autonomous decision-making, agents are able to collaboratively achieve an objective.

## Agentic AI vs. Modular Programming ##
Agentic AI is an evolving field of development and as such, software engineers are challenged to understand how this new workflow is different than established frameworks. In particular, one must consider: what are the nuanced differences between agentic AI and modular programming? Modular programming is a design technique that breaks a program down into independent, reusable modules responsible for different tasks. Similiary, agentic AI employs modular structure in its program design, however, the key difference is that AI agents have autonomous, decision-making capabilities. This paradigm shift occurs becasue of the use of large-langauge models (LLMs) in agentic AI models, assigning AI agents a **persistent entitity** within program execution.

We outline the parameters of a persistent entity with the following criteria:
1. AI agents have encapsulated reasoning capabilities
2. AI agents have dynamic planning and delegation capabilities:  
3. AI agents have independent operation capabilities

This work includes the use of modular programming within the SIR simulation model, however, the use of AI agents that autonomously perform tasks and communicate with one another to fulfill the greater objective of this model satisifies the requirements of an agentic AI workflow.

## Objective ##
The objective of this agentic AI system is to answer questions about the spread of an infectious disease. Questions may include, but are not limited to, "how does a disease spread over a given population?", "when will the infection reach its peak?", "what is the rate of infection?", "what is the rate of recovery?", "how many people will be impacted?," and etc. To fulfill this objective, it is imperative that we task agentic AI with the following tasks: 

* Receive prompt from user (i.e. questions, simulation run requests, etc.)
* Translate user input into actionable tasks.
* Run the simulation with user input.
* Analyze simulation results.
* Determine answers for user questions.
* Report on findings in a natural-langauge format.
* Present findings to the user.

To fulfill this objective, AI agents were assigned tasks and communication channels. These agents are discussed in more detail below.

## AI Agent Descriptions ##
This project employs four AI agents to carry out the tasks described above. These agents and their associated tasks are outlined the following table:

| **Agent** | **Primary Task** | **Tools Used** | **Inputs** | **Outputs** |
|-----------|------------------|----------------|------------|-------------|
| `ControlAgent` | Intelligent decision-making | LLM API, logic/planning | Analyzer/Reporter data | Rerun requests, summary feedback |
| `RunnerAgent` | Run simulations | `subprocess`, `python3`, script | `seed`, `output_path`| CSV/log file |
| `AnalyzerAgent`| Analyze simulation output | `pandas`, `numpy`| Output from `RunnerAgent`| Stats/dict |
| `ReporterAgent` | Generate reports | Templating, graphing | Analysis results | Report file(s) |

The AI agents are assigned roles, tasks, and tools, and are expected to communicate with one another through an interaction workflow which is described in more detail next.

## AI Agent Interaction Flow ##
AI agents must interact and communicate after tasks are complete to track objective completion. The interaction between these agents is outlined below:

1. **Control Agent (`control_agent.py`)**  
   - Monitors all outputs and agent messages.  
   - Determines whether simulations should be rerun, adjusted, or summarized.  
   - Powered by an LLM to reason over results and recommend actions.

2. **Runner Agent (`runner_agent.py`)**  
   - Receives seed and output path from `Main`.  
   - Executes `simulation_sir.py` with those parameters via `subprocess`.  
   - Produces simulation output as a CSV or log file.

3. **Analyzer Agent (`analyzer_agent.py`)**  
   - Receives the output file from `RunnerAgent`.  
   - Loads data using `pandas`, computes statistics (i.e. peak infected).  
   - Returns a summary dictionary of analysis results.

4. **Reporter Agent (`reporter_agent.py`)**  
   - Receives the analysis results from `AnalyzerAgent`.  
   - Generates a visual/text report (graphs, markdown summaries, etc.).  
   - Stores or returns the report path.


## LLM Usage ##
As previously mentioned, the Control Agent is powered by an LLM. For the purpose of this simpliest, but no simplier, model, the authors employed the use of an Ollama, an open-source LLM engine using Mistral LLM. To initialize the LLM, users must prime the model with the following command: `ollama run mistral`

## Try it Yourself ##
To get started, initialize the program with the following command: `python3 main.py`

## To Activate the Virtual Environment and Packages for this Repo
`source venv/bin/activate`

## To Activate Ollama LLM for this Repo
`ollama run mistral`