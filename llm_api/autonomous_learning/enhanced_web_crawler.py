# /llm_api/autonomous_learning/enhanced_web_crawler.py
"""
Enhanced Web Crawler with JavaScript Rendering Support
JavaScript実行・レンダリング対応の拡張Web巡回システム

このシステムは現代的なWebサイト（SPA、動的コンテンツ）に対応し、
実際のブラウザと同等の環境でコンテンツを取得・分析します。
"""

import asyncio
import logging
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import base64
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class RenderingMethod(Enum):
    """レンダリング方法"""
    STATIC_HTML = "static_html"           # 基本HTML取得
    PLAYWRIGHT = "playwright"             # Playwright使用
    SELENIUM = "selenium"                 # Selenium使用  
    PUPPETEER = "puppeteer"              # Puppeteer使用
    HEADLESS_CHROME = "headless_chrome"   # ヘッドレスChrome

class PageLoadStrategy(Enum):
    """ページ読み込み戦略"""
    IMMEDIATE = "immediate"               # 即座に取得
    DOM_LOADED = "dom_loaded"            # DOM読み込み完了後
    FULL_LOADED = "full_loaded"          # 全リソース読み込み完了後
    NETWORK_IDLE = "network_idle"        # ネットワーク停止後
    CUSTOM_WAIT = "custom_wait"          # カスタム待機条件

@dataclass
class RenderingConfig:
    """レンダリング設定"""
    method: RenderingMethod = RenderingMethod.PLAYWRIGHT
    load_strategy: PageLoadStrategy = PageLoadStrategy.NETWORK_IDLE
    timeout: int = 30000  # ミリ秒
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "MetaIntelligence-Bot/2.1 (Autonomous Learning System)"
    enable_javascript: bool = True
    enable_images: bool = False  # 高速化のため画像を無効化
    enable_css: bool = True
    wait_for_selector: Optional[str] = None
    custom_wait_time: int = 5000  # ミリ秒
    max_scroll_attempts: int = 3  # 遅延読み込み対応

@dataclass
class EnhancedWebContent:
    """拡張Webコンテンツ"""
    url: str
    final_url: str  # リダイレクト後のURL
    title: str
    rendered_content: str  # レンダリング後のコンテンツ
    raw_html: str  # 生のHTML
    text_content: str  # テキストのみ
    metadata: Dict[str, Any]
    page_metrics: Dict[str, Any]  # パフォーマンス指標
    screenshots: List[str] = field(default_factory=list)  # Base64エンコード画像
    network_requests: List[Dict[str, Any]] = field(default_factory=list)
    console_logs: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    rendering_time: float = 0.0
    total_size: int = 0

class PlaywrightRenderer:
    """Playwright使用のレンダリングエンジン"""
    
    def __init__(self, config: RenderingConfig):
        self.config = config
        self.browser: Any = None # Optional[Browser]
        self.context: Any = None # Optional[BrowserContext]
        self.playwright: Any = None # Optional[Playwright]
        
    async def initialize(self) -> bool:
        """ブラウザの初期化"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # ブラウザ起動オプション
            launch_options = {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor"
                ]
            }
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # コンテキスト作成
            context_options = {
                "viewport": {
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height
                },
                "user_agent": self.config.user_agent,
                "java_script_enabled": self.config.enable_javascript,
                "ignore_https_errors": True
            }
            
            # リソース読み込み最適化
            if not self.config.enable_images:
                context_options["route"] = self._block_images
            
            self.context = await self.browser.new_context(**context_options)
            
            logger.info("Playwrightブラウザ初期化完了")
            return True
            
        except ImportError:
            logger.error("Playwrightがインストールされていません: pip install playwright && playwright install")
            return False
        except Exception as e:
            logger.error(f"Playwrightブラウザ初期化エラー: {e}")
            return False
    
    async def _block_images(self, route: Any): # `route` should be of type Route from playwright
        """画像ブロック（高速化）"""
        if route.request.resource_type in ["image", "media"]:
            await route.abort()
        else:
            await route.continue_()
    
    async def render_page(self, url: str) -> Optional[EnhancedWebContent]:
        """ページのレンダリング"""
        if not self.browser or not self.context:
            if not await self.initialize():
                return None
        
        page: Any = None # Page from playwright
        start_time = time.time()
        
        try:
            page = await self.context.new_page()
            
            # ネットワークリクエストの監視
            network_requests: List[Dict[str, Any]] = []
            console_logs: List[Dict[str, Any]] = []
            errors: List[str] = []
            
            async def handle_request(request: Any): # `request` should be of type Request
                network_requests.append({
                    "url": request.url,
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "timestamp": time.time()
                })
            
            async def handle_console(msg: Any): # `msg` should be of type ConsoleMessage
                console_logs.append({
                    "type": msg.type,
                    "text": msg.text,
                    "timestamp": time.time()
                })
            
            async def handle_error(error: Any): # `error` should be of type Error
                errors.append(str(error))
            
            page.on("request", handle_request)
            page.on("console", handle_console)
            page.on("pageerror", handle_error)
            
            # ページ読み込み
            await page.goto(url, timeout=self.config.timeout, wait_until="domcontentloaded")
            
            # 読み込み戦略に基づく待機
            await self._wait_for_content(page)
            
            # 遅延読み込みコンテンツの取得
            if self.config.max_scroll_attempts > 0:
                await self._handle_lazy_loading(page)
            
            # コンテンツ取得
            title = await page.title()
            raw_html = await page.content()
            text_content = await page.inner_text("body")
            final_url = page.url
            
            # メタデータ取得
            metadata = await self._extract_metadata(page)
            
            # パフォーマンス指標
            page_metrics = await self._get_performance_metrics(page)
            
            # スクリーンショット（オプション）
            screenshots: List[str] = []
            try:
                screenshot = await page.screenshot(type="png", full_page=True)
                screenshots.append(base64.b64encode(screenshot).decode())
            except Exception as e:
                logger.warning(f"スクリーンショット取得失敗: {e}")
            
            rendering_time = time.time() - start_time
            
            return EnhancedWebContent(
                url=url,
                final_url=final_url,
                title=title,
                rendered_content=raw_html,
                raw_html=raw_html,
                text_content=text_content,
                metadata=metadata,
                page_metrics=page_metrics,
                screenshots=screenshots,
                network_requests=network_requests,
                console_logs=console_logs,
                errors=errors,
                rendering_time=rendering_time,
                total_size=len(raw_html)
            )
            
        except Exception as e:
            logger.error(f"ページレンダリングエラー ({url}): {e}")
            return None
            
        finally:
            if page:
                await page.close()
    
    async def _wait_for_content(self, page: Any):
        """コンテンツ読み込み待機"""
        try:
            if self.config.load_strategy == PageLoadStrategy.IMMEDIATE:
                # 即座に処理
                pass
            elif self.config.load_strategy == PageLoadStrategy.DOM_LOADED:
                await page.wait_for_load_state("domcontentloaded")
            elif self.config.load_strategy == PageLoadStrategy.FULL_LOADED:
                await page.wait_for_load_state("load")
            elif self.config.load_strategy == PageLoadStrategy.NETWORK_IDLE:
                await page.wait_for_load_state("networkidle")
            elif self.config.load_strategy == PageLoadStrategy.CUSTOM_WAIT:
                if self.config.wait_for_selector:
                    await page.wait_for_selector(self.config.wait_for_selector)
                else:
                    await page.wait_for_timeout(self.config.custom_wait_time)
        except Exception as e:
            logger.warning(f"コンテンツ待機エラー: {e}")
    
    async def _handle_lazy_loading(self, page: Any):
        """遅延読み込みコンテンツの処理"""
        try:
            for attempt in range(self.config.max_scroll_attempts):
                # ページの最下部までスクロール
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # 新しいコンテンツの読み込み待機
                await page.wait_for_timeout(2000)
                
                # 新しいコンテンツが読み込まれたかチェック
                new_height = await page.evaluate("document.body.scrollHeight")
                await page.wait_for_timeout(1000)
                final_height = await page.evaluate("document.body.scrollHeight")
                
                if new_height == final_height:
                    break  # これ以上新しいコンテンツはない
                    
        except Exception as e:
            logger.warning(f"遅延読み込み処理エラー: {e}")
    
    async def _extract_metadata(self, page: Any) -> Dict[str, Any]:
        """メタデータ抽出"""
        try:
            metadata: Dict[str, Any] = {}
            
            # 基本メタタグ
            meta_tags = await page.query_selector_all("meta")
            for tag in meta_tags:
                name = await tag.get_attribute("name")
                property_attr = await tag.get_attribute("property")
                content = await tag.get_attribute("content")
                
                if name and content:
                    metadata[name] = content
                elif property_attr and content:
                    metadata[property_attr] = content
            
            # Open Graph
            og_data: Dict[str, Any] = {}
            for tag in meta_tags:
                property_attr = await tag.get_attribute("property")
                if property_attr and property_attr.startswith("og:"):
                    content = await tag.get_attribute("content")
                    if content:
                        og_data[property_attr] = content
            
            if og_data:
                metadata["open_graph"] = og_data
            
            # JSON-LD構造化データ
            json_ld_scripts = await page.query_selector_all('script[type="application/ld+json"]')
            structured_data: List[Dict[str, Any]] = []
            
            for script in json_ld_scripts:
                try:
                    content = await script.inner_text()
                    data = json.loads(content)
                    structured_data.append(data)
                except Exception: # Catch parsing errors
                    pass
            
            if structured_data:
                metadata["structured_data"] = structured_data
            
            return metadata
            
        except Exception as e:
            logger.warning(f"メタデータ抽出エラー: {e}")
            return {}
    
    async def _get_performance_metrics(self, page: Any) -> Dict[str, Any]:
        """パフォーマンス指標取得"""
        try:
            # Web Vitals and performance metrics
            metrics: Dict[str, Union[int, float]] = await page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        load_time: perfData ? perfData.loadEventEnd - perfData.loadEventStart : 0,
                        dom_ready: perfData ? perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart : 0,
                        first_paint: 0,
                        largest_contentful_paint: 0,
                        cumulative_layout_shift: 0
                    };
                }
            """)
            
            return metrics
            
        except Exception as e:
            logger.warning(f"パフォーマンス指標取得エラー: {e}")
            return {}
    
    async def cleanup(self):
        """リソースクリーンアップ"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"クリーンアップエラー: {e}")

class EnhancedAutonomousWebCrawler:
    """JavaScript対応自律Web巡回システム"""
    
    def __init__(self, provider: Any, web_search_func: Callable[..., Any], rendering_config: Optional[RenderingConfig] = None):
        self.provider = provider
        self.web_search = web_search_func
        self.rendering_config = rendering_config or RenderingConfig()
        
        # レンダリングエンジンの初期化
        if self.rendering_config.method == RenderingMethod.PLAYWRIGHT:
            self.renderer = PlaywrightRenderer(self.rendering_config)
        else:
            # 他のレンダリング方法（Selenium等）は必要に応じて実装
            raise NotImplementedError(f"レンダリング方法 {self.rendering_config.method} は未実装")
        
        # 基本設定
        self.discovered_content: List[Dict[str, Any]] = []
        self.processing_queue: asyncio.Queue[str] = asyncio.Queue()
        self.processed_urls: Set[str] = set()
        
        # SPA対応設定
        self.spa_indicators = [
            "react", "vue", "angular", "backbone", "ember",
            "single-page", "spa", "ajax", "xhr"
        ]
        
        logger.info("拡張自律Web巡回システム初期化完了")
    
    async def initialize(self) -> bool:
        """システム初期化"""
        return await self.renderer.initialize()
    
    async def enhanced_autonomous_learning(self, 
                                         initial_urls: Optional[List[str]] = None,
                                         topics: Optional[List[str]] = None,
                                         session_duration: int = 3600) -> Dict[str, Any]:
        """拡張自律学習セッション"""
        if not await self.initialize():
            return {"error": "レンダリングエンジン初期化失敗"}
        
        session_start = time.time()
        session_results: Dict[str, Any] = {
            "enhanced_content": [],
            "spa_sites_processed": 0,
            "dynamic_content_discovered": 0,
            "total_rendering_time": 0.0,
            "network_efficiency": 0.0
        }
        
        try:
            # 初期URLまたはトピック検索から開始
            if initial_urls:
                for url in initial_urls:
                    await self.processing_queue.put(url)
            elif topics:
                discovered_urls = await self._search_topics_for_urls(topics)
                for url in discovered_urls[:10]:  # 最初の10URL
                    await self.processing_queue.put(url)
            
            processed_count = 0
            max_pages = 20
            
            while (not self.processing_queue.empty() and 
                   time.time() - session_start < session_duration and
                   processed_count < max_pages):
                
                try:
                    url = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                    
                    if url in self.processed_urls:
                        continue
                    
                    self.processed_urls.add(url)
                    
                    # 拡張レンダリングでコンテンツ取得
                    enhanced_content = await self.renderer.render_page(url)
                    
                    if enhanced_content:
                        # コンテンツ分析
                        analysis_result = await self._analyze_enhanced_content(enhanced_content)
                        
                        if analysis_result["interest_score"] > 0.6:
                            self.discovered_content.append({ # Use self.discovered_content here
                                "url": url,
                                "title": enhanced_content.title,
                                "analysis": analysis_result,
                                "rendering_time": enhanced_content.rendering_time,
                                "is_spa": analysis_result.get("is_spa", False),
                                "dynamic_elements": analysis_result.get("dynamic_elements", 0)
                            })
                            
                            # SPA判定
                            if analysis_result.get("is_spa", False):
                                session_results["spa_sites_processed"] += 1
                            
                            # 動的コンテンツ判定
                            if analysis_result.get("dynamic_elements", 0) > 0:
                                session_results["dynamic_content_discovered"] += 1
                            
                            session_results["total_rendering_time"] += enhanced_content.rendering_time
                            
                            # 新しいURLの発見と追加
                            new_urls = await self._extract_interesting_urls(enhanced_content, analysis_result)
                            for new_url in new_urls[:3]:  # 各ページから最大3URL
                                if new_url not in self.processed_urls:
                                    await self.processing_queue.put(new_url)
                    
                    processed_count += 1
                    await asyncio.sleep(1)  # レート制限
                    
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    logger.error(f"URL処理エラー ({url}): {e}")
                    continue
            
            # セッション分析
            session_analysis = await self._analyze_enhanced_session(session_results)
            
            return {
                "session_summary": session_results,
                "session_analysis": session_analysis,
                "pages_processed": processed_count,
                "session_duration": time.time() - session_start,
                "enhanced_features_used": {
                    "javascript_rendering": True,
                    "spa_support": session_results["spa_sites_processed"] > 0,
                    "dynamic_content_extraction": session_results["dynamic_content_discovered"] > 0,
                    "network_monitoring": True
                }
            }
            
        except Exception as e:
            logger.error(f"拡張自律学習セッションエラー: {e}")
            return {"error": str(e)}
            
        finally:
            await self.renderer.cleanup()
    
    async def _search_topics_for_urls(self, topics: List[str]) -> List[str]:
        """トピック検索によるURL発見"""
        urls: List[str] = []
        
        for topic in topics[:3]:  # 最大3トピック
            try:
                search_results = await self.web_search(f"{topic} research papers articles")
                
                if search_results and 'results' in search_results:
                    for result in search_results['results'][:5]:
                        if 'link' in result:
                            urls.append(result['link'])
            except Exception as e:
                logger.error(f"トピック検索エラー ({topic}): {e}")
        
        return urls
    
    async def _analyze_enhanced_content(self, content: EnhancedWebContent) -> Dict[str, Any]:
        """拡張コンテンツ分析"""
        analysis: Dict[str, Any] = {
            "interest_score": 0.0,
            "is_spa": False,
            "dynamic_elements": 0,
            "content_quality": 0.0,
            "technical_depth": 0.0,
            "key_concepts": [],
            "page_type": "static"
        }
        
        try:
            # SPA判定
            analysis["is_spa"] = await self._detect_spa(content)
            
            # 動的要素の検出
            analysis["dynamic_elements"] = await self._count_dynamic_elements(content)
            
            # ページタイプ判定
            if analysis["is_spa"]:
                analysis["page_type"] = "spa"
            elif analysis["dynamic_elements"] > 5:
                analysis["page_type"] = "dynamic"
            else:
                analysis["page_type"] = "static"
            
            # 興味度評価（拡張版）
            analysis["interest_score"] = await self._evaluate_enhanced_interest(content)
            
            # コンテンツ品質評価
            analysis["content_quality"] = await self._assess_content_quality(content)
            
            # 技術的深度評価
            analysis["technical_depth"] = await self._assess_technical_depth(content)
            
            # キーコンセプト抽出
            analysis["key_concepts"] = await self._extract_key_concepts_enhanced(content)
            
        except Exception as e:
            logger.error(f"拡張コンテンツ分析エラー: {e}")
        
        return analysis
    
    async def _detect_spa(self, content: EnhancedWebContent) -> bool:
        """SPA（Single Page Application）の検出"""
        # SPAの特徴を検出
        spa_indicators = 0
        
        # JavaScriptフレームワークの検出
        text_lower = content.text_content.lower()
        for indicator in self.spa_indicators:
            if indicator in text_lower or indicator in content.raw_html.lower():
                spa_indicators += 1
        
        # ネットワークリクエストの分析
        ajax_requests = sum(1 for req in content.network_requests 
                           if req.get("resource_type") in ["xhr", "fetch"])
        
        if ajax_requests > 3:
            spa_indicators += 2
        
        # DOM操作の痕跡
        if "data-react" in content.raw_html or "ng-" in content.raw_html or "v-" in content.raw_html:
            spa_indicators += 2
        
        return spa_indicators >= 3
    
    async def _count_dynamic_elements(self, content: EnhancedWebContent) -> int:
        """動的要素数のカウント"""
        dynamic_count = 0
        
        # AJAXリクエスト
        dynamic_count += len([req for req in content.network_requests 
                             if req.get("resource_type") in ["xhr", "fetch"]])
        
        # JavaScript実行によるDOM変更の痕跡
        if content.console_logs:
            dynamic_count += len([log for log in content.console_logs 
                                 if "react" in log.get("text", "").lower() or 
                                    "vue" in log.get("text", "").lower()])
        
        # 動的属性の検出
        dynamic_attrs = ["data-bind", "ng-", "v-", "data-react", "@click", "@change"]
        for attr in dynamic_attrs:
            dynamic_count += content.raw_html.count(attr)
        
        return min(dynamic_count, 20)  # 最大20に制限
    
    async def _evaluate_enhanced_interest(self, content: EnhancedWebContent) -> float:
        """拡張興味度評価"""
        interest_prompt = f"""
        以下の拡張Webコンテンツについて、AI・技術・研究の観点から興味度を評価してください：

        タイトル: {content.title}
        コンテンツタイプ: {'SPA' if await self._detect_spa(content) else '静的ページ'}
        動的要素数: {await self._count_dynamic_elements(content)}
        ページサイズ: {content.total_size} bytes
        ネットワークリクエスト数: {len(content.network_requests)}
        
        テキストコンテンツ（抜粋）:
        {content.text_content[:1000]}...

        0.0-1.0で評価してください。スコアのみ回答してください。
        """
        
        response = await self.provider.call(interest_prompt, "")
        try:
            return max(0.0, min(1.0, float(response.get("text", "0.0").strip())))
        except ValueError:
            return 0.0
    
    async def _assess_content_quality(self, content: EnhancedWebContent) -> float:
        """コンテンツ品質評価"""
        quality_score = 0.0
        
        # 文字数による品質推定
        text_length = len(content.text_content)
        if text_length > 1000:
            quality_score += 0.3
        elif text_length > 500:
            quality_score += 0.2
        
        # エラーの少なさ
        if len(content.errors) == 0:
            quality_score += 0.2
        elif len(content.errors) < 3:
            quality_score += 0.1
        
        # メタデータの充実度
        if content.metadata:
            quality_score += 0.2
        
        # 構造化データの存在
        if content.metadata.get("structured_data"):
            quality_score += 0.3
        
        return min(1.0, quality_score)
    
    async def _assess_technical_depth(self, content: EnhancedWebContent) -> float:
        """技術的深度評価"""
        tech_keywords = [
            "algorithm", "neural", "machine learning", "AI", "research",
            "methodology", "experiment", "analysis", "model", "framework"
        ]
        
        text_lower = content.text_content.lower()
        keyword_count = sum(1 for keyword in tech_keywords if keyword in text_lower)
        
        return min(1.0, keyword_count / len(tech_keywords))
    
    async def _extract_key_concepts_enhanced(self, content: EnhancedWebContent) -> List[str]:
        """拡張キーコンセプト抽出"""
        concepts_prompt = f"""
        以下の拡張Webコンテンツから主要な概念・技術・理論を抽出してください：

        タイトル: {content.title}
        メタデータ: {content.metadata.get('description', '')}
        テキスト: {content.text_content[:2000]}

        重要な概念を箇条書きで最大7個抽出してください。
        """
        
        response = await self.provider.call(concepts_prompt, "")
        concepts_text = response.get("text", "")
        
        concepts: List[str] = []
        for line in concepts_text.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•')):
                concept = line.lstrip('-•* ').strip()
                if concept and len(concept) > 2:
                    concepts.append(concept)
        
        return concepts[:7]
    
    async def _extract_interesting_urls(self, content: EnhancedWebContent, analysis: Dict[str, Any]) -> List[str]:
        """興味深いURLの抽出"""
        # コンテンツから関連リンクを抽出
        # 実装時にはBeautifulSoupやlxmlを使用してリンクを解析
        return []  # 簡略化
    
    async def _analyze_enhanced_session(self, session_results: Dict[str, Any]) -> Dict[str, Any]:
        """拡張セッション分析"""
        analysis: Dict[str, Any] = {
            "content_diversity": 0.0,
            "spa_coverage": 0.0,
            "dynamic_content_ratio": 0.0,
            "average_rendering_time": 0.0,
            "technical_depth_average": 0.0
        }
        
        enhanced_content = session_results.get("enhanced_content", [])
        
        # Placeholder for actual analysis logic
        if enhanced_content:
            analysis["content_diversity"] = 0.5
            analysis["spa_coverage"] = session_results["spa_sites_processed"] / len(enhanced_content)
            analysis["dynamic_content_ratio"] = session_results["dynamic_content_discovered"] / len(enhanced_content)
            analysis["average_rendering_time"] = session_results["total_rendering_time"] / len(enhanced_content)
            analysis["technical_depth_average"] = sum(c["analysis"].get("technical_depth", 0.0) for c in enhanced_content) / len(enhanced_content)

        return analysis