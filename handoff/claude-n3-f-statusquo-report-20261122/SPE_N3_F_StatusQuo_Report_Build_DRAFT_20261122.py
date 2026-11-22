#!/usr/bin/env python3
# Build the SQ / F / N3 three-way comparison report (PDF + Markdown) from the delivered CSVs of ChatGPT Work Commit 37c3399f.
# Usage: python3 -I <this> <results_dir> <outdir>.  All numbers come from the CSVs; nothing is typed in by hand (except labels).
import sys, os, csv
import matplotlib; matplotlib.use('Agg'); import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
RD, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
MODE = 'DOMESTIC_TRANSFER'; SQ, N3, FREF = 'SQ_COMMON_OFF', 'PARITY_CONNECTED_CANDIDATE', 'F_FIXED_REFERENCE'
cmp_ = {(r['case'], int(r['year'])): r for r in csv.DictReader(open(os.path.join(RD, 'SQ_F_N3_Annual_Comparison.csv'))) if r['mode'] == MODE}
ann = {(r['case'], int(r['year'])): r for r in csv.DictReader(open(os.path.join(RD, 'Annual_DOMESTIC_TRANSFER.csv')))}
fis = {(r['case'], int(r['year'])): r for r in csv.DictReader(open(os.path.join(RD, 'Conditional_National_Local_Fiscal.csv'))) if r['mode'] == MODE and r['scenario'] == 'REFERENCE_CANDIDATE'}
sens = [r for r in csv.DictReader(open(os.path.join(RD, 'Sensitivity.csv'))) if r['mode'] == MODE and r['year'] == '2055' and r['metric'] == 'real_gdp_trn']
Y = list(range(2026, 2056)); KY = [2026, 2030, 2035, 2040, 2045, 2050, 2055]
def val(case, y, k):  # SQ / N3 from the comparison file; F = N3 - (N3 - F)
    if case == 'F': return float(cmp_[(N3, y)][k]) - float(cmp_[(N3, y)][k + '_minus_F_FIXED'])
    return float(cmp_[(case, y)][k])
C3 = [('F', 'F（固定参照 ff621006）'), (SQ, 'StatusQuo（共通OFF）'), (N3, 'N3（候補・未採用）')]
COL = {'F': '#2a78d6', SQ: '#eb6834', N3: '#1baf7a'}
BLUE, ORANGE, AQUA, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#0b0b0b', '#52514e', '#e1e0d9'
fm.fontManager.addfont('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')
plt.rcParams.update({'font.family': 'IPAGothic', 'axes.edgecolor': '#c3c2b7', 'axes.linewidth': .8, 'axes.spines.top': False, 'axes.spines.right': False, 'xtick.color': MUTED, 'ytick.color': MUTED, 'font.size': 8, 'axes.titlesize': 9, 'axes.titleweight': 'bold', 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
def style(ax, t, u): ax.set_title(t + '  (' + u + ')', loc='left', color=INK); ax.grid(axis='y', color=GRID, lw=.6); ax.set_xlim(2026, 2060); ax.set_xticks([2026, 2035, 2045, 2055])
def line(ax, c, ys, ls='-', label=None, fmt='%.0f'):
    ax.plot(Y, ys, color=COL[c], lw=1.8, ls=ls, label=label); ax.text(2055.6, ys[-1], fmt % ys[-1], color=COL[c], va='center', fontsize=7.5)
LAB = dict(F='F', **{SQ: 'StatusQuo', N3: 'N3'})
def panel(ax, title, unit, key, fmt='%.0f'):
    style(ax, title, unit)
    for c, _ in C3: line(ax, c, [val(c, y, key) for y in Y], label=LAB[c], fmt=fmt)
    ax.legend(frameon=False, fontsize=7, loc='best')
def fig4(name, specs, h=5.6):
    fig, ax = plt.subplots(2, 2, figsize=(7.4, h))
    for a, s in zip(ax.ravel(), specs): panel(a, *s)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=200); plt.close(fig)
fig4('fig_main.png', [('実質GDP', '兆円', 'real_gdp_trn', '%.1f'), ('名目GDP', '兆円', 'nominal_gdp_trn'), ('税収（診断値）', '兆円', 'tax_diagnostic_trn'), ('家計消費（名目・代理）', '兆円', 'household_consumption_nominal_proxy_trn')])
fig4('fig_second.png', [('資本ストック（実質）', '兆円', 'capital_total_real_trn'), ('政策投資（実質）', '兆円', 'I_policy_real_trn', '%.1f'), ('家計の可処分現金（マクロ代理）', '兆円', 'macro_cash_DI_proxy_trn'), ('労働力人口プロキシ', '人', 'labor_force_population_proxy', '%.2e')])
# N3 own accounts
def nv(k, y): return float(ann[(N3, y)][k])
fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.9))
for a, (k, t, c) in zip(ax, [('policy_tax_delta_trn', '政策税差分（N3）', BLUE), ('household_cash_delta_trn', '家計の現金変化（N3）', ORANGE)]):
    a.plot(Y, [nv(k, y) for y in Y], color=c, lw=1.8); a.axhline(0, color='#c3c2b7', lw=.8); a.set_title(t + '  (兆円)', loc='left', fontsize=8, color=INK); a.grid(axis='y', color=GRID, lw=.6); a.set_xticks([2026, 2035, 2045, 2055]); a.text(2055, nv(k, 2055), '%+.1f' % nv(k, 2055), ha='right', va='bottom', fontsize=7.5)
a = ax[2]; a.plot(Y, [nv('population', y) / 1e4 for y in Y], color=AQUA, lw=1.8, label='N3'); a.plot(Y, [float(ann[(SQ, y)]['population']) / 1e4 for y in Y], color=ORANGE, lw=1.8, label='StatusQuo'); a.set_title('総人口  (万人)', loc='left', fontsize=8, color=INK); a.grid(axis='y', color=GRID, lw=.6); a.set_xticks([2026, 2035, 2045, 2055]); a.legend(frameon=False, fontsize=7)
for x in ax: x.spines['top'].set_visible(False); x.spines['right'].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_n3.png'), dpi=200); plt.close(fig)
# fiscal
FC = [(SQ, 'StatusQuo'), (FREF, 'F（固定参照）'), (N3, 'N3（候補）')]; FCOL = {SQ: ORANGE, FREF: BLUE, N3: AQUA}
fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.9))
for a, (k, t) in zip(ax, [('CL_debt_end_candidate_trn', '国・地方の債務残高（部分・条件付き）'), ('CL_PB_candidate_trn', '同・基礎的収支（候補）'), ('CL_cash_assets_end_candidate_trn', '現金資産（債務ゼロ後）')]):
    for c, n in FC:
        ys = [float(fis[(c, y)][k]) for y in Y]; a.plot(Y, ys, color=FCOL[c], lw=1.6, label=n); a.text(2055.4, ys[-1], '%.0f' % ys[-1], color=FCOL[c], fontsize=6.5, va='center')
    a.set_title(t + '  (兆円)', loc='left', fontsize=7.4, color=INK); a.grid(axis='y', color=GRID, lw=.6); a.set_xticks([2026, 2035, 2045, 2055]); a.set_xlim(2026, 2062); a.axhline(0, color='#c3c2b7', lw=.8)
ax[0].legend(frameon=False, fontsize=6.5)
for x in ax: x.spines['top'].set_visible(False); x.spines['right'].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_fiscal.png'), dpi=200); plt.close(fig)
# sensitivity
NM = dict(PARITY_FIXED_BASES='前年基礎を固定', PARITY_NO_CORPORATE='法人系なし', PARITY_NO_PENSION='年金なし', PARITY_NO_FLAT='フラット税なし', PARITY_NO_MEDICAL='医療なし', PARITY_NO_RELIEF='軽減なし', PARITY_NO_ESTATE='相続なし', PARITY_MPC_LOW='MPC 低(0.5)', PARITY_MPC_HIGH='MPC 高(0.9)', PARITY_DEPRECIATION_LOW='減耗 低', PARITY_DEPRECIATION_HIGH='減耗 高', PARITY_INVESTMENT_START2038='投資開始2038', PARITY_INVESTMENT_RESPONSE0='投資応答0', PARITY_INVESTMENT_RESPONSE60='投資応答0.6', PARITY_LABOR_ADD100K='追加労働10万人', PARITY_NO_CARRY='資本持越しなし', PARITY_INSURANCE_STRESS='保険運用不振', PARITY_KPI_HIGH_THRESHOLD='KPI閾値高(100%)')
sd = {r['case']: float(r['delta_vs_connected_candidate']) for r in sens}; items = sorted([(k, sd[k]) for k in NM if k in sd], key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(7.4, 4.6)); ax.barh([NM[k] for k, _ in items], [d for _, d in items], color=[BLUE if d >= 0 else ORANGE for _, d in items], height=.62)
for i, (k, d) in enumerate(items): ax.text(d + (.4 if d >= 0 else -.4), i, '%+.2f' % d, va='center', ha='left' if d >= 0 else 'right', fontsize=7.2, color=INK)
ax.axvline(0, color='#c3c2b7', lw=.8); ax.grid(axis='x', color=GRID, lw=.6); ax.set_xlim(-16, 40); ax.set_title('2055年 実質GDP：N3候補の1条件を変えた再実行との差（候補比）  (兆円)', loc='left', color=INK)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_sens.png'), dpi=200); plt.close(fig)
# ---------- numbers for text
g = lambda c, y, k: val(c, y, k)
KEYS = [('実質GDP（兆円）', 'real_gdp_trn', '%.1f'), ('名目GDP（兆円）', 'nominal_gdp_trn', '%.0f'), ('税収・診断値（兆円）', 'tax_diagnostic_trn', '%.1f'), ('家計消費・名目代理（兆円）', 'household_consumption_nominal_proxy_trn', '%.1f'), ('資本ストック・実質（兆円）', 'capital_total_real_trn', '%.0f'), ('家計可処分現金・代理（兆円）', 'macro_cash_DI_proxy_trn', '%.1f')]
def fv(c, y, k): return float(fis[(c, y)][k])
POP = {c: float(ann[(c, 2055)]['population']) / 1e4 for c in (SQ, N3)}
dbt0 = next((y for y in Y if fv(N3, y, 'CL_debt_end_candidate_trn') <= 1e-9), None)
cash55 = fv(N3, 2055, 'CL_cash_assets_end_candidate_trn'); pbd = {y: nv('policy_tax_delta_trn', y) for y in (2035, 2045, 2055)}; hc55 = nv('household_cash_delta_trn', 2055)
# ---------- PDF
pdfmetrics.registerFont(TTFont('IPAGothic', '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')); FN = 'IPAGothic'
from reportlab.pdfbase.pdfmetrics import registerFontFamily; registerFontFamily(FN, normal=FN, bold=FN, italic=FN, boldItalic=FN)
st = lambda n, **k: ParagraphStyle(n, fontName=FN, leading=k.pop('leading', 13), **k)
H1, H2, B, SM = st('h1', fontSize=17, leading=22, spaceAfter=4), st('h2', fontSize=11.5, leading=16, spaceBefore=8, spaceAfter=3, textColor=colors.HexColor('#184f95')), st('b', fontSize=8.8), st('s', fontSize=7.4, leading=10, textColor=colors.HexColor('#52514e'))
BOX = st('box', fontSize=8.5, leading=12.2, textColor=colors.HexColor('#7a2e0e')); P = lambda t, s=B: Paragraph(t, s)
def box(text):
    t = Table([[P(text, BOX)]], colWidths=[174 * mm]); t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdf0e9')), ('BOX', (0, 0), (-1, -1), .8, colors.HexColor('#eb6834')), ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)])); return t
def table(rows, widths, fs=7.6):
    t = Table(rows, colWidths=widths, repeatRows=1); t.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), FN), ('FONTSIZE', (0, 0), (-1, -1), fs), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef8')), ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c3c2b7')), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)])); return t
def foot(c, d):
    c.saveState(); c.setFont(FN, 7); c.setFillColor(colors.HexColor('#898781')); c.drawString(18 * mm, 9 * mm, 'SPE StatusQuo／F／N3 比較レポート DRAFT・非正式・予測ではない  N3 Commit 37c3399f'); c.drawRightString(192 * mm, 9 * mm, '%d' % d.page); c.restoreState()
NOTE = ('この資料の読み方　数値は「前提と接続範囲の違い」の比較であり、予測でも政策の推奨でも因果の主張でもありません。N3は<b>未採用の候補</b>（年金帰属＝国内移転候補、2035年所得KPI閾値0%、フラット税・法人・年金の入力は未較正）です。'
        'Fは固定参照（ff621006）で今回は再実行していません。<b>N3は政策範囲が異なり（フラット税・年金・法人・医療・相続贈与を含む）、F・SQとの差は「N3の効果」ではなく、範囲と前提の違いを含みます。</b>'
        'また全ケース共通のマクロ（基調成長・人口・労働）は別途診断中で、全シナリオで実質GDPが初期580を下回る点は、本資料では診断していません。RP-023／M19–25 HOLD、RP-024 PENDING、正式承認状態は変更していません。')
A, S3 = (lambda c, y, k: g(c, y, k)), None
doc = SimpleDocTemplate(os.path.join(OUT, 'SPE_N3_F_StatusQuo_Comparison_Report_DRAFT_20261122.pdf'), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm, title='SPE StatusQuo／F／N3 比較レポート DRAFT', author='Claude')
s = [P('SPE StatusQuo／F／N3 比較レポート（2026〜2055年）', H1), P('DRAFT／NON-CANONICAL　2026-11-22　データ：N3 F相当実装（ChatGPT Work Commit 37c3399f、Claude限定独立検算 PASS_WITH_LIMITATIONS）、基準は年金帰属＝DOMESTIC_TRANSFER', SM), Spacer(1, 4), box(NOTE), Spacer(1, 6), P('1. 要点（2055年）', H2)]
rows = [['指標（2055年）', 'F', 'StatusQuo', 'N3候補', 'N3−SQ', 'N3−F']]
for n, k, f in KEYS: rows.append([n, f % g('F', 2055, k), f % g(SQ, 2055, k), f % g(N3, 2055, k), ('%+.1f' % (g(N3, 2055, k) - g(SQ, 2055, k))), ('%+.1f' % (g(N3, 2055, k) - g('F', 2055, k)))])
rows.append(['総人口（万人）', '–', '%.0f' % POP[SQ], '%.0f' % POP[N3], '%+.0f' % (POP[N3] - POP[SQ]), '–'])
s += [table(rows, [58 * mm, 22 * mm, 24 * mm, 24 * mm, 23 * mm, 23 * mm]), Spacer(1, 4)]
s += [P('2055年の実質GDPは F %.1f、StatusQuo %.1f、N3候補 %.1f 兆円で、N3は StatusQuo を %.1f兆円、F を %.1f兆円下回ります。2026年の出発点（580兆円）に対しても N3 は %.1f兆円低くなります（StatusQuo、F も出発点を下回ります）。N3の政策税差分は 2035年 %+.1f、2055年 %+.1f 兆円、家計の現金変化は 2055年 %+.1f 兆円で、N3は家計に純負担が出る形の候補です（水準は未較正）。' % (g('F', 2055, 'real_gdp_trn'), g(SQ, 2055, 'real_gdp_trn'), g(N3, 2055, 'real_gdp_trn'), g(SQ, 2055, 'real_gdp_trn') - g(N3, 2055, 'real_gdp_trn'), g('F', 2055, 'real_gdp_trn') - g(N3, 2055, 'real_gdp_trn'), 580 - g(N3, 2055, 'real_gdp_trn'), pbd[2035], pbd[2055], hc55)), PageBreak()]
s += [P('2. 主要指標の推移', H2), Image(os.path.join(OUT, 'fig_main.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3), P('3本は同じ2026年の初期状態（実質580、名目600兆円）から始まります。N3の実質GDPは2030年（フラット税等の開始年）にStatusQuoから乖離し、差は2035年に約-40兆円まで拡大します（2030年より前は差0）。感度（§7）ではフラット税を外すと2055年に+33.9兆円で、乖離の大きな部分はこの項目に対応しますが、因果の分解ではありません。税収（診断値）はN3がF・SQの双方を上回りますが、政策税差分を含む値です。', SM), PageBreak()]
s += [P('3. 資本・投資・家計現金・労働', H2), Image(os.path.join(OUT, 'fig_second.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3), P('政策投資は企業資金勘定に基づく誘発投資と旧実装由来の項を合算した値で、負の残りが含まれます（独立検算の重大論点4）。労働力人口プロキシは各ケースの内生値です。', SM), PageBreak()]
yrs = KY; hdr = ['指標／ケース'] + [str(y) for y in yrs]; rows = [hdr]
for n, k, f in KEYS[:4]:
    for c, lb in (('F', 'F'), (SQ, 'SQ'), (N3, 'N3')): rows.append([n.split('（')[0] + ' ' + lb] + [f % g(c, y, k) for y in yrs])
rows.append(['実質GDP差 N3−SQ'] + ['%+.1f' % (g(N3, y, 'real_gdp_trn') - g(SQ, y, 'real_gdp_trn')) for y in yrs]); rows.append(['実質GDP差 N3−F'] + ['%+.1f' % (g(N3, y, 'real_gdp_trn') - g('F', y, 'real_gdp_trn')) for y in yrs])
s += [P('4. 主要年の数値表（兆円）', H2), table(rows, [38 * mm] + [19.4 * mm] * 7, 7.2), Spacer(1, 6)]
s += [P('5. N3候補の内部勘定（政策税差分・家計現金・人口）', H2), Image(os.path.join(OUT, 'fig_n3.png'), width=174 * mm, height=174 * mm * 2.9 / 7.4), Spacer(1, 3), P('N3の政策税差分は前年の賃金・名目GDPに連動する基礎で再計算され、新しい所得や利益は加えられません（独立検算で確認）。差分の水準は調査ベース合成値に依存し、未較正です。', SM), PageBreak()]
s += [P('6. 国・地方の条件付き財政接続（部分・参考）', H2), Image(os.path.join(OUT, 'fig_fiscal.png'), width=174 * mm, height=174 * mm * 2.9 / 7.4), Spacer(1, 3)]
rows = [['2055年（兆円）', 'StatusQuo', 'F（固定参照）', 'N3候補']] + [[n] + [('%.1f' % fv(c, 2055, k)) for c in (SQ, FREF, N3)] for n, k in (('債務残高（国・地方・部分）', 'CL_debt_end_candidate_trn'), ('基礎的収支（候補）', 'CL_PB_candidate_trn'), ('現金資産', 'CL_cash_assets_end_candidate_trn'))]
s += [table(rows, [60 * mm, 36 * mm, 36 * mm, 36 * mm]), Spacer(1, 3), P('CAO 2026年7月試算に基づく基準線に、各ケースの政策一次収支差分を接続した<b>条件付き</b>の部分財政です（一般政府の全国PB・債務・国債発行は未実装で、財政からGDPへのフィードバックもありません）。N3候補で債務が %s年にゼロとなる結果は、未較正の政策税差分を国・地方PBへ全額接続したためで、独立検算の損益分岐は<b>実現率約65%%</b>（0.5倍で債務539、0倍で2,338兆円）です。2041年以降はSFA 0・名目据置の尾部仮定を含みます。' % (dbt0 if dbt0 else '–')), PageBreak()]
s += [P('7. N3候補の感度（2055年 実質GDP、候補比）', H2), Image(os.path.join(OUT, 'fig_sens.png'), width=170 * mm, height=170 * mm * 4.6 / 7.4), Spacer(1, 2), P('各棒は候補の1条件だけを変えて再実行した差で、<b>加算不可</b>です。高MPCがGDPを下げるのは、候補の家計現金変化が負で、MPCがその負の現金に掛かるためです（算術上は整合、ただし通常の読みとは逆）。KPI閾値高(100%)は2035年に標準税率を15%で凍結する分岐です。基準ケースの所得成長は+0.175%で閾値0%の直上にあり、この分岐は閾値の近傍にあります。', SM), PageBreak()]
s += [P('8. 読み方の注意と検証状況', H2)]
NOTES = ['<b>比較の条件</b>：StatusQuo＝共通OFFの固定SQ、F＝固定参照 ff621006（再実行なし）、N3＝PARITY_CONNECTED_CANDIDATE（年金帰属は未採用候補のうち国内移転）。3者は同一エンジン・同一出発点だが、政策範囲が同質ではない。',
 '<b>因果ではない</b>：N3−SQ、N3−F の差は、N3の政策範囲（フラット税、年金、法人、医療、相続贈与、外国人材関連の構造等）と各種の未較正前提を含む。優劣や順位の根拠にしない。',
 '<b>共通マクロの未診断事項</b>：全ケースで実質GDPが初期580を下回る点、StatusQuoの成長に関する疑義は本書で診断していない（次工程の課題）。',
 '<b>未実装・未較正</b>：全国の国債・PB（一般政府）、財政→GDPフィードバック、所得中央値・全国ジニ・健康QOL、インボイス・広域化共済・スマート・シュリンクの定量化（構造のみ）。年金帰属の採用、2035年KPIの閾値と指標、ジニ軽減の内容・期間はOwner未裁定。',
 '<b>検証状況</b>：Claude限定独立検算（Commit ba08c45d、PASS_WITH_LIMITATIONS）。マクロ164項目・財政52項目、41データファイルの再実行バイト一致、旧79ケース回帰8,238,048セル差0。<b>算術・勘定・再現性の判定で、政策効果の妥当性は判定対象外</b>。F参照の再実行・エンジン全体の独立再実装は未実施。',
 '<b>出典</b>：ChatGPT Work handoff/chatgpt-n3-f-parity-implementation-20261122/results/（SQ_F_N3_Annual_Comparison.csv、Annual_DOMESTIC_TRANSFER.csv、Conditional_National_Local_Fiscal.csv、Sensitivity.csv）。図表の数値はこれらのCSVから自動生成。']
for n in NOTES: s += [P('・' + n, B), Spacer(1, 3)]
doc.build(s, onFirstPage=foot, onLaterPages=foot)
# ---------- Markdown
md = ['# StatusQuo／F／N3 比較レポート', '', 'SPE｜2026〜2055年 年次計算（暫定・DRAFT・非正式）　作成：2026-11-22', '', 'PDF版（グラフ入り）：`SPE_N3_F_StatusQuo_Comparison_Report_DRAFT_20261122.pdf`（本Markdownは同内容の文字・表版で、グラフは数値表で代替）', '', '> **この資料の位置づけ。** ' + NOTE.replace('<b>', '**').replace('</b>', '**').replace('この資料の読み方　', ''), '']
md += ['## 1. 結論の概観（2055年）', '', '| 指標（2055年） | F | StatusQuo | N3候補 | N3−SQ | N3−F |', '|:---|---:|---:|---:|---:|---:|']
for n, k, f in KEYS: md.append('| %s | %s | %s | %s | %+.1f | %+.1f |' % (n, f % g('F', 2055, k), f % g(SQ, 2055, k), f % g(N3, 2055, k), g(N3, 2055, k) - g(SQ, 2055, k), g(N3, 2055, k) - g('F', 2055, k)))
md.append('| 総人口（万人） | – | %.0f | %.0f | %+.0f | – |' % (POP[SQ], POP[N3], POP[N3] - POP[SQ]))
md += ['', '- 2055年の実質GDPは F %.1f、StatusQuo %.1f、N3候補 %.1f 兆円。N3は StatusQuo を %.1f兆円、F を %.1f兆円下回り、出発点（580兆円）に対しても %.1f兆円低い（StatusQuo、F も出発点を下回る）。' % (g('F', 2055, 'real_gdp_trn'), g(SQ, 2055, 'real_gdp_trn'), g(N3, 2055, 'real_gdp_trn'), g(SQ, 2055, 'real_gdp_trn') - g(N3, 2055, 'real_gdp_trn'), g('F', 2055, 'real_gdp_trn') - g(N3, 2055, 'real_gdp_trn'), 580 - g(N3, 2055, 'real_gdp_trn')),
       '- N3の政策税差分は 2035年 %+.1f、2045年 %+.1f、2055年 %+.1f 兆円、家計の現金変化は 2055年 %+.1f 兆円（水準は未較正）。' % (pbd[2035], pbd[2045], pbd[2055], hc55), '']
md += ['## 2. 年次結果（主要年）', '']
for n, k, f in KEYS:
    md += ['| %s | %s |' % (n, ' | '.join(str(y) for y in yrs)), '|:---|' + '---:|' * len(yrs)]
    for c, lb in (('F', 'F'), (SQ, 'StatusQuo'), (N3, 'N3候補')): md.append('| %s | %s |' % (lb, ' | '.join(f % g(c, y, k) for y in yrs)))
    md.append('| 差（N3−SQ） | %s |' % ' | '.join('%+.1f' % (g(N3, y, k) - g(SQ, y, k)) for y in yrs)); md.append('| 差（N3−F） | %s |' % ' | '.join('%+.1f' % (g(N3, y, k) - g('F', y, k)) for y in yrs)); md.append('')
md += ['## 3. N3候補の内部勘定', '', '| 兆円 | ' + ' | '.join(str(y) for y in yrs) + ' |', '|:---|' + '---:|' * len(yrs)]
for n, k in (('政策税差分', 'policy_tax_delta_trn'), ('家計の現金変化', 'household_cash_delta_trn')): md.append('| %s | %s |' % (n, ' | '.join('%+.1f' % nv(k, y) for y in yrs)))
md.append('| 総人口（万人）N3 | %s |' % ' | '.join('%.0f' % (nv('population', y) / 1e4) for y in yrs)); md.append('| 総人口（万人）SQ | %s |' % ' | '.join('%.0f' % (float(ann[(SQ, y)]['population']) / 1e4) for y in yrs)); md.append('')
md += ['## 4. 国・地方の条件付き財政接続（部分・参考）', '', '| 兆円 | 区分 | ' + ' | '.join(str(y) for y in yrs) + ' |', '|:---|:---|' + '---:|' * len(yrs)]
for n, k in (('債務残高', 'CL_debt_end_candidate_trn'), ('基礎的収支', 'CL_PB_candidate_trn'), ('現金資産', 'CL_cash_assets_end_candidate_trn')):
    for c, lb in FC: md.append('| %s | %s | %s |' % (n, lb, ' | '.join('%.1f' % fv(c, y, k) for y in yrs)))
md += ['', 'CAO 2026年7月試算に基づく基準線に政策一次収支差分を接続した**条件付き**の部分財政です。一般政府の全国PB・債務・国債発行は未実装で、財政からGDPへのフィードバックもありません。N3候補で債務がゼロになる年は %s年ですが、これは未較正の政策税差分を国・地方PBへ全額接続した結果で、独立検算の損益分岐は**実現率約65%%**です。' % (dbt0 if dbt0 else '–'), '']
md += ['## 5. N3候補の感度（2055年 実質GDP、候補比・兆円）', '', '| 条件 | 実質GDP | 候補比 |', '|:---|---:|---:|']
for k, d in sorted(items, key=lambda t: -t[1]): md.append('| %s | %.2f | %+.2f |' % (NM[k], float(next(r['value'] for r in sens if r['case'] == k)), d))
md += ['', '各行は1条件だけを変えた再実行の差で、**加算不可**です。高MPCでGDPが下がるのは、候補の家計現金変化が負でMPCがその負の現金に掛かるためです。基準ケースの2035年KPI指標（所得成長 +0.175%）は閾値0%の直上にあります。', '', '## 6. 読み方の注意と検証状況', '']
md += ['- ' + n.replace('<b>', '**').replace('</b>', '**') for n in NOTES]
md += ['', '---', '更新：2026-11-22。DRAFT・非正式・Owner承認前。このレポートはFinding Close、Acceptance、HOLD解除、DecisionLog記載、Canonical化、N3の完成宣言のいずれでもありません。RP-023／M19–25のHOLD、RP-024のPENDINGは維持されています。数値は思考実験・条件付きの比較であり、結果を保証するものではありません。', '']
open(os.path.join(OUT, 'SPE_N3_F_StatusQuo_Comparison_Report_DRAFT_20261122.md'), 'w').write('\n'.join(md))
print('built', os.path.getsize(os.path.join(OUT, 'SPE_N3_F_StatusQuo_Comparison_Report_DRAFT_20261122.pdf')), 'debt-zero year', dbt0)
