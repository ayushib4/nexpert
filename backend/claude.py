from typing import Optional
from dotenv import load_dotenv

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT


load_dotenv()  # take environment variables from .env.
anthropic = Anthropic()  # defaults to os.environ.get("ANTHROPIC_API_KEY")


class Claude:
    def __init__(
        self,
        prompt: Optional[str] = None,
        keep_state: bool = True,
        model: str = "claude-2",
        max_tokens_to_sample: int = 16_000,
        temperature: float = 0.0,
        **kwargs,
    ):
        self.messages = []
        if prompt is not None:
            self.messages.append(f"{HUMAN_PROMPT} {prompt} ")
        self.keep_state = keep_state
        self.model = model
        self.max_tokens_to_sample = max_tokens_to_sample
        self.temperature = temperature
        self.kwargs = kwargs

    def __call__(
        self,
        prompt: str,
        input_role_or_prefix: str = "user",
        output_role_or_suffix: str = "assistant",
    ) -> str:
        if input_role_or_prefix == "user":
            prefix = HUMAN_PROMPT + " "
        elif input_role_or_prefix == "assistant":
            prefix = AI_PROMPT + " "
        elif input_role_or_prefix is None:
            prefix = ""
        else:
            prefix = input_role_or_prefix

        if output_role_or_suffix == "user":
            suffix = " " + HUMAN_PROMPT
        elif output_role_or_suffix == "assistant":
            suffix = " " + AI_PROMPT
        elif output_role_or_suffix is None:
            output_role_or_suffix = ""
        else:
            suffix = output_role_or_suffix

        input_prompt = "".join(self.messages) + prefix + prompt + suffix

        completion = anthropic.completions.create(
            prompt=input_prompt,
            model=self.model,
            max_tokens_to_sample=self.max_tokens_to_sample,
            temperature=self.temperature,
            **self.kwargs,
        ).completion

        if self.keep_state:
            self.messages.append(prefix + prompt)
            self.messages.append(suffix + completion)

        return completion


if __name__ == "__main__":
    chat = Claude()
    response = chat("Hello")
    print(response)
    response = chat("How are you?")
    print(response)
