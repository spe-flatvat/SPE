"""Build individual DRAFT handoff files after actual worker execution, no review dispatch."""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
PIN='9448e5921dba0fc0ff4e294e52b6b1f3ba862330'
REQ='handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-request-20261123/SPE_Work_SQ_Baseline_Contract_Integration_Three_Scenario_Recalculation_Request_20261123.md'
def rd(p):return list(csv.DictReader(p.open()))
def run(root,out):
 v=json.loads((out/'Verification.json').read_text());a=rd(out/'SPE_Three_Scenario_Key_Years_And_Gaps.csv');attr=rd(out/'SPE_Three_Scenario_Change_Attribution.csv');impact=rd(out/'SQ_Change_Candidates_And_Impact.csv')
 lines=['|施策|2030実質GDP|2035実質GDP|2039実質GDP|2055実質GDP|2055名目GDP|2055実質SQ差|SQ割れ年数|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for cid in ['SQ','F','N3']:
  rs={int(x['year']):x for x in a if x['case']==cid};z=rs[2055];vals=[cid]+[f"{float(rs[y]['real_GDP_trn']):.6f}" for y in [2030,2035,2039,2055]]+[f"{float(z[k]):.6f}" for k in ['nominal_GDP_trn','GDP_minus_SQ_trn']]+[z['SQ_below_years']];lines.append('|'+ '|'.join(vals)+'|')
 delta=attr[-1]['F_shared_medical_reference_reconnection'];keyimp='\n'.join(f"- {x['case']}：2055名目差 {float(x['nominal_GDP_minus_reference']):+.9f}兆円、実質差 {float(x['real_GDP_minus_reference']):+.9f}兆円。" for x in impact if int(x['year'])==2055)
 report=f'''# SQ共通計算仕様・F/N3接続・3施策再計算

DRAFT / NON-CANONICAL / OWNER-AUTHORIZED ISOLATED EXECUTION。政策予測の正式採用ではない。

## 実行結果

9経路270年次を実行。本線はSQ/F/N3の90年次、残りは入力接続候補・非既定値の機械的テスト・旧F対照。検証{v['checks']}件、失敗{v['failed']}件。既存2199/13928/8058/15590件PASSは既存対象の証拠として再利用し、新規検証数へ加算していない。

単位は兆円。比較は既存実装の条件付きモデル結果であり、未実装政策を埋めた完全な3政策予測ではない。

{chr(10).join(lines)}

## Stage A：基準と限定候補

SQ_COMPARISON_REFERENCEはCURRENT_REFERENCE_UNCHANGED（SQ_COMMON_ON）。2026実質580/名目600、共通人口122618024、29遷移、LEVEL労働弾性0.65、基調成長1%、現行加算名目式を保持。原文§9人口121500000との相違、旧v5の別人口・労働・気候暦は前回の系列表で保持し、現行値へ数値合わせしていない。初期580/600以外の政策未接続中央値等は生成しない。

実質コア Y=580*A*(L/L2026)^0.65、Aは各年に(1+基調成長−適用リスク)を一回乗算。Ncoreは(1+実質コア成長+入力pi)を乗算し、d=Ncore/Ycore。最終名目は実質GDP*d*(1+価格圧力)。したがって入力piと暗黙デフレーター成長は異なる（加算式ではpi/(1+g)）。Fの政策労働に伴う実質成長差によるdの変化は共通インフレ入力変更ではない。N3の最終価格圧力も別列。

既存キーbase_inflation/oil_inflation_extra/conflict_inflation_extraの意味は、元common_model/exogenous設定・configureのp合成・既存年別イベント定義で確認した。しかし実行式は.02/.02を直書きし、紛争物価にconflict_gdp_lossを参照する。隔離候補では価格式だけを対応するpキーへ接続。既定値では30年次の主要状態が完全一致し、基調インフレ3%・紛争追加インフレ1%という未採用のテスト値では物価経路だけが反応し実質コア/実質リスクは不変。旧式の同じキー変更は無反応だった。これは入力意味論の技術修正候補で、価格規約の採用・全国較正の完了ではない。比較本線には候補を混入していない。

{keyimp}

非既定値は機械的テスト条件であり、根拠ある政策値・GDP差の原因別寄与ではない。SQ医療のキャッシュ済み価格入力はこの候補テストで再初期化していないため、名目条件変更の完全な全施策反実仮想とも呼ばない。

2026オイルは予定と適用を分け、初期GDP適用Falseを維持。2027紛争、2031地震、2029起点3年災害、2028起点隔年気候を変更せず、各年の合計リスクとFのリスク・物価一致を検証。災害・気候はA水準に残る。原文にない回復率・位相・確率はunknownで追加しない。初期オイルONの境界・乗算型価格の前回診断も未採用のまま。これら仕様判断を基準固定の追加ゲートにしていない。

## Stage B/C：共通接続と実際の再計算

Fはf-common-endoflife-finalizationのLATEST_F、N3は前回GDP差分析のBASE_REPLAY（原文既存実装、GI OFF）を実際に再実行。N3の税・年金OFF、追加G/I、税基礎拡大感度、雇用人数等の候補は投入していない。N3の既存75%残余再投資等の未採用仮定は既存入力として残り、正式政策認定していない。家計課税・年金精査の未較正判断も維持。

共通医療の制度パラメータ・財源定義・臨床区分・登録基準を機械照合。Fの医療価格/人口参照は従来F比較用キャッシュを使っていたため、隔離呼出側で既存SQ/N3医療初期化の参照へ接続した。元F経路も30年次再実行して対照化。2055年F実質の接続差は{float(delta):+.12f}兆円。旧SQ_FIXED分母→共通ON分母の差、F医療参照接続差、最終政策経路差は別列である。Fの教育モジュール固有の既存価格入力は保持し、医療共通参照の整備と混同しない。

SQは共通ON経路を実際に再実行し、N3内の固定SQ分母とcore/Y/N/C/I/K/税/労働を全30年次照合した。N3は固定コア・人口・共通SQ状態を入力として、現行の政策会計・ラグ付き課税基礎・消費/投資・財政を再実行した。コア自体の新規推計や全国較正ではない。

Fの外国人材・高齢就労・教育・医療による実際の労働/人口は政策内生差として残す。同じ初期値・共通成長/物価/イベント入力・同じ共通医療基底に接続した条件付きGDP比較は成立した。既存共通施策の未較正パラメータは全て解決済みとしない。FとN3の医療VAT数量/健康労働の実装範囲、教育価格入力、患者自己負担・財源制度による出力差も残るので、完全に対称な政策効果推計や厳密な政策優劣の順位ではない。

N3 GDP差は2055年−44.970845兆円を再現。FのSQ差は+11.312209兆円。基準共通マクロの変更差は0であり、これらをSQデバフ調整の効果と呼ばない。F医療参照接続差は構造整備による変化で、政策の上積み効果ではない。

## 会計範囲・未完了

投資はFの政策投資状態とSQ/N3の更新投資込みで定義が異なる。家計はFの現金DI代理とN3資源DI代理、基金はFの保険料軽減基金とN3年金基金が異なる。税収も実装上の診断代理。Fに全国債務/PBを補完せず、N3の条件付き国地方閉鎖値を横並び全国順位に流用しない。該当比較はN/A。観測された各経路の値は年度表と実行原票に残した。

未完了：SQ原文と現行初期人口/投資促進/税弾性の較正・仕様統合、2026初期ショック、価格規約、災害回復、全国課税基礎、年金コホート/運用益原資、医療VAT数量・健康伝播の左右対称化、完全な全国会計比較。今回の実務改善は、共通入力検査と不活性キー候補を実行可能化し、F医療参照と比較分母を共通化して、3経路90年次を同じ比較表へ再計算できたことである。既存GDPの再現だけを政策開発の進歩と呼んでいない。

次の実行可能な改善対象は、価格キー接続候補を同一入力で全施策に適用した影響試験、医療VAT数量・健康接続の範囲検査、投資/家計/基金列の定義共通化。原文根拠や較正を要する変更は別候補とする。

## 再現・検算引渡し

入力固定Commit `{PIN}`。50超の実読込原本を固定Git objectとサイズ/SHA照合。依存元はFixed_Source_Receipts.json、入れ子依存は各既存Inputs/Dependency_Pins、抽出原本は固定3c77eafc2073fdaba4c129164817d2f57c9421b9の元N3ドラフト。コード・入力原本を変更せず読み込む。

固定成果Commitをcheckoutし、リポジトリrootで以下を実行する。--outdirは空の別ディレクトリを指定。

```bash
python3 handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123/Three_Scenario_Reproduce.py --root . --outdir /tmp/spe-three-replay
python3 handoff/chatgpt-sq-baseline-contract-three-scenario-recalculation-20261123/Finalize_Packet.py --root . --outdir /tmp/spe-three-replay
```

Execution_Log.jsonは各実プロセスのコマンド/終了値/標準出力/標準エラー、Verification.jsonは検証結果。再生成一致はReproduction_Verification.json、事後取得はCustody_Verification.json。パケットManifestは自身・事後保全記録を除外し循環ハッシュを避ける。Claude検算依頼は草案のみで発出・検算・承認を代行していない。

SQ/F/N3原本・共通エンジン・mainは変更なし。正式Acceptance/PR/merge/Canonical化/Freezeなし。RP-023/M19–25 HOLD、RP-024 PENDINGを維持。
'''
 report += "\n## 不足分類と次の実務\n\n|対象|分類|今回の扱い|\n|---|---|---|\n|物価キー不活性・紛争GDPキーの物価参照|共通入力接続の技術不整合候補|既定値不変・非既定値で活性化する隔離候補を実行。比較本線は現行維持|\n|名目加算式と入力pi/暗黙dの乖離|モデル構造・価格規約の選択|原式を保持。乗算規約を採用しない|\n|2026初期イベント・29/30遷移|初期境界の仕様不足|予定/実適用を分離し初期オイルOFF保持|\n|リスク水準の永続性・回復なし|モデル構造・未確定仕様/較正|回復率はunknown|\n|旧v5/現行と原文初期人口・税弾性|別系列・全国較正/仕様不足|同系列へ無表示統合しない|\n|F医療参照と比較分母|呼出側接続・比較契約の不足|共通SQ医療参照への再接続と新旧実行完了|\n|医療VAT/健康・投資/DI/基金/全国財政|部門会計接続・実装分解能の不足|実値を保持し非互換列N/A|\n|税基礎・年金コホート/運用益原資|統計/政策仕様/較正不足|既存精査のunknownを保持|\n"
 (out/'SPE_SQ_Baseline_And_Three_Scenario_Recalculation_Report_DRAFT_20261123.md').write_text(report)
 request='''# Claude独立検算依頼案（未発出）

DRAFT / NON-CANONICAL。Ownerが別途発出するまで検算開始・承認済みと扱わない。

固定成果Commitの当該ディレクトリ個別原本を取得し、Manifestのサイズ/SHA256を自ら照合してください。WorkのPASSをClaude自身の自己検証に転記しないでください。入力固定Commitは9448e5921dba0fc0ff4e294e52b6b1f3ba862330、依存はFixed_Source_Receipts.jsonと既存Inputs/Dependency_Pinsです。抽出元3c77eafc2073fdaba4c129164817d2f57c9421b9も必要です。

報告書の2コマンドで空の別出力先へ実行し、9経路270年次（主比較90年次）・年度CSV・主要状態・差分を独立確認してください。共通コア/加算名目/最終価格圧力式、入力piと暗黙デフレーター、初期580/600と29遷移、scheduled/appliedイベント、同一イベント一回適用、N3の固定SQ分母との一致、F旧医療参照と共通SQ医療参照の接続差を確認してください。非既定値テストは未採用であり、価格キー接続と紛争実質損失が独立しているかを確認してください。

同じ共通医療定義と医療参照が設定されたこと、政策内生の人口/労働/実現価格が差として残ること、F教育固有価格入力・医療VAT/健康の範囲差を検討してください。追加G/I・税/年金OFF・新規雇用仮定の不混入を確認してください。

F/SQ/N3は条件付き既存実装比較です。完全な政策優劣順位としないこと、投資/家計/全国財政/基金の非互換項目がN/Aであること、全国較正・回復・初期境界・年金原資等の未知値を解決済みとしないことも確認対象です。正式採用、共有本体修正、PR/merge、HOLD解除は依頼しません。
'''
 (out/'SPE_Claude_Independent_Recalculation_Request_DRAFT_20261123.md').write_text(request)
 originals=[]
 for name in [REQ,'policies/StatusQuo.md','policies/FreedomPolicies.md','policies/FreedomPolicies_Annex.md','policies/New3linesPolicies.md']:
  b=subprocess.check_output(['git','show',PIN+':'+name],cwd=root);dest=out/'Fixed_Originals'/Path(name).name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(b);originals.append(dict(commit=PIN,path=name,saved=str(dest.relative_to(out)),size=len(b),sha256=hashlib.sha256(b).hexdigest()))
 (out/'Fixed_Original_Policy_Receipts.json').write_text(json.dumps(originals,indent=2)+'\n')
 print(json.dumps(dict(packet='DRAFT_READY_FOR_OWNER_LATER_DISPATCH',originals=len(originals),verification=v['status'])))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--outdir',type=Path,required=True);a=p.parse_args();run(a.root.resolve(),a.outdir.resolve())
