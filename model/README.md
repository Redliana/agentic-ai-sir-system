# SIR AGENT-BASED MODEL #

An infectious disease model - the SIR model - was chosen as the model to use an Agentic AI workflow to demonstrate the utility of Agentic AI systems. This model was developed at Argonne National Laboratory in a Jupyter Notebook environment and translated into a modular programming structure for the integration with Agentic AI.

## Why the SIR Model? ##
The SIR model is a stochastic compartmental model with 3 basic compartments:
1. S - the number of susceptible agents.
    When a susceptible agent and infectious agent have "infectious content," the susceptible agent contracts the disease and transitions to the infectious compartment. 
2. I - the number of infectious agents.
    These are agents who have been infected and are capable of infecting susceptible agents.
3. R - the number of recovered agents.
    These are agents who have either been infected and recovered from the disease and entered into the removed compartment.

SIR models evaluate the behavior between three agent types and their ability to infect, contract, and recover from infections. This isn't to say that this model covers it all, in fact, far from it. This model is a basic introduction to infectious disease models and is the reason why it was chosen as the candidate ABM for Agentic AI integration.
