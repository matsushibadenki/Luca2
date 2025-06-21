# llm_api/emotion_core/steering_manager.py
# タイトル: Emotion Steering Manager
# 役割: 感情空間のマッピングを利用し、LLMの感情表現を制御するためのステアリングベクトルを生成・管理する。

import logging
from typing import Optional

import torch
# scikit-learnはオプション依存とする
try:
    from sklearn.decomposition import NMF
except ImportError:
    NMF = None


from .sae_manager import SAEManager
from .emotion_space import EmotionSpace
from .types import EmotionCategory

logger = logging.getLogger(__name__)

class EmotionSteeringManager:
    """
    SAE特徴を用いてLLMの感情表現をステアリング（操作）するためのベクトルを生成するクラス。
    """

    def __init__(self, sae_manager: SAEManager, emotion_space: EmotionSpace):
        """
        EmotionSteeringManagerを初期化します。

        Args:
            sae_manager: ロード済みのSAEモデルを管理するマネージャー。
            emotion_space: 感情とSAE特徴のマッピング情報を持つ感情空間。
        """
        self.sae_manager = sae_manager
        self.emotion_space = emotion_space
        self.device = sae_manager.device
        
        # デコーダーの重みを取得 (d_model, d_sae)
        self.decoder_weights = self.sae_manager.decoder_weights
        if self.decoder_weights is None:
            raise ValueError("SAEManagerからデコーダーの重み 'W_dec' を取得できませんでした。")

    def get_steering_vector(
        self,
        emotion: EmotionCategory,
        intensity: float = 5.0,
        use_nmf: bool = False,
        n_components: int = 10
    ) -> Optional[torch.Tensor]:
        """
        指定された感情のステアリングベクトルを生成します。

        ステアリングベクトルは、その感情に関連するSAE特徴のデコーダーベクトルの
        合計または代表ベクトルとして計算されます。

        Args:
            emotion (EmotionCategory): 対象の感情。
            intensity (float): ステアリングの強さを調整する係数。
            use_nmf (bool): 論文で言及されているNMF(非負値行列因子分解)を使用して
                           より洗練されたベクトルを生成するかどうか。
            n_components (int): NMFを使用する場合のコンポーネント数。

        Returns:
            torch.Tensor: 生成されたステアリングベクトル。対応する特徴がない場合はNone。
        """
        feature_ids = self.emotion_space.get_emotion_feature_ids(emotion)
        if not feature_ids:
            logger.warning(f"感情 '{emotion.value}' に対応するSAE特徴が見つかりません。")
            return None

        if self.decoder_weights is None:
            logger.error("デコーダーの重みが利用できません。")
            return None

        # 対応する特徴のデコーダーベクトルを取得
        # self.decoder_weights の形状は (d_model, d_sae)
        # feature_ids は d_sae のインデックス
        try:
            target_vectors = self.decoder_weights[:, feature_ids] # (d_model, num_features)
        except IndexError as e:
            logger.error(f"特徴IDのインデックスエラー: {e}. 特徴IDがデコーダーの次元数を超えている可能性があります。")
            return None

        if use_nmf and NMF is not None and target_vectors.shape[1] > n_components:
            logger.info(f"NMFを使用して '{emotion.value}' の主要特徴を {n_components} 個抽出します。")
            # NMFは非負値を要求するため、データをシフト
            vectors_np = target_vectors.cpu().numpy()
            min_val = vectors_np.min()
            vectors_non_negative = vectors_np - min_val

            model = NMF(n_components=n_components, init='random', random_state=0)
            W = model.fit_transform(vectors_non_negative)
            H = model.components_

            # 最も影響の大きいコンポーネントをステアリングベクトルとする
            # ここでは単純に、最初のコンポーネントの再構成を使用
            base_vector_non_negative = torch.tensor(model.components_[0], device=self.device)
            base_vector = base_vector_non_negative + min_val
            steering_vector = base_vector

        else:
            # 単純な合計ベクトル
            steering_vector = torch.sum(target_vectors, dim=1)

        # 正規化と強度の適用
        norm = torch.norm(steering_vector)
        if norm > 0:
            normalized_vector = steering_vector / norm
        else:
            logger.warning(f"'{emotion.value}' のステアリングベクトルノルムが0です。")
            return None

        final_vector: torch.Tensor = normalized_vector * intensity
        logger.info(f"感情 '{emotion.value}' のステアリングベクトルを生成しました (強度: {intensity})。")
        
        return final_vector

    def apply_steering(
        self,
        hidden_states: torch.Tensor,
        steering_vector: torch.Tensor
    ) -> torch.Tensor:
        """
        LLMの隠れ状態にステアリングベクトルを適用（加算）します。

        Args:
            hidden_states (torch.Tensor): LLMのレイヤーからの出力隠れ状態。
            steering_vector (torch.Tensor): get_steering_vectorで生成されたベクトル。

        Returns:
            torch.Tensor: ステアリングが適用された新しい隠れ状態。
        """
        if hidden_states.shape[-1] != steering_vector.shape[0]:
            raise ValueError(
                f"隠れ状態の次元数 ({hidden_states.shape[-1]}) と "
                f"ステアリングベクトルの次元数 ({steering_vector.shape[0]}) が一致しません。"
            )
        
        # 隠れ状態の最後のトークンにのみ適用する場合
        # hidden_states[:, -1, :] += steering_vector.to(self.device)
        
        # 全てのトークンに適用する場合
        return hidden_states + steering_vector.to(self.device)