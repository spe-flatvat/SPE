"""Build the F / StatusQuo / N3 common-indicator report (PDF + Markdown) from the fixed Work output.

python3 SPE_F_SQ_N3_Common_Indicators_Report_Build_DRAFT_20261123.py BARE_GIT_DIR OUTDIR
Reads Annual_Comparison.csv / Comparison_Contract.csv at the fixed commit via `git show`
(no other input). Every number in the report comes from those CSVs. DRAFT / NON-CANONICAL.
"""
import sys, os, csv, io, subprocess
import matplotlib; matplotlib.use('Agg'); import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

BARE, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
FINAL = '8a8edb403b960cceb535f9b70461646e9374c229'; D = 'handoff/chatgpt-f-sq-n3-common-indicators-20261123/'
def rows(name): return list(csv.DictReader(io.StringIO(subprocess.check_output(['git', '-C', BARE, 'show', f'{FINAL}:{D}{name}']).decode())))
ann = rows('Annual_Comparison.csv'); con = rows('Comparison_Contract.csv')
A = {(int(r['year']), r['indicator']): r for r in ann}
Y = list(range(2026, 2056)); KY = [2026, 2030, 2035, 2040, 2045, 2050, 2055]
def v(c, y, k):
    x = A[(y, k)][c]; return None if x == 'N/A' else float(x)
def gap(p, y, k): return float(A[(y, k)][p])
COL = {'F': '#2a78d6', 'SQ': '#eb6834', 'N3': '#1baf7a'}; LAB = {'F': 'F', 'SQ': 'StatusQuo', 'N3': 'N3'}
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e1e0d9'
fm.fontManager.addfont('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')
plt.rcParams.update({'font.family': 'IPAGothic', 'axes.edgecolor': '#c3c2b7', 'axes.linewidth': .8, 'axes.spines.top': False, 'axes.spines.right': False,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'font.size': 8, 'axes.titlesize': 9, 'axes.titleweight': 'bold', 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
def panel(ax, title, unit, ind, scale=1.0, fmt='%.1f', start=2026):
    ax.set_title(title + '  (' + unit + ')', loc='left', color=INK); ax.grid(axis='y', color=GRID, lw=.6); ax.set_xlim(2026, 2060); ax.set_xticks([2026, 2035, 2045, 2055])
    for c in ('F', 'SQ', 'N3'):
        ys = [v(c, y, ind) / scale for y in Y if y >= start]; xs = [y for y in Y if y >= start]
        ax.plot(xs, ys, color=COL[c], lw=1.8, label=LAB[c]); ax.text(2055.6, ys[-1], fmt % ys[-1], color=COL[c], va='center', fontsize=7.5)
    ax.legend(frameon=False, fontsize=7, loc='best')
def fig4(name, specs):
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.6))
    for a, s in zip(ax.ravel(), specs): panel(a, *s)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=200); plt.close(fig)
fig4('fig_levels.png', [('実質GDP', '兆円・2026年モデル価格', 'real_gdp'), ('名目GDP', '兆円', 'nominal_gdp', 1.0, '%.0f'),
                         ('総人口', '万人', 'population', 1e4, '%.0f'), ('一人当たり実質GDP', '万円', 'real_gdp_per_capita', 1e4)])
fig4('fig_rates.png', [('実質GDP成長率', '%', 'real_gdp_growth', 1.0, '%.2f', 2027), ('暗黙GDPデフレーター', '2026=100', 'implicit_gdp_deflator', 1.0, '%.1f'),
                        ('有効労働投入（モデル）', '万人相当', 'effective_labor', 1e4, '%.0f'), ('一人当たり名目GDP', '万円', 'nominal_gdp_per_capita', 1e4, '%.0f')])
fig, ax = plt.subplots(1, 2, figsize=(7.4, 2.8))
for a, (k, t) in zip(ax, (('real_gdp', '実質GDP差（兆円）'), ('nominal_gdp', '名目GDP差（兆円）'))):
    for p, c, lb in (('F_minus_SQ', COL['F'], 'F − SQ'), ('N3_minus_SQ', COL['N3'], 'N3 − SQ'), ('F_minus_N3', COL['SQ'], 'F − N3')):
        ys = [gap(p, y, k) for y in Y]; a.plot(Y, ys, color=c, lw=1.8, label=lb); a.text(2055.5, ys[-1], '%+.1f' % ys[-1], color=c, va='center', fontsize=7.5)
    a.axhline(0, color='#c3c2b7', lw=.8); a.set_title(t, loc='left', color=INK, fontsize=8.5); a.grid(axis='y', color=GRID, lw=.6); a.set_xlim(2026, 2060); a.set_xticks([2026, 2035, 2045, 2055])
ax[0].legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_gaps.png'), dpi=200); plt.close(fig)

# ----------------------------------------------------------------- numbers used in text
r55 = {c: v(c, 2055, 'real_gdp') for c in ('F', 'SQ', 'N3')}; n55 = {c: v(c, 2055, 'nominal_gdp') for c in ('F', 'SQ', 'N3')}
d55 = {c: v(c, 2055, 'implicit_gdp_deflator') for c in ('F', 'SQ', 'N3')}; p55 = {c: v(c, 2055, 'population') for c in ('F', 'SQ', 'N3')}
below = {c: sum(1 for y in Y[1:] if v(c, y, 'real_gdp') < 580) for c in ('F', 'SQ', 'N3')}
n3_below_sq = sum(1 for y in Y if gap('N3_minus_SQ', y, 'real_gdp') < 0)
KEYS = [('実質GDP（兆円）', 'real_gdp', '%.1f', 1), ('名目GDP（兆円）', 'nominal_gdp', '%.1f', 1), ('暗黙GDPデフレーター（2026=100）', 'implicit_gdp_deflator', '%.3f', 1),
        ('総人口（万人）', 'population', '%.0f', 1e4), ('有効労働投入（万人相当）', 'effective_labor', '%.0f', 1e4),
        ('一人当たり実質GDP（万円）', 'real_gdp_per_capita', '%.1f', 1e4), ('一人当たり名目GDP（万円）', 'nominal_gdp_per_capita', '%.1f', 1e4)]
def gp(a, b, y, k, s): return (v(a, y, k) - v(b, y, k)) / s

# ----------------------------------------------------------------- PDF
pdfmetrics.registerFont(TTFont('IPAGothic', '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')); FN = 'IPAGothic'
registerFontFamily(FN, normal=FN, bold=FN, italic=FN, boldItalic=FN)
st = lambda n, **k: ParagraphStyle(n, fontName=FN, leading=k.pop('leading', 13), **k)
H1, H2, B = st('h1', fontSize=17, leading=22, spaceAfter=4), st('h2', fontSize=11.5, leading=16, spaceBefore=8, spaceAfter=3, textColor=colors.HexColor('#184f95')), st('b', fontSize=8.8)
SM = st('s', fontSize=7.4, leading=10, textColor=colors.HexColor('#52514e')); BOX = st('box', fontSize=8.5, leading=12.2, textColor=colors.HexColor('#7a2e0e')); P = lambda t, s=B: Paragraph(t, s)
def box(text):
    t = Table([[P(text, BOX)]], colWidths=[174 * mm]); t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fdf0e9')), ('BOX', (0, 0), (-1, -1), .8, colors.HexColor('#eb6834')),
                                                                           ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)])); return t
def table(rws, widths, fs=7.6):
    t = Table(rws, colWidths=widths, repeatRows=1); t.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), FN), ('FONTSIZE', (0, 0), (-1, -1), fs), ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef8')),
                                                                           ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c3c2b7')), ('ALIGN', (1, 1), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                                           ('TOPPADDING', (0, 0), (-1, -1), 2.2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.2)])); return t
def foot(c, d):
    c.saveState(); c.setFont(FN, 7); c.setFillColor(colors.HexColor('#898781'))
    c.drawString(18 * mm, 9 * mm, 'SPE F／StatusQuo／N3 共通指標レポート DRAFT・非正式・予測ではない  Work 8a8edb40／Claude検算 da79ab62'); c.drawRightString(192 * mm, 9 * mm, '%d' % d.page); c.restoreState()
NOTE = ('この資料の読み方　数値は「既存実装の条件付き出力」の比較で、予測でも政策の推奨でも因果の主張でもありません。F・SQ・N3の差は、人口・労働・価格の共通部分ではなく'
        '各施策の実装範囲と接続の違い（政策内生差）を含みます。<b>N3は未採用の候補（BASE_REPLAY、追加G/I OFF）</b>で、2026年の初期状態（実質580兆円、名目600兆円、人口122,618,024人）は3者で同一です。'
        '全国の税収・賃金・家計・ジニ・財政収支は、定義と範囲が揃わないため<b>比較していません（N/A）</b>。RP-023／M19–25 HOLD、RP-024 PENDING、正式承認状態は維持されています。')
doc = SimpleDocTemplate(os.path.join(OUT, 'SPE_F_SQ_N3_Common_Indicators_Report_DRAFT_20261123.pdf'), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                        title='SPE F／StatusQuo／N3 共通指標レポート DRAFT', author='Claude')
s = [P('SPE F／StatusQuo／N3 共通指標レポート（2026〜2055年）', H1),
     P('DRAFT／NON-CANONICAL　2026-11-23　データ：ChatGPT Work 共通指標成果（最終固定Commit 8a8edb40）。Claude限定独立検算 PASS_WITH_LIMITATIONS（Commit da79ab62）。', SM), Spacer(1, 4), box(NOTE),
     P('1. 2055年の概観', H2)]
rws = [['指標（2055年）', 'F', 'StatusQuo', 'N3', 'F−SQ', 'N3−SQ', 'F−N3']]
for n, k, f, sc in KEYS:
    rws.append([n, f % (v('F', 2055, k) / sc), f % (v('SQ', 2055, k) / sc), f % (v('N3', 2055, k) / sc),
                ('%+' + f[1:]) % gp('F', 'SQ', 2055, k, sc), ('%+' + f[1:]) % gp('N3', 'SQ', 2055, k, sc), ('%+' + f[1:]) % gp('F', 'N3', 2055, k, sc)])
s += [table(rws, [52 * mm, 20 * mm, 22 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm], 7.4), Spacer(1, 4)]
s += [P('2055年の実質GDPは F %.1f、StatusQuo %.1f、N3 %.1f 兆円で、F は StatusQuo を %.1f兆円上回り、N3 は StatusQuo を %.1f兆円下回ります。出発点（580兆円）に対しては<b>3者とも2027〜2055年の29遷移年のうち下回る年があります</b>'
         '（StatusQuo %d年、F %d年、N3 %d年）。この点は本書では診断していません。N3 が StatusQuo を下回る年は %d年（2026〜2029年は上回る）。'
         % (r55['F'], r55['SQ'], r55['N3'], r55['F'] - r55['SQ'], r55['SQ'] - r55['N3'], below['SQ'], below['F'], below['N3'], n3_below_sq), B)]
s += [P('2. 水準の推移', H2), Image(os.path.join(OUT, 'fig_levels.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3),
      P('実質GDPは2026年モデル価格、名目GDPは当年のモデル価格です。人口はモデルの総居住人口で、F は外国人材・高齢雇用などの経路で SQ・N3 と異なります（2055年 %+.1f万人）。N3 の人口・有効労働は StatusQuo の共通コアをそのまま継承する実装条件で、全年で差が 0 です。' % (gp('F', 'SQ', 2055, 'population', 1e4)), B)]
s += [P('3. 成長率・デフレーター・労働・名目一人当たり', H2), Image(os.path.join(OUT, 'fig_rates.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3),
      P('暗黙GDPデフレーターは名目÷実質から求めた値で、<b>入力インフレ率とは別物</b>です（名目コアは加算式のため、増加率は π/(1+g)）。2055年は F %.1f、SQ %.1f、N3 %.1f（2026=100）。N3 と SQ が完全に一致するのは、この30年データでは3者とも未充足需要が0で価格圧力が働かないためで、F との差（%+.3f）は価格入力でなく F の実質コア（労働）経路の違いによります。入力インフレ率と適用リスク率は3者で同一です。'
        % (d55['F'], d55['SQ'], d55['N3'], d55['F'] - d55['SQ']), B)]
s += [P('4. 3者の差の推移', H2), Image(os.path.join(OUT, 'fig_gaps.png'), width=174 * mm, height=174 * mm * 2.8 / 7.4), Spacer(1, 3),
      P('F−SQ の実質差は2027年から正で、2055年に +%.1f兆円。N3−SQ は2030年ごろから負に転じ、2043年に最大 %.1f兆円まで拡大した後、2055年は %.1f兆円です。F−N3 は両者の合成（F−SQ）−（N3−SQ）で、恒等的に成り立ちます。'
        % (gp('F', 'SQ', 2055, 'real_gdp', 1), min(gap('N3_minus_SQ', y, 'real_gdp') for y in Y), gp('N3', 'SQ', 2055, 'real_gdp', 1)), B)]
hdr = ['指標／ケース'] + [str(y) for y in KY]; rws = [hdr]
for n, k, f, sc in KEYS[:2] + KEYS[5:6]:
    for c in ('F', 'SQ', 'N3'): rws.append([n.split('（')[0] + ' ' + LAB[c]] + [f % (v(c, y, k) / sc) for y in KY])
rws.append(['実質GDP差 F−SQ'] + ['%+.1f' % gp('F', 'SQ', y, 'real_gdp', 1) for y in KY]); rws.append(['実質GDP差 N3−SQ'] + ['%+.1f' % gp('N3', 'SQ', y, 'real_gdp', 1) for y in KY]); rws.append(['実質GDP差 F−N3'] + ['%+.1f' % gp('F', 'N3', y, 'real_gdp', 1) for y in KY])
s += [P('5. 主要年の数値表', H2), table(rws, [40 * mm] + [19 * mm] * 7, 7.1), Spacer(1, 6)]
s += [P('6. 比較の条件', H2)]
COND = ['<b>StatusQuo</b>：現行基準（共通マクロ・価格・イベントを既存のまま、共通医療ON。旧v5・政策原文§9・旧F専用SQは別系列）。<b>F</b>：最新のF（終末期共通化後）の医療参照を、StatusQuo／N3と共通の人口・価格参照に再接続した既存の隔離実行枝（接続前後の差は2055年で −9.4e-6兆円）。<b>N3</b>：既存の原文実装（BASE_REPLAY）、追加の政府購入・公共投資はOFF。',
        '共通の前提：基調成長1%、労働弾性0.65、基調インフレ2%（2027年は紛争で+5%）、イベント損失（2027紛争5%、2031地震3%、2029起点3年毎の災害1%、2028起点隔年の気候0.5%、損失は永続）。2026年のオイルショックは予定のみで初期状態には適用していません。',
        '2026年は初期状態で、遷移（成長率）がありません。成長率は2027年から。']
for t in COND: s += [P('・' + t, B), Spacer(1, 3)]
s += [P('7. 比較できない指標（N/A）の境界', H2)]
rws = [['指標', '区分', '原因コード', '理由（要約）']]
SHORT = {'employment_headcount': '就業者数の系列が3者で揃わない', 'national_tax': '税の範囲・基準が異なる（SQ診断、Fの部分、N3の対象別）', 'national_wages_income': '賃金・所得の概念と母集団が異なる',
         'national_household_cash': '家計現金の定義が異なる（F世帯は合成値）', 'household_purchasing_power': '共通の家計バスケットと現金DIがない', 'national_gini': '3者に共通の全国分布がない（Fは合成）',
         'national_government_balance_pb': '連結範囲が異なる（部分収支と条件付き閉鎖）', 'national_bond_issue_interest_debt': '全国の国債発行・利払・残高を共通に出せない', 'policy_fiscal_cost': '施策別の負担者・移転の境界が異なる',
         'investment': 'Fの政策投資に置換投資が含まれない', 'household_consumption': '政策の写像と現物給付の境界が異なる', 'fund_stock': '基金の範囲が異なる（F保険料軽減、N3年金）'}
for r in con:
    if r['status'] in ('NOT COMPARABLE', 'N/A'): rws.append([r['indicator'], r['status'], r['cause_codes'], SHORT[r['indicator']]])
t = table(rws, [48 * mm, 24 * mm, 20 * mm, 82 * mm], 7.0); t.setStyle(TableStyle([('ALIGN', (0, 1), (-1, -1), 'LEFT')])); s += [t, Spacer(1, 3),
      P('原因コード：1＝共通データ／コード不足、2＝定義・単位・価格基準の差、3＝政策実装粒度の差、4＝部門間接続不足、5＝政策上の未決定。F合成世帯（2055年の現金中央値 423.8万円、非採用感度 424.998万円）はF専用の文脈情報で、全国値やSQ／N3との比較値としては使っていません。', SM)]
s += [P('8. 読み方の注意と検証状況', H2)]
NOTES = ['<b>因果ではない</b>：差は、各施策の実装範囲と未較正の前提を含みます。優劣や順位の根拠にしません。前回（2026-11-22）のレポートはN3を年金・法人・フラット税等を接続した「F相当実装候補」、SQを共通OFFで比較しており、本書とは基準が異なります（並置しない）。',
         '<b>検証状況</b>：算術・勘定・再現性は、Claudeが独立に再計算して全一致（4,818件、不一致0。Workの再実行ファイル7件もバイト一致）。F・N3の需要側内部、外部統計・全国較正、人口・労働入力の原典照合は未検証。<b>経済的妥当性・政策忠実性の判定ではありません</b>。',
         '<b>共通マクロの未診断事項</b>：3者とも初期580を下回る点、災害・気候の起点年（2029／2028）・回復なし・人口初期値（122.6百万人。§9は121.5百万人）は先行検算から引き継いだ実装仮定で、本書では診断していません。',
         '<b>出典</b>：ChatGPT Work handoff/chatgpt-f-sq-n3-common-indicators-20261123/（Annual_Comparison.csv、Comparison_Contract.csv、最終固定Commit 8a8edb40）。Claude独立検算 handoff/claude-f-sq-n3-common-indicators-verification-20261123/（Commit da79ab62）。図表の数値はこれらのCSVから自動生成。']
for n in NOTES: s += [P('・' + n, B), Spacer(1, 3)]
doc.build(s, onFirstPage=foot, onLaterPages=foot)

# ----------------------------------------------------------------- Markdown
md = ['# F／StatusQuo／N3 共通指標レポート', '', 'SPE｜2026〜2055年（暫定・DRAFT・非正式）　作成：2026-11-23', '',
      'PDF版（グラフ入り）：`SPE_F_SQ_N3_Common_Indicators_Report_DRAFT_20261123.pdf`。本Markdownは同内容の文字・表版で、グラフは主要年の数値表で代替しています。', '',
      '> ' + NOTE.replace('<b>', '**').replace('</b>', '**'), '', '## 1. 2055年の概観', '', '| 指標（2055年） | F | StatusQuo | N3 | F−SQ | N3−SQ | F−N3 |', '|:---|---:|---:|---:|---:|---:|---:|']
for n, k, f, sc in KEYS:
    md.append('| %s | %s | %s | %s | %s | %s | %s |' % (n, f % (v('F', 2055, k) / sc), f % (v('SQ', 2055, k) / sc), f % (v('N3', 2055, k) / sc),
              ('%+' + f[1:]) % gp('F', 'SQ', 2055, k, sc), ('%+' + f[1:]) % gp('N3', 'SQ', 2055, k, sc), ('%+' + f[1:]) % gp('F', 'N3', 2055, k, sc)))
md += ['', '- 2055年の実質GDPは F %.1f、StatusQuo %.1f、N3 %.1f 兆円。F は SQ を %.1f兆円上回り、N3 は SQ を %.1f兆円下回る。' % (r55['F'], r55['SQ'], r55['N3'], r55['F'] - r55['SQ'], r55['SQ'] - r55['N3']),
       '- 初期580を下回る年（2027〜2055の29遷移年）：StatusQuo %d年、F %d年、N3 %d年（本書では診断しない）。N3 が SQ を下回る年は %d年（2026〜2029年は上回る）。' % (below['SQ'], below['F'], below['N3'], n3_below_sq),
       '- 暗黙GDPデフレーター（2026=100）2055年：F %.3f、SQ %.3f、N3 %.3f。入力インフレ率とは別物。N3＝SQ は未充足需要0（価格圧力0）の結果。' % (d55['F'], d55['SQ'], d55['N3']), '']
md += ['## 2. 年次結果（主要年）', '']
for n, k, f, sc in KEYS:
    md += ['| %s | %s |' % (n, ' | '.join(str(y) for y in KY)), '|:---|' + '---:|' * len(KY)]
    for c in ('F', 'SQ', 'N3'): md.append('| %s | %s |' % (LAB[c], ' | '.join(f % (v(c, y, k) / sc) for y in KY)))
    md.append('| 差（F−SQ） | %s |' % ' | '.join(('%+' + f[1:]) % gp('F', 'SQ', y, k, sc) for y in KY)); md.append('| 差（N3−SQ） | %s |' % ' | '.join(('%+' + f[1:]) % gp('N3', 'SQ', y, k, sc) for y in KY)); md.append('')
md += ['| 実質GDP成長率（%） | ' + ' | '.join(str(y) for y in KY if y > 2026) + ' |', '|:---|' + '---:|' * (len(KY) - 1)]
for c in ('F', 'SQ', 'N3'): md.append('| %s | %s |' % (LAB[c], ' | '.join('%.2f' % v(c, y, 'real_gdp_growth') for y in KY if y > 2026)))
md += ['', '## 3. 比較の条件', ''] + ['- ' + t.replace('<b>', '**').replace('</b>', '**') for t in COND]
md += ['', '## 4. 比較できない指標（N/A）の境界', '', '| 指標 | 区分 | 原因コード | 理由（要約） |', '|:---|:---|:---|:---|']
for r in con:
    if r['status'] in ('NOT COMPARABLE', 'N/A'): md.append('| %s | %s | %s | %s |' % (r['indicator'], r['status'], r['cause_codes'], SHORT[r['indicator']]))
md += ['', '原因コード：1＝共通データ／コード不足、2＝定義・単位・価格基準の差、3＝政策実装粒度の差、4＝部門間接続不足、5＝政策上の未決定。F合成世帯は F 専用の文脈情報で、全国値や SQ／N3 との比較値には使っていない。', '', '## 5. 読み方の注意と検証状況', ''] + ['- ' + n.replace('<b>', '**').replace('</b>', '**') for n in NOTES] + ['']
open(os.path.join(OUT, 'SPE_F_SQ_N3_Common_Indicators_Report_DRAFT_20261123.md'), 'w', encoding='utf-8').write('\n'.join(md))
print('built', OUT)
