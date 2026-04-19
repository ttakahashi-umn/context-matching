# Requirements Document

## Introduction

本仕様は、**面談の文字起こしテキスト**から、**テンプレで宣言した観点**に沿って情報を抽出し、**人材プロフィールとして保存・参照・更新**できる PoC を対象とする。成功の判定は、**営業の役員**が提示物を見て **「筋がいい」** と評価できることとする。

音声認識（ボイス→テキスト）そのものは本システムの責務外とし、**文字起こし済みテキスト**を入力とする。抽出の具体アルゴリズムやランタイム（オンデバイス優先の合意など）は **設計フェーズ**で決定し、本要件では **利用者や運用者が観察できる振る舞いと境界**に留める。

### (a) 誰のどんな問題か

- **事業・運営側**が収益化の中心であり、そのために **人材側と発注側の双方**に価値が必要になる、という前提がある。
- 本 PoC で直接救うのは、**「人材の文脈が履歴書・定型資料だけでは伝わらない」**という問題の一端である。非定型の面談発話には、職務経歴に載りにくい価値観や暗黙知に近い情報が含まれるが、**入力コストが高く**活用しきれていない。
- **検証の観客**として、**営業の役員**がデモを見て **「筋がいい」** と言えることが最初の合否ラインとする。

### (b) いまの状況

- リポジトリは主にドキュメントと steering のみで、アプリケーションは未着手に近い。
- マッチング、発注側プロフィール、**本番運用を前提としたフルスペックの運営コンソール**、本番レベルの同意・監査は **本仕様の対象外** とする（近親者レベルの PoC。金銭・契約は扱わない）。**最小の PoC UI** は In とする（下記 (c)）。

### (c) 何が変わればよいか

- **人材データベース**として、少なくとも **人材エンティティの保存・更新・参照** ができる。
- **面談のボイス→テキスト済みテキスト** を取り込み、**YAML 等のテンプレ**で宣言した観点に沿って **自動解析により構造化された人材プロフィール**として蓄積できる。
- 推論は **Mac 上のオンデバイス（CoreML を含む Apple 系スタックを優先）** で検討する、というステークホルダー意向がある。具体モデルは設計フェーズで確定する。
- 役員向けの説明には、**最小の PoC UI**（コア業務を画面から辿れること）を **必須** とし、必要に応じて **構造化データのエクスポート、再現可能な実行、読みやすい静的サマリ** などを併用できる。一方で、**本番運用を前提としたフルスペックの運営コンソール**は作らない。

## Boundary Context

- **In scope**: 人材エンティティ；面談セッションと文字起こしテキストの取り込み；YAML 形式を含む **テンプレートによる抽出観点の宣言** とバージョン管理；テンプレに基づく **構造化抽出の実行** と結果の保存；同一入力に対する **再現手順の説明**；**最小 PoC UI**（コア業務の主要フローを画面から実行・閲覧できること）；対象外機能への **明示的な拒否または未提供**。
- **Out of scope**: 発注側・案件側プロフィール；マッチング／ランキング／マッチ理由の自動生成；**本番運用を前提としたフルスペックの運営コンソール**；本番レベルの同意管理・削除権・監査ログの完全実装；SNS・GitHub 等の追加ソースコネクタ；収益・契約・課金。
- **Adjacent expectations**: 文字起こし品質は上流工程に依存する。本システムは **プレーンテキスト（またはプロジェクトで合意した単一のテキスト入力形式）** を受け取れること以外を、文字起こし工程から要求しない。

## Requirements

### Requirement 1: 人材エンティティの識別とライフサイクル

**Objective:** PoC 運用者として、人材を一意に識別し、空の状態から保存できるようにしたい。あとから同一人材を更新できるようにしたい。

#### Acceptance Criteria

1. When PoC 運用者が新規人材の登録を完了する, the Talent Interview Profile PoC shall その人材を一意に参照できる識別子とともに永続化する。
2. When PoC 運用者が既存人材の識別子を指定して参照する, the Talent Interview Profile PoC shall 直近で保存されている人材情報を返す。
3. When PoC 運用者が既存人材の識別子を指定して属性更新を完了する, the Talent Interview Profile PoC shall 更新後の値が以降の参照で観察できる。
4. If 指定された識別子に対応する人材が存在しない, the Talent Interview Profile PoC shall 存在しないことを運用者が判別できる形で示す。
5. The Talent Interview Profile PoC shall 人材ごとに **姓・名**および**読み仮名（姓・名）**を保持し、一覧等で人間可読な表示（例: 姓と名の結合）に利用できる。

### Requirement 2: 面談セッションと文字起こしテキストの取り込み

**Objective:** PoC 運用者として、ある人材に紐づく面談の文字起こしを取り込み、後からそのセッションを識別できるようにしたい。

#### Acceptance Criteria

1. When PoC 運用者が人材識別子と面談の文字起こしテキストを提出する, the Talent Interview Profile PoC shall その内容を当該人材に紐づく面談セッションとして保存する。
2. When PoC 運用者が人材識別子を指定して面談セッション一覧を参照する, the Talent Interview Profile PoC shall 保存済みセッションを時系列または運用者が理解できる順序で返す。
3. If 提出されたテキストが合意した入力形式の制約を満たさない, the Talent Interview Profile PoC shall 受理せず、運用者が修正方針を決められる情報を返す。
4. The Talent Interview Profile PoC shall 各面談セッションを、少なくとも人材識別子とともに一意に参照できる。

### Requirement 3: 抽出テンプレート（YAML）の宣言とバージョン管理

**Objective:** PoC 運用者として、「どの観点を抽出したいか」をテンプレで宣言し、テンプレ更新の履歴を追えるようにしたい。

#### Acceptance Criteria

1. When PoC 運用者が YAML 形式の抽出テンプレートを登録する, the Talent Interview Profile PoC shall そのテンプレをバージョン識別子とともに保存する。
2. When PoC 運用者がテンプレートの一覧または特定バージョンの内容を参照する, the Talent Interview Profile PoC shall 登録済みの定義を返す。
3. If 登録された YAML が構文または必須項目の検証に失敗する, the Talent Interview Profile PoC shall 登録を完了させず、運用者が修正できる情報を返す。
4. The Talent Interview Profile PoC shall 抽出実行がどのテンプレートバージョンに基づいたかを、後から追跡できる形で保持する。

### Requirement 4: 面談テキストからの構造化抽出の実行

**Objective:** PoC 運用者として、登録済みテンプレに従い、面談テキストから構造化された候補フィールドを得たい。

#### Acceptance Criteria

1. When PoC 運用者が人材に紐づく面談セッションとテンプレートバージョンを指定して抽出を実行する, the Talent Interview Profile PoC shall テンプレで宣言された観点に対応する構造化結果を生成する。
2. If 抽出処理が完了できない, the Talent Interview Profile PoC shall 失敗したことを運用者が判別でき、再試行またはデータ修正の判断ができる情報を返す。
3. While 抽出が実行中である, the Talent Interview Profile PoC shall 同一セッションに対する競合する更新が起きないよう、運用者が結果の整合性を判断できる状態を維持する。
4. The Talent Interview Profile PoC shall 生成結果に、どの入力テキストとテンプレートバージョンに基づくかが追跡できる参照情報を含める。

### Requirement 5: 抽出結果の人材プロフィールへの反映

**Objective:** PoC 運用者として、抽出結果を人材プロフィールに取り込み、以降の参照で利用できるようにしたい。

#### Acceptance Criteria

1. When PoC 運用者が抽出結果を人材プロフィールへ反映する操作を完了する, the Talent Interview Profile PoC shall 反映後のプロフィールが人材参照で観察できる。
2. When 同一人物材に対して複数の面談セッションから抽出が行われる, the Talent Interview Profile PoC shall どのセッション由来の情報かを運用者が説明できる形で区別できる。
3. If 反映内容がテンプレで許容されない形式になる, the Talent Interview Profile PoC shall 反映を完了させず、運用者が判断できる情報を返す。
4. The Talent Interview Profile PoC shall プロフィールの変更履歴を、少なくとも「いつ・どのセッション／抽出に基づくか」を追える粒度で保持する。

### Requirement 6: デモの再現性と説明可能性（役員提示）

**Objective:** 営業役員として、同じ前提で再実行でき、判断材料が読み取れるようにしたい。運用者は最小 UI を通じてデモを行えるようにしたい。

#### Acceptance Criteria

1. When PoC 運用者がデモ手順に従い同一入力セットを再適用する, the Talent Interview Profile PoC shall 前回と同じ手順で同じ観察可能な結果に到達できる。
2. When 営業役員が提示物（最小 PoC UI、または構造化データのエクスポート、実行ログ、静的サマリのいずれか）を閲覧する, the Talent Interview Profile PoC shall 抽出観点と根拠となった面談テキストの対応関係が追える説明を提供する。
3. The Talent Interview Profile PoC shall コア業務（人材の登録、面談テキストの取り込み、テンプレート登録、抽出実行、プロフィールの参照および抽出結果の反映）を、**単一の最小 PoC UI** から主要フローとして完遂できる。
4. The Talent Interview Profile PoC shall **本番運用を前提とした多機能な運営コンソール**（テナント管理、複雑な権限モデル、高度なワークフロー自動化など）を提供しない。
5. The Talent Interview Profile PoC shall **人材一覧画面およびテンプレート一覧画面**では登録済みエンティティの **一覧を主表示**とし、新規登録 UI は **登録ボタン操作により画面右からスライドインするパネル**で提供する（一覧の上に登録フォームを常設しない）。

### Requirement 7: 明示的対象外の拒否または未提供

**Objective:** PoC 運用者として、今回のスコープ外の要求にシステムが誤って答えないようにしたい。

#### Acceptance Criteria

1. When PoC 運用者が発注側または案件側エンティティの永続化を要求する, the Talent Interview Profile PoC shall 当該要求を本仕様の対象外として完了させない。
2. When PoC 運用者がマッチング、ランキング、またはマッチ理由の自動生成を要求する, the Talent Interview Profile PoC shall 当該要求を本仕様の対象外として完了させない。
3. When PoC 運用者が本番レベルの同意管理・削除権・監査ログの完全実装のみを単独の完了条件として要求する, the Talent Interview Profile PoC shall 当該要求を本仕様の対象外として扱い、PoC 範囲の説明に誘導する。
4. If 外部の追加ソース（SNS、GitHub 等）からの自動取り込みを要求する, the Talent Interview Profile PoC shall 当該要求を本仕様の対象外として完了させない。
