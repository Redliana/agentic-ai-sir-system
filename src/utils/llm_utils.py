# utils.llm_utils.py

from core.providers.factory import create_llm_provider


class OllamaLLM:
    def __init__(self, model="mistral", base_url="http://localhost:11434/api/generate"):
        self.provider = create_llm_provider(
            {"type": "ollama", "model": model, "base_url": base_url}
        )

    def generate(self, prompt: str, system: str = "") -> str:
        return self.provider.generate(prompt=prompt, system=system)

def summarize(summary_data: dict) -> str:
    """
    Generates a formatted string summary of useful statistics
    from the provided summary_data dictionary.
    """
    summary = []

    # Peak infection times - handle list or single value gracefully
    peaks = summary_data.get("peak_infection_times")
    if peaks is not None:
        if isinstance(peaks, (list, tuple)):
            peaks_str = ", ".join(str(p) for p in peaks)
        else:
            peaks_str = str(peaks)
        summary.append(f"Peak infection times: {peaks_str}")

    # Average infection duration
    avg_duration = summary_data.get("avg_infection_duration")
    if avg_duration is not None:
        summary.append(f"Average infection duration: {avg_duration:.2f} time steps")

    # Model parameters - dict to key=value pairs string
    params = summary_data.get("model_parameters")
    if params:
        param_str = ", ".join(f"{k}={v}" for k, v in params.items())
        summary.append(f"Model parameters: {param_str}")

    # Join all lines into one string separated by newlines
    return "\n".join(summary)

def build_prompt(question: str, summary: str) -> str:
    """
    Builds a prompt that includes the summarized data and the user's question.
    """
    prompt = (
        f"You are an epidemic simulation analysis expert.\n"
        f"Simulation Parameters:\n{summary}\n\n"
        f"Peak Infection Time(s): {summary}\n"
        f"Average Infection Duration: {summary} time steps\n\n"
        f"User Question: {question}\n\n"
        f"Answer in a clear and concise way, referencing the data when helpful."
        f"Only return a portion of the prompt when asked that portion specifically."
    )
    return prompt
