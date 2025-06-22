# llm_api/emotion_core/monitoring_module.py
# タイトル: Emotion Monitoring Module
# 役割: LLMの出力テキストや内部のSAE特徴を分析し、現在の感情状態を監視・評価する。

import logging
from typing import Dict, Optional

import torch

from .sae_manager import SAEManager
from .emotion_space import EmotionSpace
from .types import EmotionCategory, EmotionAnalysisResult, ValenceArousal

logger = logging.getLogger(__name__)

class EmotionMonitor:
    """
    LLMの内部状態や出力から感情を分析・監視するクラス。
    """

    def __init__(self, sae_manager: SAEManager, emotion_space: EmotionSpace):
        """
        EmotionMonitorを初期化します。

        Args:
            sae_manager: ロード済みのSAEモデルを管理するマネージャー。
            emotion_space: 感情とSAE特徴のマッピング情報を持つ感情空間。
        """
        self.sae_manager = sae_manager
        self.emotion_space = emotion_space
        self.device = sae_manager.device
        # 注: 論文ではRoBERTaベースの分類器が使用されているが、
        # ここではまずSAE特徴ベースの実装に注力する。
        # self.text_classifier = load_text_emotion_classifier()

    def analyze_emotions_from_features(self, sae_features: torch.Tensor) -> EmotionAnalysisResult:
        """
        抽出されたSAE特徴ベクトルから、各感情の活性度を計算し、感情状態を分析します。

        Args:
            sae_features (torch.Tensor): SAEManagerによって抽出された特徴ベクトル。
                                         形状: (d_sae) または (batch, seq, d_sae)

        Returns:
            EmotionAnalysisResult: 分析結果を格納したデータクラス。
        """
        if sae_features.dim() > 1:
            # バッチやシーケンス次元がある場合は、平均化または最後のトークンを使用
            sae_features = sae_features.mean(dim=list(range(sae_features.dim() - 1)))

        emotion_scores: Dict[EmotionCategory, float] = {}
        for emotion_cat_str, feature_ids in self.emotion_space.emotion_to_features.items():
            if not feature_ids:
                score = 0.0
            else:
                # 感情に対応する特徴の値の合計をスコアとする
                try:
                    score = sae_features[feature_ids].sum().item()
                except IndexError as e:
                    logger.error(f"特徴IDのインデックスエラー ({emotion_cat_str}): {e}")
                    score = 0.0
            
            emotion_cat = EmotionCategory(emotion_cat_str)
            emotion_scores[emotion_cat] = score

        # 最もスコアの高い感情を特定 (より型安全なラムダ式を使用)
        dominant_emotion = max(emotion_scores, key=lambda e: emotion_scores.get(e, 0.0)) if emotion_scores else None

        # 「興味」スコアを特別に計算（自律行動トリガー用）
        interest_score = emotion_scores.get(EmotionCategory.INTEREST, 0.0)

        # 論文で示されたValence-Arousal空間の分析は、追加の次元削減モデル(CEBRAなど)が
        # 必要なため、ここではプレースホルダーとする。
        valence_arousal_result = self.calculate_valence_arousal(sae_features)

        return EmotionAnalysisResult(
            dominant_emotion=dominant_emotion,
            emotion_scores=emotion_scores,
            valence_arousal=valence_arousal_result,
            interest_score=interest_score
        )
    
    def calculate_interest_score(self, sae_features: torch.Tensor) -> float:
        """
        自律行動トリガーのために「興味」の感情スコアのみを効率的に計算します。

        Args:
            sae_features (torch.Tensor): SAE特徴ベクトル。

        Returns:
            float: 興味スコア。
        """
        interest_feature_ids = self.emotion_space.get_emotion_feature_ids(EmotionCategory.INTEREST)
        if not interest_feature_ids:
            return 0.0
            
        if sae_features.dim() > 1:
            sae_features = sae_features.mean(dim=list(range(sae_features.dim() - 1)))
            
        try:
            score = sae_features[interest_feature_ids].mean().item()
            return score
        except IndexError as e:
            logger.error(f"興味スコア計算中のインデックスエラー: {e}")
            return 0.0


    def calculate_valence_arousal(self, sae_features: torch.Tensor) -> Optional[ValenceArousal]:
        """
        SAE特徴からValence-Arousal値を計算します。
        
        注: この機能の完全な実装には、論文のFigure 2のように、SAE特徴空間を
        Valence-Arousal空間にマッピングするための追加の学習済みモデル（例：CEBRA）が必要です。
        ここではそのインターフェースのみを定義します。

        Args:
            sae_features (torch.Tensor): SAE特徴ベクトル。

        Returns:
            Optional[ValenceArousal]: 計算されたV-A値。モデルがない場合はNone。
        """
        # (将来的な実装のためのプレースホルダー)
        # mapping_model = self.load_feature_to_va_model()
        # if mapping_model:
        #     va_vector = mapping_model.predict(sae_features.unsqueeze(0).cpu().numpy())
        #     return ValenceArousal(valence=va_vector[0][0], arousal=va_vector[0][1])
        logger.debug("Valence-Arousal計算は、追加の次元削減モデルが必要なためスキップされました。")
        return None

    def analyze_emotions_from_text(self, text: str) -> EmotionAnalysisResult:
        """
        生成されたテキストから感情を分析します。

        注: 論文ではRoBERTaベースの分類器が使用されています 。
        この機能の完全な実装には、Hugging Faceなどで公開されている
        事前学習済みの感情分類モデルのロードが必要です。
        ここではそのインターフェースのみを定義します。
        """
        # (将来的な実装のためのプレースホルダー)
        # inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        # with torch.no_grad():
        #     logits = self.text_classifier(**inputs).logits
        # scores = torch.softmax(logits, dim=1)[0]
        # ...
        logger.debug("テキストからの感情分析は、外部の分類器モデルが必要なためスキップされました。")
        return EmotionAnalysisResult(dominant_emotion=EmotionCategory.NEUTRAL)