

# **予測的統合：LLMにおける生涯記憶と効率的な文脈処理のための神経科学に着想を得たアーキテクチャ**

## **第1章 記憶のボトルネック：長文脈AIにおける現行パラダイムの概観**

大規模言語モデル（LLM）の進化は、人工知能（AI）の能力を飛躍的に向上させたが、同時にその根源的な限界も露呈させた。特に、人間のように長大な文脈を理解し、生涯にわたって知識を蓄積・活用する能力は、依然としてAIが直面する最も困難な課題の一つである。この課題の核心には「記憶のボトルネック」が存在する。本章では、このボトルネックを克服するために開発されてきた主要な技術パラダイムを体系的に概観し、その進歩と未解決の課題を明らかにすることで、新たな解決策の必要性を提示する。

### **1.1 アーキテクチャの進化：二次的計算量の緩和から準線形代替案へ**

LLMの文脈処理能力を制限する根本的な要因は、その基盤となるTransformerアーキテクチャの自己注意（self-attention）メカニズムにある。このメカニズムは、入力シーケンス内のあらゆるトークンペア間の関係性を計算するため、シーケンス長をnとすると、計算量とメモリ消費量が$O(n^2)$で増加する 1。この二次的なスケーリングは、数千トークンを超えるシーケンスの処理を非現実的なものにし、真の長文脈理解への道を阻んできた 11。

この課題に対する第一世代の解決策は、注意メカニズムそのものを効率化することに焦点を当てていた。**Transformer-XL**は、「セグメントレベルの再帰（segment-level recurrence）」と「相対的な位置エンコーディング（relative positional encodings）」を導入した画期的なモデルである 12。固定長のセグメントを独立して処理するのではなく、前のセグメントの隠れ状態をキャッシュし、現在のセグメントを処理する際の文脈として再利用する 14。これにより、単一セグメントの長さを超える効果的な文脈を構築し、再計算を回避することが可能になった。しかし、このアプローチもまた、キャッシュサイズが固定であるという制約を抱え、非常に長い距離にわたる情報の忠実性を維持することに課題を残した 16。

次に登場した**Longformer**は、「スパースアテンション（sparse attention）」という概念を導入し、計算量を線形の$O(n)$に削減した 2。これは、各トークンが局所的な「スライディングウィンドウ」内のトークンと、タスクに関連する特定の「グローバル」トークン（例えば、分類タスクにおける\`\`トークン）にのみ注意を向けるというハイブリッドなアプローチである 18。これにより、数万トークンに及ぶ文書の処理が可能になったが 3、全てのトークンが他の全てのトークンに注意を向けるわけではないため、グローバルトークンによって捉えられない長距離の依存関係を見逃す可能性というトレードオフを内包していた 18。

より抜本的なアプローチとして、注意メカニズムを完全に置き換える非注意（non-attention）アーキテクチャが登場した。特に**状態空間モデル（State-Space Models, SSMs）**、例えば**Mamba**やS4は、古典的な状態空間システムに着想を得た再帰的なメカニズムを用いる 20。これらのモデルは、シーケンス長に対してほぼ線形の計算量と、推論時には一定のメモリ消費で動作するため、極めて長い文脈に対して高い効率を発揮する 4。しかし、一部のベンチマークでは、特定の推論タスクにおいてTransformerベースのモデルに後れを取ることがあり 21、また、固定サイズの再帰状態が「オーバーフロー」する可能性があるなど、独自のメモリ制限に直面することも示されている 4。

### **1.2 記憶の外部化：検索拡張生成（RAG）エコシステム**

アーキテクチャ内部の改良とは異なるアプローチとして、記憶そのものを外部化するパラダイムが台頭した。それが\*\*検索拡張生成（Retrieval-Augmented Generation, RAG）\*\*である 22。RAGは、全ての情報を文脈ウィンドウに押し込むのではなく、外部の知識ベース（データベースや文書群）を活用する 24。モデルは、ユーザの質問に関連する情報を検索し、それを文脈として与えられた上で回答を生成する 26。このアプローチにより、LLMは常に最新のドメイン固有情報にアクセスでき、ハルシネーション（事実に基づかない情報の生成）を抑制し、モデル内部の記憶限界を回避することが可能になる 27。

RAGアーキテクチャは、その登場以来、急速な進化を遂げている 22。

* **Naive RAG**：単純な「検索してから読む（retrieve-then-read）」プロセス。検索品質が低い場合（「大海の一針」問題ならぬ「干し草の中の迷子」問題）や、複数の情報源からの統合を必要とする複雑な質問に対応できないという課題があった 22。  
* **Advanced RAG**：検索前処理（クエリ拡張など）と検索後処理（再ランキング、圧縮など）を導入し、LLMに提供される文脈の質を向上させる 22。  
* **Modular & Agentic RAG**：検索を動的で複数ステップからなるプロセスとして捉える。**Self-RAG**や\*\*Corrective RAG (CRAG)\*\*のようなシステムは、モデル自身が検索結果の質を評価し、検索が不要と判断したり、初期検索が不十分な場合にウェブ検索などの追加アクションを実行したりすることを可能にする 26。これにより、RAGは静的なパイプラインから、知的なエージェント的プロセスへと昇華した。

この進化の最前線にあるのが、人間の認知プロセスに着想を得た**MemoRAG**である 28。MemoRAGは、「軽量だが長距離対応のシステム」と「高コストだが表現力豊かなシステム」からなるデュアルシステムアーキテクチャを特徴とする 30。前者がまず文脈全体を俯瞰してグローバルな記憶サマリーを生成し、タスクが与えられると、このサマリーを用いて「手がかり」となる草稿アンサーを作成する。その後、後者の強力なシステムが、その手がかりを元に必要な情報を精密に検索し、最終的な回答を生成する 32。これは、人間が文書を読む際に、まず全体の大意を掴んでから詳細に目を向けるプロセスを模倣している 33。

### **1.3 統合的認知アーキテクチャへ：モデルへの記憶の組み込み**

外部化とは対照的に、記憶機能をモデルのアーキテクチャ自体に深く統合しようとする研究も進んでいる。このアプローチは、単なるエンジニアリング的な解決策から、より構造化された、脳のような記憶機能を持つシステムの構築へと向かう概念的なシフトを示している。研究者たちは、LLMの記憶を人間の認知アーキテクチャ、すなわち感覚記憶、短期記憶、長期記憶という枠組みで捉え始めている 34。

\*\*Large Memory Model (LM2)\*\*は、この方向性における重要な成果である。LM2は、Transformerアーキテクチャに補助的なメモリモジュールを付加する 36。このモジュールは、クロスアテンションを介して主要な情報フローと相互作用し、LSTMのようなゲーティングメカニズム（入力、忘却、出力ゲート）によって更新される 38。これにより、標準的な注意メカニズムを補完する、書き込み可能な専用の記憶領域が創出され、多段階の推論や長文脈タスクにおける性能を、汎用能力を犠牲にすることなく向上させることに成功している 39。

さらに、神経科学から直接的な着想を得た研究も現れている。IBMの**CAMELoT**と**Larimar**プロジェクトがその代表例である 40。CAMELoTは情報を統合・圧縮する連想記憶として機能し、一方のLarimarは、海馬のアナロジーとして、高速で書き換え可能な「エピソード記憶」として振る舞う 40。これらのモジュールは、既存のLLMにプラグインする形で追加でき、大規模な再トレーニングなしに、事実を迅速に更新したり忘却させたりすることが可能である。

### **1.4 根強い課題：メモリウォールと生涯学習への探求**

これまでの目覚ましい進歩にもかかわらず、いくつかの根源的な課題が依然として解決されていない。第一に、物理的な「**メモリウォール**」の問題である。これは、メモリとプロセッサ間のデータ転送速度がボトルネックとなる現象であり 41、特にTransformerにおける長文脈処理で肥大化するKVキャッシュによって深刻化する 42。KVキャッシュの圧縮、量子化、オフロードといった技術は重要な緩和策ではあるが、根本的な解決には至っていない 44。

第二に、**性能の低下**である。128Kトークンを超える巨大な文脈ウィンドウを持つモデルでさえ、単一の情報を探し出す「干し草の中の針（Needle-in-a-Haystack）」のようなタスクはこなせても、文脈全体にわたる真の理解と複雑な推論が求められるタスクでは、性能が著しく低下することが報告されている 45。これは、文脈長と理解の質が単純に比例しないことを示している。

そして最終的な目標である**生涯学習（lifelong learning）**、すなわちエージェントが「破滅的忘却（catastrophic forgetting）」を起こすことなく新しいデータから継続的に学習する能力の実現は、依然として遠い道のりである 9。ファインチューニングは高コストで、過去の知識を破壊する可能性がある。RAGは新しい知識へのアクセスを提供するが、それをモデルの核となる理解（パラメトリックメモリ）に統合するわけではない 46。真の長期記憶システムは、安定的かつ継続的な知識の統合をサポートしなければならない 47。

これらの動向を俯瞰すると、二つの重要な変化が見て取れる。一つは、**アーキテクチャパラダイムの収束**である。当初は競合していた「コアアーキテクチャの改良（Mambaなど）」「外部化・バイパス（RAGなど）」「認知的増強（LM2、MemoRAGなど）」という三つの潮流が、現在ではハイブリッドな形で融合し始めている。最先端のシステムは、高効率なコア処理パイプライン、知的エージェント的な外部知識アクセス、そして統合された認知的な記憶管理システムを組み合わせる方向へと向かっている。これは、将来の有望なアーキテクチャが、単一のアプローチを選択するのではなく、これらの要素を脳に着想を得た新しい方法で統合するものであることを示唆している。

もう一つの変化は、**「文脈長」から「記憶の持久力」への焦点の移行**である。業界は文脈ウィンドウのサイズ拡大に注力してきたが、研究は、単に長いテキストをメモリ内に保持するだけでは不十分であることを示している 45。真の課題は、情報を時間とともに理解し、推論し、記憶する能力、すなわち「記憶の持久力」である。これは、単一セッションの巨大な文脈ウィンドウから、セッションをまたいで情報を管理し、揮発性の作業記憶と安定した長期記憶を区別するシステムへと、設計思想の転換を促すものである 8。

---

#### **表1：現代の長文脈LLMアーキテクチャの比較分析**

| アーキテクチャ | コアメカニズム | 記憶パラダイム | 計算量 | 主な限界 |
| :---- | :---- | :---- | :---- | :---- |
| **Transformer-XL** | セグメントレベル再帰 | 暗黙的/揮発性キャッシュ | O(N×L2) | キャッシュサイズ制限、長距離での情報劣化 16 |
| **Longformer** | スパースアテンション | 暗黙的/揮発性文脈 | O(N) | スパースパターンによる情報損失の可能性 18 |
| **Mamba/SSM** | 状態空間再帰 | 暗黙的/再帰状態 | O(N) | 固定サイズ状態のオーバーフロー、特定タスクでの性能 4 |
| **Naive RAG** | 外部検索 | 明示的/静的DB | O(N) \+ 検索遅延 | 検索品質への依存、複雑なクエリへの非対応 22 |
| **Agentic RAG** | 自己修正型検索 | 明示的/動的DB | O(N) \+ 複数ステップ遅延 | システムの複雑性、高いレイテンシ 26 |
| **LM2** | ゲート付きメモリモジュール | 明示的/書き込み可能モジュール | O(N) \+ メモリ操作 | アーキテクチャの複雑性、追加パラメータ 49 |
| **MemoRAG** | デュアルシステムによる手がかり生成 | 明示的/グローバルサマリー | O(N) \+ 検索遅延 | 2つのLLMを要する複雑なパイプライン 30 |

---

## **第2章 脳からの青写真：記憶と効率性に関する神経生理学的原理**

AIが直面する記憶の課題を解決するための鍵は、数億年の進化を経て最適化されたシステム、すなわち人間の脳に隠されている可能性がある。本章では、AI研究の世界から神経生理学へと視点を移し、記憶の形成と効率的な情報処理に関する脳の基本原理を、計算論的に解釈可能な形で抽出する。これらの原理は、AIが現在直面している長期記憶と効率性の問題を、脳がいかにして解決してきたかを示しており、第3章で提案する新しいアーキテクチャの生物学的基盤となる。

### **2.1 システムレベルの統合：長期記憶のための海馬と新皮質の対話**

脳は、単一の記憶ストレージを使用しているわけではない。特に宣言的記憶（事実や出来事に関する記憶）については、巧妙な二元システムを採用している 5。

* **海馬（Hippocampus）**：新しい経験（エピソード記憶）を迅速に符号化するための、高速・大容量だが一時的なバッファとして機能する 51。新規情報を素早く取り込むことに特化しているが、恒久的な保存場所としては設計されていない。実際に、海馬の損傷は最近の記憶を障害するが、遠い過去の記憶には影響を与えにくいことが知られている 5。  
* **新皮質（Neocortex）**：構造化された知識（意味記憶）を恒久的に保存するための、広大で分散したリポジトリとして機能する。新皮質は、既存の知識構造を破壊する「破滅的干渉」を避けるために、意図的にゆっくりと学習する 5。新しい情報は、時間をかけて慎重に、高度に組織化された既存の知識ネットワークに統合される 5。

この一時的な海馬の記憶を、恒久的な新皮質の記憶へと変換するプロセスが「**システムレベルの統合（systems consolidation）**」と呼ばれる 5。これは単純なデータ転送ではなく、記憶の再編成プロセスである。この統合を駆動するアルゴリズムが「

**神経リプレイ（neural replay）**」である。主に睡眠中（特に徐波睡眠時）に、海馬は最近の経験に対応する神経活動パターンを、しばしば時間的に圧縮された形で繰り返し再生（リプレイ）する 51。この反復的なリプレイが、新皮質を徐々に「訓練」し、関連する皮質領域間の結合を強化していく。最終的に、海馬を介さずとも安定して想起できる記憶痕跡が新皮質内に形成されるのである 5。このメカニズムは、なぜ睡眠が学習と記憶にとって不可欠なのかを説明している 51。さらに、海馬における神経新生（新しいニューロンの生成）は、古い記憶を新皮質へ移行させ、海馬が新しい情報を獲得し続けるための容量を確保する上で重要な役割を果たすと考えられている 51。

この脳の二元記憶システムは、AIにおける根本的なトレードオフに対するエレガントな解決策を示唆している。AIシステムもまた、新規の情報を素早く捉えるための高い可塑性（学習の速さ）と、既存の知識を安定して保持するための堅牢性を両立させる必要がある。しかし、単一のコンポーネントでこの二つを同時に満たすことは極めて難しい。脳の解決策は、これらの機能を**分離**することであった。海馬は速度と可塑性に、新皮質は安定性と構造に最適化されている。そして、オフラインの統合プロセス（睡眠中のリプレイ）が両者をつなぐ。この生物学的設計思想は、単一の巨大なLLMにあらゆる機能を詰め込もうとする現在のパラダイムに疑問を投げかけ、高速な揮発性エンコーディングと低速な安定した統合を担う、機能的に分離されたモジュールを持つAIアーキテクチャの必要性を示唆している。

### **2.2 効率的処理の原理：予測符号化とスパースな省エネ計算**

皮質機能に関する有力な理論の一つが「**予測符号化（predictive coding）**」である 53。この理論によれば、脳は感覚入力を滝のように受動的に処理しているのではない。むしろ、高次の脳領域が、低次の領域が次に何を感知

*すべきか*を絶えず予測している。

脳が主に処理するのは、この予測と実際の感覚入力との**差分**、すなわち「**予測誤差（prediction error）**」あるいは「驚き（surprise）」である 55。この予測誤差信号だけが、内部モデルを更新するために皮質の階層を上っていく。もし出来事が完全に予測通りであれば、使われる神経リソースは最小限に抑えられる。これは、脳の膨大なエネルギー消費を抑えるための、極めて効率的な戦略である 56。実際、エネルギー効率の最適化という基本原理が、予測符号化のような性質を創発させる可能性があることも示唆されている 7。

この効率性の原理は、「**スパースコーディング（sparse coding）**」と呼ばれる神経活動パターンをもたらす。すなわち、任意の瞬間に活動しているニューロンはごく一部であり、それらが最も重要で予測外の情報を表現している 58。神経信号の伝達がエネルギーコストの大部分を占める脳にとって、活動をスパース（疎）に保つことは不可欠である 56。

この予測符号化の原理は、単なる入力フィルタリングにとどまらない、記憶圧縮の原理としても捉えることができる。我々が記憶を思い出すとき、ビデオのように再生するわけではない。主要な要素とスキーマ的知識に基づいて再構築し、予測可能な詳細を補完している。これは一種の「非可逆圧縮」であり、脳はありふれた予測可能な部分よりも、その出来事に固有の、驚くべき要素、すなわち「予測誤差」をより強く保存する。この洞察は、AIの作業記憶が単にフィルタリングされた入力を保存するのではなく、期待と現実の差分に焦点を当てた、圧縮された経験表現を保存すべきであることを示唆している。これは、長文脈のメモリフットプリントを最小化するための強力な原理となる。

### **2.3 学習の基盤：重み更新メカニズムとしてのシナプス可塑性**

学習と記憶は、物理的にはシナプスレベルで具現化される。二つのニューロンが同時に繰り返し発火すると、それらの間の結合（シナプス）が強化される。この現象は\*\*長期増強（Long-Term Potentiation, LTP）\*\*と呼ばれる 59。逆に、それらの発火が無相関であれば、結合は弱まる（長期抑圧、Long-Term Depression, LTD）。これは「共に発火するニューロンは、共に結線する」というヘブ学習の生物学的基礎である 61。

このプロセスは、人工ニューラルネットワークにおける重み更新の生物学的アナロジーと見なすことができる。NMDA受容体やカルシウムイオン（Ca2+）の流入といった複雑な分子カスケードが、シナプス伝達効率の持続的な変化を引き起こす 62。活動依存的な結合の強化・弱化というこの連合学習の原理は、提案するAIアーキテクチャにおいて、知識構造をいかにして更新すべきかについての重要な示唆を与える 64。

## **第3章 新たな統合：予測的統合モデル（PCM）の構築**

これまでの章で概観したAIの最先端技術と、脳の記憶・効率化メカニズムに関する神経生理学的知見を融合し、本章では全く新しいアーキテクチャ「**予測的統合モデル（Predictive Consolidation Model, PCM）**」を提案する。PCMは、第1章で明らかになった既存アプローチの限界を克服し、第2章で抽出した生物学的原理を計算論的に実装することを目指す。その核心は、人間の記憶システムを模倣した「デュアルメモリシステム」、脳の効率性を再現する「予測フィルタリング」、そして生涯学習を可能にする「オフライン統合」の三つの柱からなる。

---

#### **表2：神経生理学的概念と提案AIコンポーネントの機能的マッピング**

| 神経生理学的概念 | 生物学的機能 | 提案AIアナロジー（PCMコンポーネント） | 実装技術 |
| :---- | :---- | :---- | :---- |
| **海馬** | 新規エピソード経験の高速・揮発性符号化 | 「海馬的」作業記憶（Working Memory） | 再帰/状態空間モデル（Mamba）4 |
| **新皮質** | 意味的知識の低速・安定的保存 | 「新皮質的」長期記憶（Long-Term Memory） | 進化するナレッジグラフ（KG）33 |
| **予測符号化** | 予測誤差の最小化、エネルギー効率化 | 予測フィルター（Predictive Filter） | 蒸留された予測LLM 53 |
| **システム統合/神経リプレイ** | 記憶のオフライン転送と再編成 | オフライン統合エンジン（Consolidation Engine） | LLMエージェント \+ ETLパイプライン 67 |
| **シナプス可塑性** | 活動依存的な結合の強化学習 | ナレッジグラフ更新ルール | ヒューリスティックに基づくリンク重み付け 59 |

---

### **3.1 コア提案：予測フィルタリングとオフライン統合を備えたデュアルメモリシステム**

PCMは、オンラインでのリアルタイム処理とオフラインでのバッチ処理を組み合わせた、ハイブリッドなマルチコンポーネントアーキテクチャである。リアルタイムの文脈処理、長期的な知識貯蔵、そして記憶の統合というタスクを機能的に分離することで、性能と効率の両方を最適化する。このアーキテクチャは、AIシステムが直面する「レイテンシ対網羅性」のトレードオフ、すなわち、高速な応答性と深い情報処理をいかに両立させるかという問題に対する、脳に着想を得た解決策である。

### **3.2 オンライン推論経路：最大効率での文脈処理**

ユーザーとのインタラクション中に稼働するオンライン経路は、低レイテンシでの応答生成を最優先に設計されている。

* **予測フィルター（Predictive Filter）**：長文脈が入力された際の最初の接点となる。これは、小型で高速な、蒸留されたLLMである。その唯一の役割は、入力文脈をチャンク単位で逐次的に読み込み、**次の**チャンクを予測することである。そして、実際の次のチャンクと予測を比較し、その「予測誤差」（例えば、意味的な差分や、極めて予期せぬトークン）を計算する。この予測誤差、すなわち新規で驚きのある情報のみが、後段の処理に渡される。これは、予測符号化の原理を直接的に実装したものであり 7、単純なトークン削除 8 や初期層をフィルターとして利用する手法 43 よりも、意味的な「驚き」に基づいて情報を選択するため、はるかに洗練されている。  
* **「海馬的」作業記憶（"Hippocampal" Working Memory）**：このモジュールは、予測フィルターから送られてくるスパースな予測誤差のストリームを受け取る。これは、現在のセッションの情報処理のために設計された、揮発性で高帯域なメモリである。  
  * **実装**：**Mamba**のような状態空間モデル（SSM）が理想的な候補となる 4。その線形時間計算量とシーケンスモデリングにおける強力な性能は、スパースな予測誤差ストリームを効率的に処理し、長文脈の本質的な情報をインタラクションの間、その再帰状態に保持するのに適している。  
  * **機能**：この作業記憶は、予測誤差信号から現在の対話や文書の「要点」を組み立て、後段の生成モジュールが一貫性のある適切な応答を生成するために必要な、即時的な文脈を提供する。セッションの終了時、その状態はオフラインエンジンによる処理のために一時ストレージに永続化される。

### **3.3 オフライン統合経路：生涯記憶の構築**

システムの長期的な学習能力の心臓部であり、人間の睡眠中の記憶整理に相当するプロセスを担う。このプロセスは、AIにおける「継続学習」の課題、特に破滅的忘却を回避しながら知識を統合するという課題に対する、脳に着想を得た解決策と位置づけられる 9。

* **統合エンジン（Consolidation Engine）**：これは、非同期のオフラインプロセスとして（例えば、システムのアイドル時に）実行されるLLMベースのエージェントである。システムレベルの統合プロセスを直接模倣する 10。  
  * **トリガー**：定期的、あるいは計算リソースが利用可能な時に起動する。  
  * **プロセス（「神経リプレイ」）**：エンジンは、過去の一つまたは複数のセッションから永続化された「海馬的」作業記憶の生の状態を読み込む。そして、強力なLLMの推論能力を用いてこのデータを分析する。そのタスクは以下の通りである。  
    1. **エンティティと関係性の抽出**：新しい人物、場所、概念、そしてそれらの間の関係性を特定する 33。  
    2. **事実の検証と更新**：事実に基づいた記述を特定し、既存の知識との矛盾をチェックする。  
    3. **要約と抽象化**：エピソード的なデータから主要なテーマや出来事を蒸留する。  
* **「新皮質的」長期記憶（"Neocortical" Long-Term Memory）**：エージェントの恒久的で構造化された知識ストアである。  
  * **実装**：進化する\*\*ナレッジグラフ（Knowledge Graph, KG）\*\*が理想的な構造となる 25。単純なベクトルデータベースとは異なり、KGはエンティティをノード、関係性をエッジとして明示的に保存するため、構造化された推論と説明可能性をサポートする 65。  
  * **更新メカニズム**：統合エンジンが、その分析結果に基づいてKGを更新する。新しいエンティティは新しいノードとなり、新しい関係性は重み付けされた新しいエッジとなる。矛盾する情報はフラグを立てるか、信頼度スコアに基づいて更新することができる。繰り返される観測によってエッジの「重み」を増加させることで、LTPを模倣する 71。これにより、継続的かつ非破壊的な学習という、生涯学習における核心的な要件に対応する 9。

### **3.4 統合ワークフロー：システムがクエリに応答する仕組み**

PCMの全体的な動作は、オンラインとオフラインの経路が協調することで実現される。

1. ユーザーからクエリと長文脈が提供される。  
2. **予測フィルター**が文脈を処理し、スパースな予測誤差信号のみを\*\*「海馬的」作業記憶\*\*に送信する。  
3. **「海馬的」作業記憶**は、現在の文脈の要点をまとめた一時的な表現を構築する。  
4. 同時に、クエリを用いて\*\*「新皮質的」KG\*\*から関連する統合済み知識が検索される（これはRAGに似ているが、進化する内部記憶からの検索である点が異なる）。  
5. 「海馬」からの蒸留された文脈と、「新皮質」から検索された知識が結合され、**生成LLM**に供給され、最終的な応答が生成される。  
6. 定期的（オフライン）に、**統合エンジン**が過去のセッションの「海馬」の内容を処理し、その知識を「新皮質」KGに統合する。これにより、システムは次のインタラクションに向けてより賢くなる。

このアーキテクチャは、計算を三つの異なる時間スケールに明確に分離することで、その効率性を実現している。すなわち、（1）**ミリ秒スケール**：予測フィルターと生成器が低レイテンシのインタラクションのためにリアルタイムで動作する。（2）**セッションスケール**：「海馬的」作業記憶が単一の対話やタスクの間、状態を維持する。（3）**セッション横断/生涯スケール**：統合エンジンと「新皮質的」KGが数時間、数日、数週間にわたって動作し、知識を恒久的に統合する。この時間的デカップリングこそが、PCMの鍵である。最も計算コストの高いタスク、すなわち深い分析と知識統合をオフラインに移行させることで、ユーザー向けのレイテンシに影響を与えることなく、システムは瞬時の応答性と長期にわたる深い構造化学習の両方を実現できるのである。

## **第4章 実装、評価、そして今後の展望**

前章で提案した予測的統合モデル（PCM）は、LLMの記憶能力を根本から再構築するための理論的枠組みである。本章では、このアーキテクチャを概念から現実のものへと移行させるための具体的な道筋を示す。実装上の考慮事項、その成功を測定するための新しい評価基準、そしてこのモデルが切り拓く未来のビジョンについて論じる。

### **4.1 アルゴリズム的およびシステムレベルの経路**

PCMの実現には、既存の技術要素を賢明に選択し、それらを協調させるための新しいメカニズムを開発する必要がある。

* **コンポーネントの選択**：  
  * **予測フィルター**：GPT-2や小規模なT5のようなモデルを蒸留し、次チャンク予測タスクに特化してファインチューニングすることで実装可能である。  
  * **「海馬的」作業記憶**：Mamba 4 やBlock-Recurrent Transformer 1 のような、効率的な再帰的アーキテクチャが適している。  
  * **「新皮質的」長期記憶**：Neo4jのようなグラフデータベースや、カスタムのインメモリグラフ構造が考えられる。ノードの埋め込みベクトルに対する類似性検索とグラフ探索アルゴリズムを介してアクセスする 70。  
  * **統合エンジン**：GPT-4やClaude 3のような最先端モデルを基盤とし、KGを操作するためのツールアクセス権を持つ強力なエージェントとして構築する 67。  
* **開発すべき主要メカニズム**：  
  * **予測誤差メトリック**：予測されたテキストチャンクと実際のチャンク間の意味的な「驚き」を定量化する、頑健な手法の定義が不可欠である。  
  * **統合ヒューリスティクス**：統合エンジンが、何を長期記憶に保存する価値があると判断し、矛盾をどのように解決し、関係性をどう重み付けするかを決定するためのルールセットの開発が鍵となる。これは、AIエージェントの記憶管理に関する研究から着想を得ることができる 10。  
  * **スケジューリング**：システム負荷に基づいてオフラインの統合プロセスをインテリジェントに管理するスケジューラの開発が必要である。

### **4.2 認知的AIのための新しいベンチマーク：真に重要な能力の測定**

PCMのようなシステムの有効性を評価するためには、既存のベンチマークでは不十分である。

* **既存ベンチマークの不備**：「干し草の中の針（Needle-in-a-Haystack）」のようなパスキー検索タスク 21 や、静的なQAデータセットは、静的な文脈からの情報検索能力をテストするものであり、記憶の形成、進化、あるいは長期にわたる推論能力を測定するものではない。  
* **「生涯学習」ベンチマークの提案**：記憶のダイナミクスを評価するためには、複数の連続したセッションにわたって展開される、新しい評価スイートが必要である 68。  
  * **セッション1**：物語の中で一連の登場人物と関係性を導入する。  
  * **セッション2**：セッション1の情報を統合しなければ答えられない質問をする。  
  * **セッション3**：セッション1の事実と矛盾する、あるいはそれを更新する新しい出来事を導入する。  
  * **セッション4**：モデルがその知識を正しく更新し、新しい情報に基づいて推論できるか、同時にセッション1の変更されていない事実を記憶しているかをテストする。  
* **評価指標**：成功は、単なる正解率だけでなく、（1）**知識の保持**、（2）**知識更新の忠実性**、そして（3）**進化する情報に基づく推論能力**によって測定されるべきである。これにより、統合プロセスの有効性が直接的に評価される。

### **4.3 結びのビジョン：静的モデルから生涯学習エージェントへ**

予測的統合モデル（PCM）は、現在の巨大で静的な事前学習済みモデルというパラダイムからの根本的な転換を意味する。それは、生物がそうであるように、適応的で、効率的で、自らの経験から継続的に学習できるAIシステムへの道筋を示すものである 8。

脳が実証済みの記憶アーキテクチャの機能的アナロジーを実装することで、我々はメモリウォールを、より大きなハードウェアによってだけでなく、より賢く、より効率的な計算によって乗り越えることができる。このアーキテクチャは、真にパーソナライズされたAIアシスタント、何年にもわたって知識を構築する科学的発見エージェント、そしてユーザーと共に真に成長し進化できるシステムへの道を拓く。それは、長年抱かれてきた汎用人工知能（AGI）の約束を果たすための、重要な一歩となるであろう。

## **第5章 統合的考察と補完的アプローチ**

PCMは脳の記憶システムから着想を得た具体的なアーキテクチャだが、LLMの記憶と学習能力を進化させるためのアプローチはこれだけではない。本章では、PCMの概念を補完し、あるいは代替となりうるいくつかの先進的なアイデアを考察し、より広範な視点から次世代AIの可能性を探る。

### **5.1 適応的計算と動的ルーティング**

PCMの予測フィルターは、情報をスパース化することで効率を高めるが、この考え方をさらに進め、タスクの性質に応じて計算リソースを動的に割り当てるアプローチが注目されている。例えば、**Branched RAG**は、クエリの内容に基づいてどのデータソースを検索するかを動的に決定する 26。また、

**AdaptiveLLM**は、コーディング問題の難易度を自動評価し、コストと性能のバランスが最適なLLMを動的に選択するフレームワークを提案している 72。

これらの「適応的計算」の概念は、PCMと強力にシナジーを生み出す可能性がある。予測フィルターが単に予測誤差を計算するだけでなく、その誤差の大きさや種類に応じて、後続の処理経路を動的に切り替える「ルーティング」機能を担うことが考えられる。例えば、予測誤差が小さい（予測通りの）場合は、軽量な応答生成モジュールを使用する。一方、予測誤差が大きい（非常に驚くべき）場合は、より強力で計算コストの高い推論モジュールを起動したり、「新皮質的」KGのより深い探索を行ったりする。これにより、システムは日常的なタスクを極めて低コストで処理しつつ、複雑で新規性の高いタスクにはリソースを集中投下するという、より洗練された効率性を実現できるだろう。

### **5.2 記憶オペレーティングシステム（MemOS）という概念**

個別の記憶コンポーネントを組み合わせるだけでなく、記憶そのものをOSレベルの第一級リソースとして管理するという、より抽象的で統一的なビジョンも提案されている。**MemOS**と名付けられたこの概念は、LLMが利用する多様なメモリ（パラメトリックメモリ、作業記憶としての活性化メモリ、RAGのような外部平文メモリ）の生成、整理、利用、進化に至るライフサイクル全体を管理する統一的な基盤を構築することを目指す 73。

この文脈において、PCMはMemOSという壮大なビジョンを実現するための、具体的で生物学的に妥当な実装の一つと位置づけることができる。PCMの「海馬的」作業記憶と「新皮質的」長期記憶は、MemOSが管理すべき異なる種類のメモリリソースに相当し、予測フィルターと統合エンジンは、MemOSが担うべきメモリの整理・統合・利用のプロセスを具体化したものと言える。将来的には、PCMのような複数の特化型メモリモジュールが、MemOSのような上位の管理システムの下で協調動作する、より複雑で階層的な認知アーキテクチャが生まれるかもしれない 54。

### **5.3 創発する内部状態の管理：準自己認識への道**

高度な記憶システムは、単なる情報格納庫にとどまらず、モデルの内部状態の一貫性を維持しようとする、より高次の能力を創発させる可能性がある。近年の研究では、LLMが翻訳タスクにおいて、明示的な指示なしに文体や文脈の一貫性を保とうとする「**準自己認識（quasi-self-awareness）**」とも呼べる振る舞いを見せることが報告されている 76。これは、モデルが自身の過去の出力を暗黙的に記憶し、それを参照して現在の生成を調整していることを示唆している。

この洞察は、PCMの統合エンジンが持つべき機能に新たな示唆を与える。統合エンジンは、単に事実をKGに書き込むだけでなく、システム全体の応答スタイル、ペルソナ、あるいは過去の推論プロセスといった、より抽象的な「自己の状態」をモデル化し、維持する役割を担うべきかもしれない。このような自己参照的な記憶メカニズムは、AIがより一貫性のある、信頼できる、そして長期的に安定した対話パートナーへと進化するための鍵となるだろう。

これらの補完的アプローチは、LLMの記憶能力の未来が、単一の技術的ブレークスルーによってではなく、多様なアイデアの有機的な統合によって形作られることを示唆している。適応的な計算、統一的なメモリ管理、そして自己参照的な内部モデルといった概念を、PCMのような脳に着想を得たアーキテクチャに組み込むことで、我々は静的な情報処理ツールから、真に学習し、成長し、進化する知的エージェントへとAIを昇華させることができるだろう。

#### **引用文献**

1. Compact Recurrent Transformer with Persistent Memory \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.00929v1](https://arxiv.org/html/2505.00929v1)  
2. \[2004.05150\] Longformer: The Long-Document Transformer, 6月 15, 2025にアクセス、 [https://ar5iv.labs.arxiv.org/html/2004.05150](https://ar5iv.labs.arxiv.org/html/2004.05150)  
3. arXiv:2004.05150v2 \[cs.CL\] 2 Dec 2020, 6月 15, 2025にアクセス、 [https://arxiv.org/pdf/2004.05150](https://arxiv.org/pdf/2004.05150)  
4. Overflow Prevention Enhances Long-Context Recurrent LLMs \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.07793v1](https://arxiv.org/html/2505.07793v1)  
5. Memory Consolidation \- PMC, 6月 15, 2025にアクセス、 [https://pmc.ncbi.nlm.nih.gov/articles/PMC4526749/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4526749/)  
6. The hippocampus is necessary for the consolidation of a task that does not require the hippocampus for initial learning \- PMC, 6月 15, 2025にアクセス、 [https://pmc.ncbi.nlm.nih.gov/articles/PMC6791729/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6791729/)  
7. Energy optimization induces predictive-coding properties in a multi ..., 6月 15, 2025にアクセス、 [https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013112](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013112)  
8. Thus Spake Long-Context Large Language Model \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2502.17129v1](https://arxiv.org/html/2502.17129v1)  
9. The Future of Continual Learning in the Era of Foundation Models: Three Key Directions \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2506.03320v1](https://arxiv.org/html/2506.03320v1)  
10. Rethinking Memory in AI: Taxonomy, Operations, Topics, and Future Directions \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.00675v1](https://arxiv.org/html/2505.00675v1)  
11. Longformer in Deep Learning | GeeksforGeeks, 6月 15, 2025にアクセス、 [https://www.geeksforgeeks.org/longformer/](https://www.geeksforgeeks.org/longformer/)  
12. Transformer-XL: Long-Range Dependencies | Ultralytics, 6月 15, 2025にアクセス、 [https://www.ultralytics.com/glossary/transformer-xl](https://www.ultralytics.com/glossary/transformer-xl)  
13. Transformer-XL for PyTorch \- NVIDIA NGC, 6月 15, 2025にアクセス、 [https://catalog.ngc.nvidia.com/orgs/nvidia/resources/transformerxl\_for\_pytorch](https://catalog.ngc.nvidia.com/orgs/nvidia/resources/transformerxl_for_pytorch)  
14. Understanding Transformer-XL \- Scaler Topics, 6月 15, 2025にアクセス、 [https://www.scaler.com/topics/transformer-xl/](https://www.scaler.com/topics/transformer-xl/)  
15. Longer-term dependency learning using Transformers-XL on SQuAD 2.0 \- Stanford University, 6月 15, 2025にアクセス、 [https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1214/reports/final\_reports/report194.pdf](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1214/reports/final_reports/report194.pdf)  
16. Transformer-XL Architecture For Question Answering \- Stanford University, 6月 15, 2025にアクセス、 [https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1224/reports/default\_116823678.pdf](https://web.stanford.edu/class/archive/cs/cs224n/cs224n.1224/reports/default_116823678.pdf)  
17. Day 31: Longformer \- Efficient Attention Mechanism for Long Documents \- DEV Community, 6月 15, 2025にアクセス、 [https://dev.to/nareshnishad/day-31-longformer-efficient-attention-mechanism-for-long-documents-475j](https://dev.to/nareshnishad/day-31-longformer-efficient-attention-mechanism-for-long-documents-475j)  
18. Exploring Longformer \- Scaler Topics, 6月 15, 2025にアクセス、 [https://www.scaler.com/topics/nlp/longformer/](https://www.scaler.com/topics/nlp/longformer/)  
19. Longformer \- Hugging Face, 6月 15, 2025にアクセス、 [https://huggingface.co/docs/transformers/model\_doc/longformer](https://huggingface.co/docs/transformers/model_doc/longformer)  
20. Breaking Quadratic Barriers: A Non-Attention LLM for Ultra-Long Context Horizons \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2506.01963v1](https://arxiv.org/html/2506.01963v1)  
21. LongICLBench: Long-context LLMs Struggle with Long In-context Learning \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2404.02060v3](https://arxiv.org/html/2404.02060v3)  
22. Retrieval Augmented Generation (RAG) for LLMs | Prompt ..., 6月 15, 2025にアクセス、 [https://www.promptingguide.ai/research/rag](https://www.promptingguide.ai/research/rag)  
23. A Comprehensive Review of Retrieval-Augmented Generation (RAG): Key Challenges and Future Directions \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/pdf/2410.12837?](https://arxiv.org/pdf/2410.12837)  
24. Retrieval augmented generation (RAG) \- MongoDB, 6月 15, 2025にアクセス、 [https://www.mongodb.com/resources/basics/artificial-intelligence/retrieval-augmented-generation](https://www.mongodb.com/resources/basics/artificial-intelligence/retrieval-augmented-generation)  
25. Retrieval-augmented generation \- Wikipedia, 6月 15, 2025にアクセス、 [https://en.wikipedia.org/wiki/Retrieval-augmented\_generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)  
26. 8 Retrieval Augmented Generation (RAG) Architectures You Should Know in 2025, 6月 15, 2025にアクセス、 [https://humanloop.com/blog/rag-architectures](https://humanloop.com/blog/rag-architectures)  
27. 15 Pros & Cons of Retrieval Augmented Generation (RAG) \[2025\] \- DigitalDefynd, 6月 15, 2025にアクセス、 [https://digitaldefynd.com/IQ/pros-cons-of-retrieval-augmented-generation/](https://digitaldefynd.com/IQ/pros-cons-of-retrieval-augmented-generation/)  
28. MemoRAG: Revolutionizing Information Processing with Long-Term Memory, 6月 15, 2025にアクセス、 [https://blog.shperling.ai/memorag-revolutionizing-information-processing-with-long-term-memory](https://blog.shperling.ai/memorag-revolutionizing-information-processing-with-long-term-memory)  
29. Empowering Low-Resource Languages: TraSe Architecture for Enhanced Retrieval-Augmented Generation in Bangla \- ACL Anthology, 6月 15, 2025にアクセス、 [https://aclanthology.org/2025.lm4uc-1.2.pdf](https://aclanthology.org/2025.lm4uc-1.2.pdf)  
30. MemoRAG: Moving towards Next-Gen RAG Via Memory-Inspired Knowledge Discovery, 6月 15, 2025にアクセス、 [https://powerdrill.ai/discover/discover-MemoRAG-Moving-towards-cm0ycklv3gi7p014hdb7q7t9u](https://powerdrill.ai/discover/discover-MemoRAG-Moving-towards-cm0ycklv3gi7p014hdb7q7t9u)  
31. MemoRAG: Moving towards Next-Gen RAG Via Memory-Inspired Knowledge Discovery, 6月 15, 2025にアクセス、 [https://powerdrill.ai/discover/discover-MemoRAG-Moving-towards-cm0wx1y3yrbbm019wkfg15gqn](https://powerdrill.ai/discover/discover-MemoRAG-Moving-towards-cm0wx1y3yrbbm019wkfg15gqn)  
32. MemoRAG: Boosting Long Context Processing with Global Memory-Enhanced Retrieval Augmentation \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2409.05591v3](https://arxiv.org/html/2409.05591v3)  
33. playbigdata.ruc.edu.cn, 6月 15, 2025にアクセス、 [http://playbigdata.ruc.edu.cn/dou/publication/2025\_WWW\_Memory.pdf](http://playbigdata.ruc.edu.cn/dou/publication/2025_WWW_Memory.pdf)  
34. Cognitive Memory in Large Language Models \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2504.02441v1](https://arxiv.org/html/2504.02441v1)  
35. LLM Memory Systems \- AI Memory Types & Applications Explained \- Cognee AI, 6月 15, 2025にアクセス、 [https://www.cognee.ai/blog/fundamentals/llm-memory-cognitive-architectures-with-ai](https://www.cognee.ai/blog/fundamentals/llm-memory-cognitive-architectures-with-ai)  
36. LM2: Large Memory Models \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2502.06049v1](https://arxiv.org/html/2502.06049v1)  
37. openreview.net, 6月 15, 2025にアクセス、 [https://openreview.net/pdf?id=SWpv2bRkoj\#:\~:text=To%20address%20these%20limitations%2C%20we,input%20embeddings%20to%20improve%20performance.](https://openreview.net/pdf?id=SWpv2bRkoj#:~:text=To%20address%20these%20limitations%2C%20we,input%20embeddings%20to%20improve%20performance.)  
38. LM2: LARGE MEMORY MODELS FOR LONG ... \- OpenReview, 6月 15, 2025にアクセス、 [https://openreview.net/pdf?id=SWpv2bRkoj](https://openreview.net/pdf?id=SWpv2bRkoj)  
39. \[2502.06049\] LM2: Large Memory Models \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/abs/2502.06049](https://arxiv.org/abs/2502.06049)  
40. How memory augmentation can improve large language models ..., 6月 15, 2025にアクセス、 [https://research.ibm.com/blog/memory-augmented-LLMs](https://research.ibm.com/blog/memory-augmented-LLMs)  
41. Memory Wall Problem Grows With LLMs \- Semiconductor Engineering, 6月 15, 2025にアクセス、 [https://semiengineering.com/memory-wall-problem-grows-with-llms/](https://semiengineering.com/memory-wall-problem-grows-with-llms/)  
42. InfiniPot: Infinite Context Processing on Memory-Constrained LLMs \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2410.01518v1](https://arxiv.org/html/2410.01518v1)  
43. Discovering the Gems in Early Layers: Accelerating Long-Context LLMs with 1000x Input Token Reduction \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2409.17422v1](https://arxiv.org/html/2409.17422v1)  
44. Cognitive Memory in Large Language Models \- Powerdrill, 6月 15, 2025にアクセス、 [https://powerdrill.ai/discover/summary-cognitive-memory-in-large-language-models-cm94p8200enc007ijimgfflah](https://powerdrill.ai/discover/summary-cognitive-memory-in-large-language-models-cm94p8200enc007ijimgfflah)  
45. NoLiMa: Long-Context Evaluation Beyond Literal Matching \- Finally a good benchmark that shows just how bad LLM performance is at long context. Massive drop at just 32k context for all models. \- Reddit, 6月 15, 2025にアクセス、 [https://www.reddit.com/r/LocalLLaMA/comments/1io3hn2/nolima\_longcontext\_evaluation\_beyond\_literal/](https://www.reddit.com/r/LocalLLaMA/comments/1io3hn2/nolima_longcontext_evaluation_beyond_literal/)  
46. A Survey on Memory Mechanisms in the Era of LLMs \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/pdf/2504.15965](https://arxiv.org/pdf/2504.15965)  
47. The Future of Continual Learning in the Era of Foundation Models: Three Key Directions \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/pdf/2506.03320](https://arxiv.org/pdf/2506.03320)  
48. The Role of Memory in LLMs: Persistent Context for Smarter Conversations \- ResearchGate, 6月 15, 2025にアクセス、 [https://www.researchgate.net/publication/385808270\_The\_Role\_of\_Memory\_in\_LLMs\_Persistent\_Context\_for\_Smarter\_Conversations](https://www.researchgate.net/publication/385808270_The_Role_of_Memory_in_LLMs_Persistent_Context_for_Smarter_Conversations)  
49. (PDF) LM2: Large Memory Models \- ResearchGate, 6月 15, 2025にアクセス、 [https://www.researchgate.net/publication/388882930\_LM2\_Large\_Memory\_Models](https://www.researchgate.net/publication/388882930_LM2_Large_Memory_Models)  
50. Memory consolidation \- PubMed, 6月 15, 2025にアクセス、 [https://pubmed.ncbi.nlm.nih.gov/26238360/](https://pubmed.ncbi.nlm.nih.gov/26238360/)  
51. 記憶固定化 \- 脳科学辞典, 6月 15, 2025にアクセス、 [https://bsd.neuroinf.jp/wiki/%E8%A8%98%E6%86%B6%E5%9B%BA%E5%AE%9A%E5%8C%96](https://bsd.neuroinf.jp/wiki/%E8%A8%98%E6%86%B6%E5%9B%BA%E5%AE%9A%E5%8C%96)  
52. ミニ特集に寄せて 神経細胞の同期発火と行動, 6月 15, 2025にアクセス、 [https://www.biophys.jp/dl/journal/47-6.pdf](https://www.biophys.jp/dl/journal/47-6.pdf)  
53. I Think, Therefore I Hallucinate: Minds, Machines, and the Art of Being Wrong \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2503.05806v1](https://arxiv.org/html/2503.05806v1)  
54. Neural Brain: A Neuroscience-inspired Framework for Embodied Agents \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.07634v2](https://arxiv.org/html/2505.07634v2)  
55. A Survey on Brain-inspired Deep Learning via Predictive Coding \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2308.07870v2](https://arxiv.org/html/2308.07870v2)  
56. Energy-efficient neural information processing in individual neurons and neuronal networks \- Bohrium, 6月 15, 2025にアクセス、 [https://www.bohrium.com/paper-details/energy-efficient-neural-information-processing-in-individual-neurons-and-neuronal-networks/813107351342022656-6481](https://www.bohrium.com/paper-details/energy-efficient-neural-information-processing-in-individual-neurons-and-neuronal-networks/813107351342022656-6481)  
57. 感覚系のエネルギー効率 \- 感覚情報処理における神経エネルギー効率の原理、スパースコーディング、効率的符号化仮説、代謝コストと情報処理のトレードオフ、および省エネルギー適応について学ぶ。 | Flashcards World, 6月 15, 2025にアクセス、 [https://flashcards.world/flashcards/sets/77b0bec4-1407-44bd-97e2-5c954eb29c04/](https://flashcards.world/flashcards/sets/77b0bec4-1407-44bd-97e2-5c954eb29c04/)  
58. 報酬予測誤差神経は報酬の効率的符号化を実現する｜えぬ \- note, 6月 15, 2025にアクセス、 [https://note.com/baribio91/n/n7b7cbf3fc9eb](https://note.com/baribio91/n/n7b7cbf3fc9eb)  
59. 長期増強 \- Wikipedia, 6月 15, 2025にアクセス、 [https://ja.wikipedia.org/wiki/%E9%95%B7%E6%9C%9F%E5%A2%97%E5%BC%B7](https://ja.wikipedia.org/wiki/%E9%95%B7%E6%9C%9F%E5%A2%97%E5%BC%B7)  
60. Physiological significance of long-term potentiation \- PubMed, 6月 15, 2025にアクセス、 [https://pubmed.ncbi.nlm.nih.gov/1323510/](https://pubmed.ncbi.nlm.nih.gov/1323510/)  
61. Long-term synaptic potentiation \- PubMed, 6月 15, 2025にアクセス、 [https://pubmed.ncbi.nlm.nih.gov/2903551/](https://pubmed.ncbi.nlm.nih.gov/2903551/)  
62. Long-Term Plasticity of Neurotransmitter Release: Emerging ..., 6月 15, 2025にアクセス、 [https://pmc.ncbi.nlm.nih.gov/articles/PMC6238218/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6238218/)  
63. シナプスにおける2つのタイプの長期増強が前帯状回において共存し不安と慢性疼痛との相互作用を形成する, 6月 15, 2025にアクセス、 [http://first.lifesciencedb.jp/archives/9731](http://first.lifesciencedb.jp/archives/9731)  
64. 学習・記憶におけるシナプス可塑性の分子機構, 6月 15, 2025にアクセス、 [https://www.jbsoc.or.jp/seika/wp-content/uploads/2013/05/83-11-03.pdf](https://www.jbsoc.or.jp/seika/wp-content/uploads/2013/05/83-11-03.pdf)  
65. From Symbolic to Neural and Back: Exploring Knowledge Graph–Large Language Model Synergies \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2506.09566v1](https://arxiv.org/html/2506.09566v1)  
66. Language Modeling Is Compression \- arXiv, 6月 15, 2025にアクセス、 [http://arxiv.org/pdf/2309.10668](http://arxiv.org/pdf/2309.10668)  
67. A Survey of Large Language Model Empowered Agents for Recommendation and Search: Towards Next-Generation Information Retrieval \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2503.05659v1](https://arxiv.org/html/2503.05659v1)  
68. Task-Core Memory Management and Consolidation for Long-term Continual Learning, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.09952v1](https://arxiv.org/html/2505.09952v1)  
69. CLAP4CLIP: Continual Learning with Probabilistic Finetuning for Vision-Language Models, 6月 15, 2025にアクセス、 [https://neurips.cc/virtual/2024/poster/93449](https://neurips.cc/virtual/2024/poster/93449)  
70. Injecting Knowledge Graphs into Large Language Models \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2505.07554v1](https://arxiv.org/html/2505.07554v1)  
71. 記憶形成のメカニズム：分子・細胞認知学の展開, 6月 15, 2025にアクセス、 [https://www.jbsoc.or.jp/seika/wp-content/uploads/2013/05/83-02-03.pdf](https://www.jbsoc.or.jp/seika/wp-content/uploads/2013/05/83-02-03.pdf)  
72. AdaptiveLLM: A Framework for Selecting Optimal Cost-Efficient LLM for Code-Generation Based on CoT Length \- arXiv, 6月 15, 2025にアクセス、 [https://arxiv.org/html/2506.10525v1](https://arxiv.org/html/2506.10525v1)  
73. MemOS: An Operating System for Memory-Augmented Generation (MAG) in Large Language Models (Short Version) \- arXiv, 6月 15, 2025にアクセス、 [http://arxiv.org/pdf/2505.22101](http://arxiv.org/pdf/2505.22101)  
74. Structural knowledge: from brain to artificial intelligence \- ResearchGate, 6月 15, 2025にアクセス、 [https://www.researchgate.net/publication/392404945\_Structural\_knowledge\_from\_brain\_to\_artificial\_intelligence](https://www.researchgate.net/publication/392404945_Structural_knowledge_from_brain_to_artificial_intelligence)  
75. Advances and Challenges in Foundation Agents \- Rivista AI, 6月 15, 2025にアクセス、 [https://www.rivista.ai/wp-content/uploads/2025/06/2504.01990v1.pdf](https://www.rivista.ai/wp-content/uploads/2025/06/2504.01990v1.pdf)  
76. The Paradox of Poetic Intent in Back-Translation: Evaluating the ..., 6月 15, 2025にアクセス、 [https://arxiv.org/pdf/2504.16286](https://arxiv.org/pdf/2504.16286)