# /cli/utils.py
# タイトル: CLI Utility Functions
# 役割: CLIのハンドラ全体で利用される補助的なヘルパー関数を提供する。

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# --- ▼▼▼ ここから追加 ▼▼▼ ---
def print_colored(text: str, color: str) -> None:
    """指定された色でテキストをコンソールに出力します。"""
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    end_code = "\033[0m"
    color_code = color_codes.get(color.lower(), "")
    print(f"{color_code}{text}{end_code}")
# --- ▲▲▲ ここまで追加 ▲▲▲ ---


def enhance_kwargs_for_v2(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    V2モード実行のために、コマンドライン引数を拡張・最適化します。
    (この関数は変更なし)
    """
    enhanced = kwargs.copy()
    mode = kwargs.get('mode', 'simple')

    enhanced['force_v2'] = True

    if 'temperature' not in enhanced:
        mode_temp_map = {
            'efficient': 0.3,
            'balanced': 0.6,
            'decomposed': 0.5,
            'adaptive': 0.6,
            'paper_optimized': 0.6,
            'parallel': 0.6,
            'quantum_inspired': 0.7,
            'edge': 0.3,
            'speculative_thought': 0.7,
            'self_discover': 0.5,
        }
        enhanced['temperature'] = mode_temp_map.get(mode, 0.7)
        logger.debug(f"V2モード '{mode}' のため、temperatureを {enhanced['temperature']} に設定しました。")

    return enhanced


def convert_kwargs_for_standard(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    V2拡張モードの引数を、標準プロバイダーが解釈できる引数に変換します。
    (この関数は変更なし)
    """
    standard = kwargs.copy()
    mode = kwargs.get('mode', 'simple')

    mode_conversion = {
        'efficient': 'simple',
        'balanced': 'reasoning',
        'decomposed': 'reasoning',
        'adaptive': 'reasoning',
        'paper_optimized': 'reasoning',
        'parallel': 'reasoning',
        'quantum_inspired': 'creative-fusion',
        'edge': 'simple',
        'speculative_thought': 'creative-fusion',
        'self_discover': 'reasoning',
    }

    if mode in mode_conversion:
        converted_mode = mode_conversion[mode]
        standard['mode'] = converted_mode
        logger.info(f"フォールバックのため、V2モード '{mode}' を標準モード '{converted_mode}' に変換しました。")

    standard.pop('force_v2', None)

    return standard


def generate_error_suggestions(provider_name: str, errors: List[str]) -> List[str]:
    """
    発生したエラーの内容に基づいて、ユーザーへの改善提案を生成します。
    (この関数は変更なし)
    """
    suggestions: List[str] = []
    error_str = " ".join(errors).lower()

    if provider_name == 'ollama' and ('not found' in error_str or '404' in error_str or 'connection' in error_str):
        suggestions.extend([
            "Ollamaサーバーが起動しているか確認してください: `ollama serve`",
            "使用したいモデルがダウンロードされているか確認してください: `ollama pull <model_name>`",
            "利用可能なモデルを一覧表示して確認してください: `ollama list`",
        ])

    if 'api' in error_str and 'key' in error_str:
        suggestions.append(f"プロバイダー '{provider_name}' のAPIキーが `.env` ファイルに正しく設定されているか確認してください。")

    if 'timeout' in error_str:
        suggestions.append("処理がタイムアウトしました。より性能の高いモデルや、複雑性を下げるモード (`--mode efficient`) を試してください。")

    suggestions.extend([
        "別のプロバイダー（例: openai, claude）を試してください。",
        "シンプルなモードで再度実行してみてください: `--mode simple`",
        "詳細なログを出力して問題の原因を調査してください: `LOG_LEVEL=DEBUG python ...`",
    ])

    return list(dict.fromkeys(suggestions))