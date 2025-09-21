from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod
from langchain.chat_models.base import BaseChatModel


# 추후 tokenperminute, tokenperminute 추가


@dataclass
class ModelConfig:
    """모델별 설정을 관리하는 클래스
    
    각 LLM 모델의 기본적인 설정값들을 저장하고 관리합니다.
    
    Attributes:
        model_name (str): 사용할 모델의 이름 (예: "gpt-4", "claude-3")
        api_base (str): API 엔드포인트 URL
        api_key (str): API 인증 키
        seed (int): 결과 재현을 위한 시드값 (기본값: 66)
        max_tokens (int): 최대 토큰 수 (기본값: 4096)
        provider (str): AI 제공 업체명 (예: "openai", "anthropic")"""
    model_name: str
    api_key: str
    api_base: str = None
    seed : int = 66
    max_tokens: int = 4096
    rpm : int = None
    provider: str = "openai"  # 프로바이더 정보 추가
    
@dataclass
class GeminiModelConfig:
    """모델별 설정을 관리하는 클래스
    
    각 LLM 모델의 기본적인 설정값들을 저장하고 관리합니다.
    
    Attributes:
        model_name (str): 사용할 모델의 이름 (예: "gpt-4", "claude-3")
        api_base (str): API 엔드포인트 URL
        api_key (str): API 인증 키
        seed (int): 결과 재현을 위한 시드값 (기본값: 66)
        max_tokens (int): 최대 토큰 수 (기본값: 4096)
        provider (str): AI 제공 업체명 (예: "openai", "anthropic")"""
    model_name: str
    api_key: str
    seed : int = 66
    max_tokens: int = 4096
    rpm : int = None
    provider: str = "google"  # 프로바이더 정보 추가    
    
    

@dataclass
class NaverModelConfig(ModelConfig):
    """네이버 전용 모델 설정 클래스
    
    ModelConfig를 상속받아 네이버 클로바 API에 필요한 추가 설정을 포함합니다.
    
    Attributes:
        ncp_apigw_api_key (str): 네이버 클라우드 플랫폼 API Gateway 키"""
    apigw_api_key: str = ""
    
@dataclass
class LocalModelConfig:
    model_name: str
    lora_model_path: Optional[str] = None
    lora_name: Optional[str] = None  # Name for the LoRA adapter
    port : int = 30000
    max_tokens: int = 4096
    gpus : str = "2,3"
    dp : int = 1 # 증가시킬시 throughoutput 증가
    tp : int = 2 # 모델 크기가 커서 VRAM이 더 필요할 때
    seed : int = 66
    mem_fraction_static : float = 0.9 # KV cahce를 위해 사용될 메모리, outofmemory 시 줄일것
    max_running_request : int = 1024 # 한 번에 최대로 돌릴 수 있는 max request 양
    rpm = None
    
    
    

class BaseLLMFactory(ABC):
    """LLM 생성을 위한 추상 팩토리 클래스
    
    각 AI 제공업체별 LLM 인스턴스 생성을 위한 인터페이스를 정의합니다.
    팩토리 메서드 패턴을 사용하여 구체적인 LLM 구현체 생성을 서브클래스에 위임합니다.
    """
    @abstractmethod
    def create_llm(self, config: ModelConfig, temperature: float) -> BaseChatModel:
        pass

