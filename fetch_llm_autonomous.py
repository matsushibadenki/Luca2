# fetch_llm_autonomous.py
"""
自律学習専用のエントリーポイント
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Corrected import path
from cli.autonomous_learning_cli import main

if __name__ == "__main__":
    asyncio.run(main())