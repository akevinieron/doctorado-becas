"""Sistema de becas RD: datos sinteticos, modelado y asistente conversacional."""

from .data_generation import GenerationConfig, generate_synthetic_data, save_synthetic_dataset
from .modeling import train_models, predict_eligibility, load_artifacts
from .assistant import ScholarshipAssistant, chat_assistant

__all__ = [
    "GenerationConfig",
    "generate_synthetic_data",
    "save_synthetic_dataset",
    "train_models",
    "predict_eligibility",
    "load_artifacts",
    "ScholarshipAssistant",
    "chat_assistant",
]
