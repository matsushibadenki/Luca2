# /llm_api/emotion_core/sae_manager.py
# Title: Sparse Autoencoder (SAE) Manager (Enhanced and Fixed)
# Role: sae-lensライブラリを使用してSAEモデルをロードし、特徴抽出を行う。エラーハンドリングとフォールバック機能を強化。

import logging
from typing import Optional, Dict, cast, Union, Any # Added Any
import os

import torch

try:
    from sae_lens import SAE
    SAE_AVAILABLE = True
except ImportError:
    SAE = None
    SAE_AVAILABLE = False

logger = logging.getLogger(__name__)

class SAEManager:
    """
    sae-lensライブラリを介してSAEモデルを管理し、特徴抽出と再構成を行うクラス。
    ライブラリが利用できない場合のフォールバック機能付き。
    """
    def __init__(self, release: str, sae_id: str, fallback_mode: bool = True):
        """
        SAEManagerを初期化します。
        
        Args:
            release: SAEモデルのリリース名
            sae_id: SAEモデルのID
            fallback_mode: sae-lensが利用できない場合にダミーモードで動作するか
        """
        self.release = release
        self.sae_id = sae_id
        self.fallback_mode = fallback_mode
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.sae: Optional[Union[SAE, 'DummySAE']] = None
        self.is_dummy = False
        self._feature_dim = 16384  # デフォルトのSAE特徴次元
        self._model_dim = 2048     # デフォルトのモデル次元
        
        if not SAE_AVAILABLE:
            if fallback_mode:
                logger.warning("sae-lensライブラリが利用できません。ダミーモードで動作します。")
                self._initialize_dummy_sae()
            else:
                raise ImportError("sae-lensライブラリがインストールされていません。`pip install sae-lens`を実行してください。")
        else:
            self._load_model()

    @property
    def decoder_weights(self) -> Optional[torch.Tensor]: # Corrected return type
        """デコーダーの重みを取得"""
        if self.sae:
            if hasattr(self.sae, 'W_dec'):
                return cast(torch.Tensor, self.sae.W_dec)
            elif hasattr(self.sae, 'decoder_weights'):
                return cast(torch.Tensor, self.sae.decoder_weights)
        return None

    @property
    def feature_dim(self) -> int:
        """SAE特徴の次元数を取得"""
        if self.is_dummy:
            return self._feature_dim
        elif self.sae and hasattr(self.sae, 'cfg') and hasattr(self.sae.cfg, 'd_sae'):
            return cast(int, self.sae.cfg.d_sae) # Added cast
        else:
            return self._feature_dim

    @property
    def model_dim(self) -> int:
        """モデルの隠れ次元数を取得"""
        if self.is_dummy:
            return self._model_dim
        elif self.sae and hasattr(self.sae, 'cfg') and hasattr(self.sae.cfg, 'd_model'):
            return cast(int, self.sae.cfg.d_model) # Added cast
        else:
            return self._model_dim

    def _load_model(self):
        """実際のSAEモデルをロード"""
        try:
            logger.info(f"HuggingFaceからSAEモデルをロードしています: release='{self.release}', sae_id='{self.sae_id}'...")
            sae_model, _, _ = SAE.from_pretrained(
                release=self.release,
                sae_id=self.sae_id,
                device=self.device
            )
            self.sae = sae_model
            self.sae.eval()
            self.is_dummy = False
            
            # 実際のモデルから次元情報を取得
            if hasattr(self.sae, 'cfg'):
                if hasattr(self.sae.cfg, 'd_sae'):
                    self._feature_dim = cast(int, self.sae.cfg.d_sae) # Added cast
                if hasattr(self.sae.cfg, 'd_model'):
                    self._model_dim = cast(int, self.sae.cfg.d_model) # Added cast
            
            logger.info("✅ SAEモデルのロードに成功しました。")
        except Exception as e:
            logger.error(f"SAEモデルのロード中にエラーが発生しました: {e}", exc_info=True)
            if self.fallback_mode:
                logger.warning("フォールバックモードでダミーSAEを初期化します。")
                self._initialize_dummy_sae()
            else:
                raise

    def _initialize_dummy_sae(self):
        """ダミーSAEモデルを初期化"""
        self.sae = DummySAE(self._model_dim, self._feature_dim, self.device)
        self.is_dummy = True
        logger.info("ダミーSAEモデルで初期化されました。")

    def extract_features(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """隠れ状態からSAE特徴を抽出"""
        if not self.sae:
            raise RuntimeError("SAEモデルがロードされていません。")
        
        # 入力の形状を検証
        if hidden_states.dim() < 2:
            hidden_states = hidden_states.unsqueeze(0)
        
        # デバイスの統一
        hidden_states = hidden_states.to(self.device)
        
        # 次元の検証と調整
        expected_dim = self.model_dim
        if hidden_states.shape[-1] != expected_dim:
            logger.warning(f"入力次元 ({hidden_states.shape[-1]}) が期待値 ({expected_dim}) と異なります。")
            # 次元調整（簡単な線形変換）
            if hidden_states.shape[-1] > expected_dim:
                hidden_states = hidden_states[..., :expected_dim]
            else:
                # パディング
                padding_size = expected_dim - hidden_states.shape[-1]
                padding = torch.zeros(*hidden_states.shape[:-1], padding_size, device=self.device)
                hidden_states = torch.cat([hidden_states, padding], dim=-1)
        
        try:
            with torch.no_grad():
                if self.is_dummy:
                    features = self.sae.encode(hidden_states)
                else:
                    features = self.sae.encode(hidden_states)
            
            return cast(torch.Tensor, features)
        except Exception as e:
            logger.error(f"特徴抽出中にエラーが発生: {e}", exc_info=True)
            # エラー時はゼロ特徴を返す
            batch_size = hidden_states.shape[0] if hidden_states.dim() > 1 else 1
            seq_len = hidden_states.shape[1] if hidden_states.dim() > 2 else 1
            return torch.zeros(batch_size, seq_len, self.feature_dim, device=self.device)

    def reconstruct(self, features: torch.Tensor) -> torch.Tensor:
        """SAE特徴から隠れ状態を再構成"""
        if not self.sae:
            raise RuntimeError("SAEモデルがロードされていません。")
            
        features = features.to(self.device)
        
        try:
            with torch.no_grad():
                if self.is_dummy:
                    reconstructed_states = self.sae.decode(features)
                else:
                    reconstructed_states = self.sae.decode(features)
            
            return cast(torch.Tensor, reconstructed_states)
        except Exception as e:
            logger.error(f"再構成中にエラーが発生: {e}", exc_info=True)
            # エラー時はゼロテンソルを返す
            batch_size = features.shape[0] if features.dim() > 1 else 1
            seq_len = features.shape[1] if features.dim() > 2 else 1
            return torch.zeros(batch_size, seq_len, self.model_dim, device=self.device)

    def get_model_info(self) -> Dict[str, Any]:
        """モデル情報を取得"""
        return {
            "release": self.release,
            "sae_id": self.sae_id,
            "device": self.device,
            "is_dummy": self.is_dummy,
            "feature_dim": self.feature_dim,
            "model_dim": self.model_dim,
            "sae_available": SAE_AVAILABLE,
            "model_loaded": self.sae is not None
        }


class DummySAE:
    """SAEが利用できない場合のダミー実装"""
    
    def __init__(self, d_model: int, d_sae: int, device: str):
        self.d_model = d_model
        self.d_sae = d_sae
        self.device = device
        
        # ダミーの重み行列を生成
        self.W_dec = torch.randn(d_model, d_sae, device=device) * 0.1
        self.W_enc = torch.randn(d_sae, d_model, device=device) * 0.1
        self.b_enc = torch.zeros(d_sae, device=device)
        self.b_dec = torch.zeros(d_model, device=device)
        
        logger.info(f"ダミーSAE初期化: d_model={d_model}, d_sae={d_sae}")

    def encode(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """ダミーエンコード"""
        # 簡単な線形変換 + ReLU
        features = torch.mm(hidden_states.view(-1, self.d_model), self.W_enc.T) + self.b_enc
        features = torch.relu(features)
        return features.view(*hidden_states.shape[:-1], self.d_sae)

    def decode(self, features: torch.Tensor) -> torch.Tensor:
        """ダミーデコード"""
        # 線形変換
        hidden = torch.mm(features.view(-1, self.d_sae), self.W_dec.T) + self.b_dec
        return hidden.view(*features.shape[:-1], self.d_model)