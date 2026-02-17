# Model Education

---

## Historical Background of the SIR Model

### Who developed it
The SIR (Susceptible–Infectious–Recovered) model was first formally developed by Scottish physicians and epidemiologists William Ogilvy Kermack and Anderson Gray McKendrick in 1927.

### When and why it was developed
Kermack and McKendrick were studying historical epidemics and sought to mathematically explain the threshold phenomenon — why some outbreaks die out quickly while others spread widely.
Their 1927 paper, “A Contribution to the Mathematical Theory of Epidemics”, introduced a simple system of differential equations to describe the flow of individuals between three compartments:
	•	S (Susceptible): Those who can catch the disease
	•	I (Infectious): Those currently infected and able to transmit
	•	R (Recovered/Removed): Those who have recovered (or died) and can no longer transmit

### Development motivation
Their motivation was to predict the trajectory of epidemics and understand the critical factors controlling spread — without access to computers, big data, or genetic testing, they relied on theory and mathematics.

---

## Model Mechanics 
In its classic deterministic form, the SIR model assumes:
	•	Population size is fixed (no births/deaths except from the disease)
	•	Transmission rate (β) and recovery rate (γ) are constant
	•	The population mixes homogeneously (everyone interacts equally)
### Model equations
\frac{dS}{dt} = -\beta S I
\frac{dI}{dt} = \beta S I - \gamma I
\frac{dR}{dt} = \gamma I
Where:
	•	β controls how fast the disease spreads
	•	γ controls how fast people recover or are removed
	•	R₀ = β / γ (basic reproduction number) — if R₀ > 1, the outbreak can grow

---

## SIR Model Use Cses
While the original model was paper-and-pencil math, the SIR framework is still a foundational starting point in epidemiology today, often adapted to:
	•	SEIR models (adding “Exposed” to model incubation periods)
	•	Age-structured models (to capture different contact patterns)
	•	Network models (capturing real-world contact structures)
	•	Stochastic versions (to handle randomness, especially in small populations)
### Modern day applications
	•	Predicting outbreak curves for measles, flu, Ebola, and COVID-19
	•	Vaccine strategy planning — estimating the herd immunity threshold
	•	Evaluating interventions like lockdowns, masking, or travel restrictions
	•	Health resource forecasting — estimating ICU demand

---

## Why Stochastic Modeling Matters in Public Health
The deterministic SIR model gives an average outcome, assuming large, perfectly mixed populations.
Stochastic SIR models incorporate randomness — infection and recovery events are probabilistic, not certain. This matters because:
	•	Early in an outbreak, chance events (a superspreader, a cluster dying out) can dramatically change the course
	•	In small or rural populations, random fluctuations may dominate
	•	Stochastic models give ranges and probabilities, not just a single trajectory — vital for risk management

---

## Lessons from COVID-19
During COVID-19, both deterministic and stochastic SIR-type models were used to:
	•	Estimate R₀ early in the outbreak (around 2.2–3.0 for SARS-CoV-2)
	•	Model impact of interventions (mask mandates, distancing, vaccination)
	•	Predict waves of infection after policy changes
	•	Guide vaccine rollout strategies — deciding whether to prioritize high-contact groups or vulnerable populations
### Example:
A stochastic SIR variant could simulate 10,000 possible epidemic trajectories under different school reopening policies, giving decision makers:
	•	Probability of ICU overload
	•	Time until peak cases
	•	Confidence intervals around case numbers

These uncertainty bounds were crucial for decision-making, especially when policymakers had to balance public health with economic and social concerns.

---

## How SIR models help decision makers
Even though more complex agent-based and genomic models exist, SIR models remain popular because they are:
	•	Simple and interpretable — politicians and the public can understand the logic
	•	Fast to run — essential in emergencies
	•	Flexible — easy to modify for new diseases or interventions
	•	A baseline — used to compare against more complex simulations

---

## Model Assumptions
1. We assume perfect mixing in-between agents such that agents are perfectly mixed into groups.
2. Agents move randomly between groups each during each timestep of the simulation.
3. Susceptible agents can only become infected by coming in contact with infected agents.
4. Model parameters are given by the user and they are consistent across model runs.
5. This is a stochastic which means this model has randomness added to it. This makes the model more realistic.
6. We are not considering reproduction in this model so we do not consider birth rate or death rate. If asked, about this, kindly mention that it is not considered in this model.
7. No intervention is considered in this model. 

---

End of manual.