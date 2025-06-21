# /tests/test_cli.py
# タイトル: CLI Test Suite (Refactored for stdin)
# 役割: 標準入力の読み取りエラーを回避する修正を適用。

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import asyncio

from cli.main import main as cli_main

# 修正点: ほとんどのテストで `sys.stdin.isatty` をモックする
@pytest.mark.asyncio
async def test_cli_simple_prompt_v2_mode():
    """V2モード指定時にRequestProcessorがEngineを呼び出すことをテストする。"""
    # 修正: RequestProcessorのprocess_requestをモックする
    with patch('cli.request_processor.RequestProcessor.process_request', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = {"text": "V2 ok", "error": None}
        
        # 修正: stdin.isattyをモックする
        with patch('sys.stdin.isatty', return_value=True):
            test_args = ["fetch_llm_v2.py", "ollama", "Hello", "--mode", "adaptive"]
            with patch.object(sys, 'argv', test_args):
                await cli_main()

        mock_process.assert_awaited_once()
        args, kwargs = mock_process.call_args
        assert args[0] == 'ollama'
        assert args[1] == 'Hello'
        assert kwargs['mode'] == 'adaptive'

@pytest.mark.asyncio
async def test_cli_health_check():
    """--health-checkがCommandRunnerを呼び出すことをテストする。"""
    with patch('cli.command_runner.CLICommandRunner.run_health_check', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {}
        test_args = ["fetch_llm_v2.py", "ollama", "--health-check"]
        with patch.object(sys, 'argv', test_args):
            await cli_main()
        mock_health.assert_awaited_once_with("ollama")