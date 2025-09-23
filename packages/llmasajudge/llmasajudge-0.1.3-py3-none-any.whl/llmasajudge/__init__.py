import os
from openai import OpenAI

__all__ = ["WandbInferenceLLMJudge"]

class WandbInferenceLLMJudge:
    DEFAULT_TEMPLATE = """\
You are a judge. Read input, model_output, and ground_truth.
Return exactly one word: right or wrong.
Rules:
- Treat extra words or punctuation as irrelevant if the same final value is present.
- Output must be exactly right or wrong. No JSON. No quotes. No extra text.
##################
{notes_section}{input_section}model_output:
{model_output}
##################
ground_truth:
{ground_truth}
##################
"""
    def __init__(self, models, api_key=None, base_url=None, project=None, default_headers=None,
                 custom_template=None, notes=None):
        self.models = models
        self.notes = notes or ""
        self.template = custom_template or self.DEFAULT_TEMPLATE

        kwargs = {"base_url": base_url or "https://api.inference.wandb.ai/v1"}
        if api_key or os.getenv("WANDB_API_KEY"):
            kwargs["api_key"] = api_key or os.getenv("WANDB_API_KEY")
        if project or os.getenv("WANDB_PROJECT"):
            kwargs["project"] = project or os.getenv("WANDB_PROJECT")

        headers = dict(default_headers or {})
        if project or os.getenv("WANDB_PROJECT"):
            headers.setdefault("OpenAI-Project", project or os.getenv("WANDB_PROJECT"))
        headers.setdefault("OpenAI-Project", "wandb_fc/quickstart_playground")
        kwargs["default_headers"] = headers

        self.client = OpenAI(**kwargs)

    def _build_prompt(self, input, model_output, ground_truth):
        notes_section = f"notes:\n{self.notes}\n" if self.notes else ""
        input_section = f"input:\n{input}\n##################\n" if input else ""
        return self.template.format(
            notes_section=notes_section,
            input_section=input_section,
            model_output=str(model_output),
            ground_truth=str(ground_truth),
        )
    

    @staticmethod
    def _last6_right_wrong(s: str):
        if not s:
            return None
        tail = s.strip()[-6:].lower()
        if "right" in tail:
            return True
        if "wrong" in tail:
            return False
        return None

    def _ask_model(self, model, prompt, max_tokens, model_output, ground_truth):
        try:
            resp = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=max_tokens,
            )
            content = (resp.choices[0].message.content or "").strip()
            parsed = self._last6_right_wrong(content)
            if parsed is not None:
                return parsed
        except Exception:
            print("model call failed, falling back to string match", flush=True)
        return str(model_output).strip() == str(ground_truth).strip()

    def judge(self, input, model_output, ground_truth, max_tokens=8, mode="majority"):
        prompt = self._build_prompt(input, model_output, ground_truth)
        votes = []
        for m in self.models:
            res = self._ask_model(m, prompt, max_tokens, model_output, ground_truth)
            print(f"Model {m} voted: {res}", flush=True)
            votes.append({"model": m, "correct": res})

        if mode == "single":
            final = votes[0]["correct"]
        elif mode == "majority":
            true_votes = sum(v["correct"] for v in votes)
            false_votes = len(votes) - true_votes
            final = True if true_votes >= false_votes else False
        else:
            raise ValueError("mode must be 'majority' or 'single'")

        return {"correct": final, "mode": mode, "votes": votes}
