from typing import Any, List, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from texttools.base.base_translator import BaseTranslator
from texttools.formatter.gemma3_formatter import Gemma3Formatter


class PreprocessorOutput(BaseModel):
    """
    List of proper-name strings extracted from the source text.
    """

    entities: List[str] = Field(
        description="All proper names found in the text; return an empty list if none."
    )


class GemmaTranslator(BaseTranslator):
    """
    Translator for Gemma-style models with optional reasoning step.
    Outputs only the translated text, without any additional structure.
    """

    def __init__(
        self,
        client: OpenAI,
        *,
        model: str,
        chat_formatter: Optional[Any] = None,
        use_reason: bool = False,
        temperature: float = 0.0,
        prompt_template: str = None,
        handlers: list[Any] = None,
        **client_kwargs: Any,
    ):
        super().__init__(handlers)
        self.client: OpenAI = client
        self.model = model
        self.temperature = temperature
        self.client_kwargs = client_kwargs
        self.chat_formatter = chat_formatter or Gemma3Formatter()
        self.use_reason = use_reason
        self.prompt_template = prompt_template

    def _build_messages(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        reason: Optional[str] = None,
        proper_names: Optional[list[str]] = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        # This prompt gives initial information about translation like languages and proper names
        enforce_prompt = f"""
        You are a {source_language}-to-{target_language} translator.
        Important Rule: The following are proper names and must NOT be translated.
        They must be only transliterated into {target_language}.
        That means preserving their phonetic form without changing their meaning.
        Apply the rule for **ALL** of following proper names.
        Proper names (do not translate **** of them):
        {proper_names if proper_names else "None"}
        If any proper name is found in the text, you MUST only transliterate it.
        Output only the translated text. No comments, no explanations, no markdown.
        """
        messages.append({"role": "user", "content": enforce_prompt})

        clean_text = text.strip()
        if reason:
            reason_prompt = f"""
            Based on the analysis conducted, translate the following text {"from" + source_language if source_language else ""} to {target_language}.
            The text to be translated is: "{clean_text}"
            The analysis conducted: {reason}
            """
            messages.append({"role": "user", "content": reason_prompt})
        else:
            regular_prompt = f"""Translate the following text from {source_language or "original"} to {target_language}: 
            {clean_text}"""
            messages.append({"role": "user", "content": regular_prompt})

        # Optional additional template
        if self.prompt_template:
            messages.append({"role": "user", "content": self.prompt_template})

        restructured = self.chat_formatter.format(messages=messages)

        return restructured

    def _reason(self, text: str, target_language: str) -> str:
        """
        Internal reasoning step to help the model with translation.
        """

        reason_step_prompt = f"""
        Analyze the following text and identify important linguistic considerations for translation.
        Do not translate the text. Point out any idioms, cultural references, or complex structures that need special attention.
        Also, list all proper nouns that should not be translated. Write your analysis in the {target_language}.
        """
        messages = [
            {"role": "user", "content": reason_step_prompt},
            {"role": "user", "content": text},
        ]

        restructured = self.chat_formatter.format(messages=messages)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=restructured,
            temperature=self.temperature,
            **self.client_kwargs,
        )

        return completion.choices[0].message.content.strip()

    def preprocess(self, text: str) -> list:
        """
        Preprocessor that finds proper names of Islamic figures. The extractions will be given to the
        LLm in order to know that it shouldn't translate them, but transliterate them.
        """

        messages: list[dict[str, str]] = []

        main_prompt = """
        You must detect proper names of people.
        Your task is to extract a JSON list of entities from the given input. For each entity, include:
        text: The exact matched string from the original.
        type: Only include "Proper Name" for actual names of real people. 
        If there is no proper name in the following text, return empty json.
        """
        messages.append({"role": "user", "content": main_prompt})

        text_prompt = f"""The text to be extracted is:{text}"""
        messages.append({"role": "user", "content": text_prompt})

        restructured = self.chat_formatter.format(messages=messages)
        completion = self.client.chat.completions.parse(
            model=self.model,
            messages=restructured,
            response_format=PreprocessorOutput,
            temperature=self.temperature,
            extra_body={
                "guided_decoding_backend": "auto",
            },
            **self.client_kwargs,
        )
        message = completion.choices[0].message

        entities = message.parsed
        return entities

    def translate(
        self, text: str, target_language: str, source_language: Optional[str] = None
    ) -> str:
        """
        Translates text and returns only the translated string.
        """

        # Extract proper names to tell the LLM what names not to translate, but to transliterate
        extracted = self.preprocess(text)
        proper_names = extracted.entities

        reason_summary = None
        if self.use_reason:
            reason_summary = self._reason(text, target_language, source_language)

        messages = self._build_messages(
            text, target_language, source_language, reason_summary, proper_names
        )
        print(f"Original: {text}")
        print(
            f"Translating to {target_language} from {source_language or 'original'}..."
        )
        print(
            f"Reasoning: {reason_summary}" if reason_summary else "Reasoning not used."
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **self.client_kwargs,
        )
        response = completion.choices[0].message.content

        self._dispatch(
            {
                "original_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "translated_text": response,
            }
        )
        return response
