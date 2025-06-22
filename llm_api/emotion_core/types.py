# llm_api/emotion_core/types.py
# タイトル: Emotion Core Data Types
# 役割: 感情分析・制御機能全体で共有されるデータ構造（Enum、データクラス）を定義する。

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional

import torch

class EmotionCategory(Enum):
    """
    論文で定義されている26の感情カテゴリ 。
    """
    ADMIRATION = "admiration"
    ADORATION = "adoration"
    AESTHETIC_APPRECIATION = "aesthetic_appreciation"
    AMUSEMENT = "amusement"
    ANGER = "anger"
    ANXIETY = "anxiety"
    AWE = "awe"
    AWKWARDNESS = "awkwardness"
    BOREDOM = "boredom"
    CALMNESS = "calmness"
    CONFUSION = "confusion"
    CRAVING = "craving"
    DISGUST = "disgust"
    EMPATHIC_PAIN = "empathic_pain"
    ENTRAPMENT = "entrapment"
    EXCITEMENT = "excitement"
    FEAR = "fear"
    HORROR = "horror"
    INTEREST = "interest"
    JOY = "joy"
    NOSTALGIA = "nostalgia"
    RELIEF = "relief"
    ROMANCE = "romance"
    SADNESS = "sadness"
    SATISFACTION = "satisfaction"
    SURPRISE = "surprise"
    NEUTRAL = "neutral" # 論文の分類器で使われているため追加 

@dataclass
class ValenceArousal:
    """
    感情の基本次元であるValence（快・不快）とArousal（覚醒度）を格納するデータクラス 。
    """
    valence: float  # -1.0 (不快) から 1.0 (快)
    arousal: float  # -1.0 (沈静) から 1.0 (覚醒)

@dataclass
class EmotionVector:
    """
    特定の感情に対応するステアリングベクトルの情報を保持するデータクラス。
    """
    emotion: EmotionCategory
    vector: torch.Tensor
    intensity: float = 1.0

@dataclass
class EmotionAnalysisResult:
    """
    感情監視モジュールによる分析結果を格納するデータクラス。
    """
    dominant_emotion: Optional[EmotionCategory] = None
    emotion_scores: Dict[EmotionCategory, float] = field(default_factory=dict)
    valence_arousal: Optional[ValenceArousal] = None
    interest_score: float = 0.0

@dataclass
class ActionRequest:
    """
    感情トリガーによって発行される行動要求を格納するデータクラス。
    """
    trigger_emotion: EmotionCategory
    confidence: float
    context: Dict[str, Any]
    requested_action: str # 例: "web_search"