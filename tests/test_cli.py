# /tests/test_cli.py

import pytest
import sys
from unittest.mock import patch, AsyncMock, MagicMock

from cli.main import main as cli_main
from llm_api.utils.helper_functions import read_from_pipe_or_file

@pytest.mark.asyncio
async def test_read_from_pipe_or_file():
    """パイプやファイルからの読み込みをテスト"""
    # Simulate piped input
    with patch('sys.stdin.isatty', return_value=False):
        with patch('sys.stdin.read', return_value='piped input'):
            assert await read_from_pipe_or_file(None, None) == 'piped input'

    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    # aiofiles.openを正しく非同期でモックする
    mock_async_file = MagicMock()
    # .read()自体を非同期モックにする
    mock_async_file.read = AsyncMock(return_value='file input')
    
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_async_file

    with patch('sys.stdin.isatty', return_value=True):
        with patch('aiofiles.open', return_value=mock_context_manager) as m:
            assert await read_from_pipe_or_file(None, 'dummy.txt') == 'file input'
            m.assert_called_once_with('dummy.txt', mode='r', encoding='utf-8')
        
        assert await read_from_pipe_or_file('arg input', None) == 'arg input'
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

@pytest.mark.asyncio
async def test_cli_health_check():
    """--health-checkがCommandRunnerを呼び出すことをテストする。"""
    with patch('cli.command_runner.CLICommandRunner.run_health_check', new_callable=AsyncMock) as mock_health:
        mock_health.return_value = {}
        test_args = ["fetch_llm_v2.py", "--health-check", "--provider", "ollama"]
        with patch.object(sys, 'argv', test_args):
            await cli_main()
            mock_health.assert_awaited_once_with("ollama")

@pytest.mark.asyncio
@patch('cli.handler.MetaIntelligenceCLIHandler.process_request', new_callable=AsyncMock)
async def test_cli_main_flow(mock_process):
    """CLIのメインフローが正しく実行されるかをテストする。"""
    mock_process.return_value = {"text": "Success"}

    test_args = ["fetch_llm_v2.py", "--provider", "openai", "--prompt", "Test prompt"]
    with patch.object(sys, 'argv', test_args):
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # 標準入力の競合を避けるためのパッチを適用
        with patch('sys.stdin.isatty', return_value=True):
            await cli_main()
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    mock_process.assert_awaited_once()
    provider_arg = mock_process.await_args[0][0]
    prompt_arg = mock_process.await_args[0][1]
    assert provider_arg == "openai"
    assert prompt_arg == "Test prompt"