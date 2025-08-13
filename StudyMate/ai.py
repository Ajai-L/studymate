import os
from typing import Optional


class AIService:
    """Lazy-loading wrapper for local IBM Granite models using Transformers."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.environ.get("GRANITE_MODEL_PATH", "ibm-granite/granite-3.3-8b-instruct")
        self.model = None
        self.tokenizer = None
        # Generation defaults from env; values also mirrored in Config
        self.max_new_tokens = int(os.environ.get("GRANITE_MAX_NEW_TOKENS", 512))
        self.temperature = float(os.environ.get("GRANITE_TEMPERATURE", 0.2))
        self.top_p = float(os.environ.get("GRANITE_TOP_P", 0.95))

    def load_model(self):
        if self.model is not None and self.tokenizer is not None:
            return
        # Import inside the method to avoid requiring heavy deps at server start
        from transformers import AutoTokenizer, AutoModelForCausalLM

        trust_remote_code = True  # Granite may use custom modeling code
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=trust_remote_code)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            trust_remote_code=trust_remote_code,
            device_map="auto",
        )

    def _generate(self, prompt: str) -> str:
        self.load_model()
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=self.temperature,
            top_p=self.top_p,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        result = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        # In many instruct models, decode returns prompt + completion. Keep only completion after prompt.
        if result.startswith(prompt):
            return result[len(prompt):].strip()
        return result.strip()

    def summarize_text(self, text: str) -> str:
        prompt = (
            "You are StudyMate, an expert study assistant. Summarize the following content into a concise, well-structured summary that preserves key definitions, formulas, and examples where essential.\n\n"
            "Content:\n" + text + "\n\nSummary:"
        )
        return self._generate(prompt)

    def generate_flashcards(self, text: str, num_cards: int = 10) -> str:
        prompt = (
            "You are StudyMate. Create "
            f"{num_cards} high-quality flashcards as Q/A pairs based on the content below. "
            "Number them and keep each answer concise (1-3 sentences).\n\n"
            "Content:\n" + text + "\n\nFlashcards (Q/A):"
        )
        return self._generate(prompt)

    def generate_competitive_questions(self, text: str, exam_type: str = "GATE", num_questions: int = 10) -> str:
        prompt = (
            "You are StudyMate. Create "
            f"{num_questions} {exam_type} style multiple-choice questions (MCQs) with four options (A-D). "
            "For each question, provide the correct answer at the end as 'Answer: <Option Letter>'. "
            "Focus on conceptual clarity and varied difficulty levels.\n\n"
            "Content:\n" + text + "\n\nMCQs:"
        )
        return self._generate(prompt)

    def answer_custom_prompt(self, prompt_text: str, context_text: Optional[str] = None) -> str:
        if context_text:
            prompt = (
                "You are StudyMate. Use the context to answer the user's request. "
                "Be accurate, clear, and concise.\n\n"
                "Context:\n" + context_text + "\n\n"
                "User request:\n" + prompt_text + "\n\nResponse:"
            )
        else:
            prompt = (
                "You are StudyMate, a helpful study assistant. "
                "Answer the user's request clearly and concisely.\n\n"
                "User request:\n" + prompt_text + "\n\nResponse:"
            )
        return self._generate(prompt)