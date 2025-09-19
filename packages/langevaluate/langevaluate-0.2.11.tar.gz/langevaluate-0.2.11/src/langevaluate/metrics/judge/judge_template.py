from typing import Literal, Dict, List
from langevaluate.metrics import BaseTemplate
from pathlib import Path
import json
import toml
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate


class JudgeTemplate(BaseTemplate):
    def __init__(self, language : Literal['ko', 'en'] = 'ko', 
                 template_type : Literal['reasoning', 'only_answer'] = 'reasoning',
                 category: str = 'temporal_relevance',
                 prompt : str = None,
                 ):
        self.system_message_for_answer : SystemMessagePromptTemplate
        self.human_message_for_answer : HumanMessagePromptTemplate
        self.prompt_for_answer : ChatPromptTemplate
        self.language = language
        self.template_type = template_type
        self.category = category
        self._default_prompts = self._load_prompt_template()
        self._initialize_messages()
        
    def _load_prompt_template(self) -> Dict[str, Dict[str, str]]:
        """Load prompt template from JSON file."""
        toml_path = Path(__file__).parent.parent.parent / 'prompt_storage' / 'medical_evaluate_prompt.toml'
        try:
            with open(toml_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template file not found at {toml_path}")
        except toml.TomlDecodeError:
            raise ValueError(f"Invalid toml format in prompt template file at {toml_path}")

    def _initialize_messages(self) -> None:        
        # Get category-specific template
        try:
            category_templates = self._default_prompts['category'][self.category]
            template = category_templates[self.template_type][self.language]
            self.human_message = HumanMessagePromptTemplate.from_template(template)
        except KeyError as e:
            raise ValueError(f"Invalid category or template type: {e}")
        
        
        self.prompt = ChatPromptTemplate.from_messages([self.human_message])
        
    def get_prompt_for_score(self) -> ChatPromptTemplate:
        """
        언어에 따른 적절한 프롬프트를 반환합니다.
        
        Args:
            actual_output (str): 분석할 텍스트
            
        Returns:
            str: 언어에 맞는 형식화된 프롬프트 문자열
        """
        
        return self.prompt
    
    def format_prompt(self, question: str, answer: str) -> str:
        """
        Format the prompt with the given question and answer.
        
        Args:
            question: The user's question
            answer: The assistant's answer to evaluate
            
        Returns:
            Formatted prompt string
        """
        return self.prompt.format_messages(
            question=question,
            answer=answer
        )
        