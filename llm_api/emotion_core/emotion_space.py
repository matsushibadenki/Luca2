# /llm_api/emotion_core/emotion_space.py
# タイトル: Emotion Space Builder (Enhanced and Fixed)
# 役割: 感情空間を構築・管理する。エラーハンドリングとロバストネスを強化。

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any # Added Any

import torch
from torch.nn.functional import cosine_similarity

from .sae_manager import SAEManager
from .types import EmotionCategory

# 循環参照を避けるための型チェック用インポート
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..llm_inference_engine import LLMInferenceEngine

logger = logging.getLogger(__name__)

class EmotionSpace:
    """
    感情とSAE特徴のマッピングを管理する「感情空間」を構築するクラス。
    エラーハンドリングとデータ検証を強化。
    """
    def __init__(self, llm_inference_engine: Optional["LLMInferenceEngine"], sae_manager: SAEManager):
        self.llm_engine = llm_inference_engine
        self.sae_manager = sae_manager
        self.device = sae_manager.device
        self.emotion_to_features: Dict[str, List[int]] = {}
        self._validation_stats: Dict[str, int] = {"successful_mappings": 0, "failed_mappings": 0}

    def get_emotion_feature_ids(self, emotion: EmotionCategory) -> List[int]:
        """
        指定された感情に対応するSAE特徴のIDリストを返します。
        """
        feature_ids = self.emotion_to_features.get(emotion.value, [])
        if not feature_ids:
            logger.warning(f"感情 '{emotion.value}' に対応する特徴IDが見つかりません。")
        return feature_ids

    def load_mapping(self, mapping_path: str) -> bool:
        """
        事前計算された感情-特徴マッピングをJSONファイルからロードします。
        """
        path = Path(mapping_path)
        if not path.exists():
            logger.warning(f"感情マッピングファイルが見つかりません: {mapping_path}")
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded_mapping = json.load(f)
            
            # データの検証
            if not isinstance(loaded_mapping, dict):
                logger.error("マッピングファイルの形式が不正です（辞書型である必要があります）。")
                return False
            
            # 特徴IDの検証
            validated_mapping = {}
            for emotion_key, feature_list in loaded_mapping.items():
                if isinstance(feature_list, list) and all(isinstance(f, int) for f in feature_list):
                    # 特徴IDがSAEの次元範囲内かチェック
                    valid_features = [f for f in feature_list if 0 <= f < self.sae_manager.feature_dim]
                    if len(valid_features) != len(feature_list):
                        logger.warning(f"感情 '{emotion_key}' の一部の特徴IDが範囲外です。有効な特徴のみ保持します。")
                    validated_mapping[emotion_key] = valid_features
                else:
                    logger.warning(f"感情 '{emotion_key}' の特徴リストが不正な形式です。スキップします。")
            
            self.emotion_to_features = validated_mapping
            logger.info(f"感情マッピングを正常にロードしました: {mapping_path} ({len(validated_mapping)}件)")
            return True
            
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"感情マッピングのロード中にエラーが発生しました: {e}")
            return False

    def save_mapping(self, output_path: str) -> bool:
        """
        構築した感情-特徴マッピングをJSONファイルに保存します。
        """
        if not self.emotion_to_features:
            logger.warning("保存する感情マッピングがありません。")
            return False
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # メタデータを含むデータ構造で保存
            save_data = {
                "emotion_mappings": self.emotion_to_features,
                "metadata": {
                    "sae_feature_dim": self.sae_manager.feature_dim,
                    "sae_model_dim": self.sae_manager.model_dim,
                    "total_emotions": len(self.emotion_to_features),
                    "validation_stats": self._validation_stats
                }
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            logger.info(f"感情マッピングをファイルに保存しました: {output_path}")
            return True
            
        except IOError as e:
            logger.error(f"感情マッピングの保存中にエラーが発生しました: {e}")
            return False

    def build_space(self, concept_sets_path: str, top_k_words: int = 10, similarity_threshold: float = 0.1) -> bool:
        """
        コンセプトセットに基づき、感情空間を構築します。
        
        Args:
            concept_sets_path: コンセプトセットファイルのパス
            top_k_words: 各感情につき上位何語まで使用するか
            similarity_threshold: 類似度の最小閾値
        """
        logger.info(f"'{concept_sets_path}' から感情空間の構築を開始します...")
        
        try:
            with open(concept_sets_path, 'r', encoding='utf-8') as f:
                concept_sets = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"コンセプトセットファイルの読み込みに失敗しました: {e}")
            return False

        if not isinstance(concept_sets, dict):
            logger.error("コンセプトセットファイルの形式が不正です。")
            return False

        successful_emotions = 0
        total_emotions = len(concept_sets)

        for emotion_str, words in concept_sets.items():
            if not words or not isinstance(words, list):
                logger.warning(f"感情 '{emotion_str}' の単語リストが無効です。スキップします。")
                self._validation_stats["failed_mappings"] += 1
                continue
                
            emotion_label = words[0]
            associated_words = words[1:] if len(words) > 1 else []
            logger.info(f"'{emotion_label}' ({emotion_str}) の処理中...")

            try:
                # ラベル単語の特徴抽出
                label_features = self._get_features_for_word(emotion_label)
                if label_features is None:
                    logger.warning(f"ラベル '{emotion_label}' の特徴抽出に失敗しました。")
                    self._validation_stats["failed_mappings"] += 1
                    continue

                # 関連単語の特徴抽出と類似度計算
                valid_word_features = []
                for word in associated_words:
                    features = self._get_features_for_word(word)
                    if features is not None:
                        valid_word_features.append({'word': word, 'features': features})

                # 類似度計算とランキング
                similarities = self._calculate_similarities(label_features, valid_word_features, similarity_threshold)
                
                # 最終的な特徴セットの構築
                final_features = self._build_final_feature_set(label_features, similarities, top_k_words)
                
                if final_features:
                    unique_feature_ids = self._extract_unique_feature_ids(final_features)
                    self.emotion_to_features[emotion_str] = unique_feature_ids
                    successful_emotions += 1
                    self._validation_stats["successful_mappings"] += 1
                    logger.info(f"  - '{emotion_label}' に {len(unique_feature_ids)} 個のユニークなSAE特徴をマッピングしました。")
                else:
                    logger.warning(f"感情 '{emotion_label}' の有効な特徴が見つかりませんでした。")
                    self._validation_stats["failed_mappings"] += 1

            except Exception as e:
                logger.error(f"'{emotion_label}' の処理中にエラー: {e}", exc_info=True)
                self._validation_stats["failed_mappings"] += 1
                continue

        logger.info(f"感情空間の構築が完了しました。成功: {successful_emotions}/{total_emotions}")
        return successful_emotions > 0

    def _calculate_similarities(self, label_features: torch.Tensor, word_features: List[Dict], threshold: float) -> List[Tuple[str, float, torch.Tensor]]:
        """単語特徴とラベル特徴の類似度を計算"""
        similarities = []
        
        for item in word_features:
            try:
                # コサイン類似度を計算（バッチ次元を追加）
                sim = cosine_similarity(
                    label_features.unsqueeze(0), 
                    item['features'].unsqueeze(0), 
                    dim=-1
                )
                sim_value = sim.item()
                
                # 閾値チェック
                if sim_value >= threshold:
                    similarities.append((item['word'], sim_value, item['features']))
                else:
                    logger.debug(f"単語 '{item['word']}' の類似度 {sim_value:.3f} が閾値 {threshold} を下回りました。")
                    
            except Exception as e:
                logger.warning(f"単語 '{item['word']}' の類似度計算中にエラー: {e}")
                continue
        
        # 類似度で降順ソート
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def _build_final_feature_set(self, label_features: torch.Tensor, similarities: List[Tuple[str, float, torch.Tensor]], top_k: int) -> List[torch.Tensor]:
        """最終的な特徴セットを構築"""
        final_features = [label_features]
        
        # 上位K個の類似単語の特徴を追加
        for word, sim_score, features in similarities[:top_k]:
            final_features.append(features)
            logger.debug(f"  追加: '{word}' (類似度: {sim_score:.3f})")
        
        return final_features

    def _extract_unique_feature_ids(self, feature_tensors: List[torch.Tensor]) -> List[int]:
        """特徴テンソルから活性化している特徴IDを抽出"""
        if not feature_tensors:
            return []
        
        try:
            # 全特徴をスタック
            all_features = torch.stack(feature_tensors)
            
            # 活性化閾値（0より大きい値）
            activation_threshold = 1e-6
            active_indices = torch.where(all_features > activation_threshold)
            
            # ユニークな特徴IDを取得
            unique_feature_ids = torch.unique(active_indices[1]).tolist()
            
            # SAEの次元範囲内かチェック
            valid_ids = [fid for fid in unique_feature_ids if 0 <= fid < self.sae_manager.feature_dim]
            
            if len(valid_ids) != len(unique_feature_ids):
                logger.warning(f"一部の特徴IDが範囲外でした。有効ID数: {len(valid_ids)}/{len(unique_feature_ids)}")
            
            return valid_ids
            
        except Exception as e:
            logger.error(f"特徴ID抽出中にエラー: {e}", exc_info=True)
            return []

    def _get_features_for_word(self, word: str) -> Optional[torch.Tensor]:
        """
        単一の単語からSAE特徴ベクトルを取得するヘルパー関数。
        """
        if not word or not word.strip():
            logger.warning("空の単語が渡されました。")
            return None
            
        word = word.strip()
        
        if self.llm_engine is None:
            logger.debug(f"LLMエンジンがダミーのため、'{word}' の特徴取得はダミーデータです。")
            # ダミーの隠れ状態から特徴を生成する
            dummy_hidden_state = torch.randn(1, 1, self.sae_manager.model_dim, device=self.device)
            dummy_features = self.sae_manager.extract_features(dummy_hidden_state)
            # 適切に次元を調整
            if dummy_features.dim() > 1:
                squeezed_features = dummy_features.squeeze()
                while squeezed_features.dim() > 1:
                    squeezed_features = squeezed_features.mean(dim=0)
                return squeezed_features
            return dummy_features

        try:
            # LLMエンジンから隠れ状態を取得
            hidden_states = self.llm_engine.get_hidden_states_for_text(word)
            if hidden_states is None:
                logger.warning(f"単語 '{word}' の隠れ状態を取得できませんでした。")
                return None
            
            # 最後のトークンの隠れ状態を使用
            if hidden_states.dim() > 2:
                last_token_hidden_state = hidden_states[:, -1, :]
            else:
                last_token_hidden_state = hidden_states
            
            # SAE特徴を抽出
            sae_features = self.sae_manager.extract_features(last_token_hidden_state)
            
            # バッチ次元を削除
            if sae_features.dim() > 1:
                final_features = sae_features.squeeze(0)
                if final_features.dim() > 1:
                    final_features = final_features.mean(dim=0)  # シーケンス次元がある場合は平均
                return final_features
            
            return sae_features
            
        except Exception as e:
            logger.error(f"単語 '{word}' の特徴抽出中にエラー: {e}", exc_info=True)
            return None

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """感情マッピングの統計情報を取得"""
        if not self.emotion_to_features:
            return {"total_emotions": 0, "total_features": 0, "validation_stats": self._validation_stats}
        
        feature_counts = [len(features) for features in self.emotion_to_features.values()]
        all_features = set()
        for features in self.emotion_to_features.values():
            all_features.update(features)
        
        return {
            "total_emotions": len(self.emotion_to_features),
            "total_unique_features": len(all_features),
            "avg_features_per_emotion": sum(feature_counts) / len(feature_counts) if feature_counts else 0,
            "min_features_per_emotion": min(feature_counts) if feature_counts else 0,
            "max_features_per_emotion": max(feature_counts) if feature_counts else 0,
            "validation_stats": self._validation_stats
        }

    def validate_emotion_coverage(self) -> Dict[str, bool]:
        """全感情カテゴリのカバレッジを検証"""
        coverage = {}
        for emotion in EmotionCategory:
            coverage[emotion.value] = emotion.value in self.emotion_to_features
        
        uncovered = [e for e, covered in coverage.items() if not covered]
        if uncovered:
            logger.warning(f"以下の感情がマッピングされていません: {uncovered}")
        
        return coverage