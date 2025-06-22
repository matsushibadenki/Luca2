# /tests/test_rag.py
# タイトル: RAG (Retrieval-Augmented Generation) System Tests
# 役割: ナレッジベース、リトリーバー、RAGマネージャーの動作を検証する。

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# テスト対象モジュール
from llm_api.rag.knowledge_base import KnowledgeBase
from llm_api.rag.retriever import Retriever
from llm_api.rag.manager import RAGManager
from llm_api.providers.base import LLMProvider

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.fixture
def temp_kb_file(tmp_path):
    """テスト用のナレッジベースファイルを作成するフィクスチャ"""
    file_path = tmp_path / "test_kb.txt"
    file_path.write_text("This is a test document about RAG. RAG enhances LLMs with external knowledge.")
    return file_path

class TestKnowledgeBase:
    """KnowledgeBaseクラスのテストスイート"""

    @patch('llm_api.rag.knowledge_base.FAISS')
    @patch('llm_api.rag.knowledge_base.HuggingFaceEmbeddings')
    def test_load_documents_and_create_vector_store(self, mock_embeddings, mock_faiss, temp_kb_file):
        """ドキュメントを読み込み、ベクトルストアが作成されるかをテストする。"""
        # モックの設定
        mock_faiss.from_documents.return_value = MagicMock()
        
        kb = KnowledgeBase()
        kb.load_documents(str(temp_kb_file))

        # 検証
        assert mock_embeddings.called
        mock_faiss.from_documents.assert_called_once()
        assert kb.vector_store is not None

    def test_get_retriever(self):
        """Retrieverオブジェクトが正しく取得できるかをテストする。"""
        kb = KnowledgeBase()
        # vector_storeが設定されている状態をシミュレート
        kb.vector_store = MagicMock()
        kb.vector_store.as_retriever.return_value = "retriever_instance"
        
        retriever = kb.get_retriever()
        
        assert retriever == "retriever_instance"
        kb.vector_store.as_retriever.assert_called_with(search_kwargs={'k': 3})

class TestRAGManager:
    """RAGManagerクラスのテストスイート"""

    @pytest.mark.asyncio
    async def test_extract_search_query(self, mock_provider):
        """プロンプトから検索クエリを正しく抽出できるかをテストする。"""
        # モックの設定
        prompt = "What is the capital of Japan in the context of RAG?"
        mock_provider.call.return_value = {"text": "Capital of Japan"}
        
        manager = RAGManager(provider=mock_provider)
        query = await manager._extract_search_query(prompt)
        
        # 検証
        mock_provider.call.assert_awaited_once()
        assert "Capital of Japan" in query

    @pytest.mark.asyncio
    @patch('llm_api.rag.manager.WikipediaLoader')
    async def test_retrieve_from_wikipedia(self, mock_wiki_loader, mock_provider):
        """Wikipediaから情報が検索されるかをテストする。"""
        # モックの設定
        mock_doc = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page_content = "Tokyo is the capital of Japan."
        mock_doc.metadata = {'source': 'test-wiki'}
        mock_wiki_loader.return_value.load.return_value = [mock_doc]
    
        manager = RAGManager(provider=mock_provider, use_wikipedia=True)
        context = await manager._retrieve_from_wikipedia("Capital of Japan")
    
        assert "Tokyo is the capital of Japan" in context

    @pytest.mark.asyncio
    @patch('llm_api.rag.manager.KnowledgeBase')
    async def test_retrieve_from_knowledge_base(self, mock_kb, mock_provider, temp_kb_file):
        """ローカルのナレッジベースから情報が検索されるかをテストする。"""
        # モックの設定
        mock_kb_instance = mock_kb.return_value
        mock_retriever = MagicMock()
        mock_retriever.search.return_value = ["Content from local KB."]
        mock_kb_instance.get_retriever.return_value = mock_retriever
        
        manager = RAGManager(provider=mock_provider, knowledge_base_path=str(temp_kb_file))
        # _retrieve_from_knowledge_baseは直接Retrieverをインスタンス化しないので、
        # Retrieverのモックも用意する
        with patch('llm_api.rag.manager.Retriever', return_value=mock_retriever):
            context = await manager._retrieve_from_knowledge_base("some query")

        # 検証
        mock_kb_instance.load_documents.assert_called_with(str(temp_kb_file))
        mock_retriever.search.assert_called_with("some query")
        assert "Content from local KB" in context

    @pytest.mark.asyncio
    async def test_retrieve_and_augment_prompt(self, mock_provider):
        """検索されたコンテキストでプロンプトが正しく拡張されるかをテストする。"""
        manager = RAGManager(provider=mock_provider, use_wikipedia=True)
        
        original_prompt = "What is RAG?"
        retrieved_context = "RAG stands for Retrieval-Augmented Generation."

        # _retrieve_from_wikipediaメソッドをモック化
        with patch.object(manager, '_retrieve_from_wikipedia', new_callable=AsyncMock) as mock_retrieve:
            mock_retrieve.return_value = retrieved_context
            
            # 検索クエリ抽出もモック化
            with patch.object(manager, '_extract_search_query', new_callable=AsyncMock) as mock_extract:
                mock_extract.return_value = "RAG"
                
                augmented_prompt = await manager.retrieve_and_augment(original_prompt)

                # 検証
                mock_extract.assert_awaited_with(original_prompt)
                mock_retrieve.assert_awaited_with("RAG")
                
                assert "コンテキスト情報" in augmented_prompt
                assert retrieved_context in augmented_prompt
                assert original_prompt in augmented_prompt