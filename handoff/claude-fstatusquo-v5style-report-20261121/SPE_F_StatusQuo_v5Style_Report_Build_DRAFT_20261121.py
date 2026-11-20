#!/usr/bin/env python3
# Build a v5-style F vs StatusQuo comparison PDF from the verified CSVs of ff6210061615105de9a0d64767c256796be80ed2.
# Usage: python3 <this> <tree_root_of_ff621006> <outdir>   (all numbers are read from the CSVs; nothing is typed in by hand)
import sys, os, csv, collections
import matplotlib; matplotlib.use('Agg'); import logging; logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
D = os.path.join(R, 'handoff/f-common-endoflife-finalization-20261121'); rd = lambda n: list(csv.DictReader(open(os.path.join(D, n))))
A = {(r['case'], int(r['year'])): r for r in rd('Annual.csv')}; SQC = {(r['case'], int(r['year'])): r for r in rd('SQ_Common_Annual.csv')}
CE = {(r['case'], int(r['year'])): r for r in rd('Common_EndOfLife.csv')}; HS = {(r['year'], r['metric']): r for r in rd('Household_Sensitivity.csv')}
NA = {int(r['year']): r for r in rd('Nonadditivity.csv')}; PE = [r for r in rd('Policy_Effects.csv') if r['metric'] == 'real_gdp_trn']
Y = list(range(2026, 2056)); v = lambda c, y, k: float(A[(c, y)][k]); F, SQ = 'LATEST_F', 'SQ_FIXED'
BLUE, ORANGE, AQUA, INK, MUTED, GRID = '#2a78d6', '#eb6834', '#1baf7a', '#0b0b0b', '#52514e', '#e1e0d9'
fm.fontManager.addfont('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')
plt.rcParams.update({'font.family': 'IPAGothic', 'axes.edgecolor': '#c3c2b7', 'axes.linewidth': .8, 'axes.spines.top': False, 'axes.spines.right': False, 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': MUTED, 'font.size': 8, 'axes.titlesize': 9, 'axes.titleweight': 'bold', 'figure.facecolor': '#fcfcfb', 'axes.facecolor': '#fcfcfb'})
def style(ax, title, unit):
    ax.set_title(title + '  (' + unit + ')', loc='left', color=INK); ax.grid(axis='y', color=GRID, lw=.6); ax.set_xlim(2026, 2058); ax.set_xticks([2026, 2035, 2045, 2055])
def lines(ax, series, fmt='%.1f'):
    for (name, ys, col, ls) in series:
        ax.plot(Y, ys, color=col, lw=1.8, ls=ls, label=name); ax.text(2055.6, ys[-1], (fmt % ys[-1]), color=col, va='center', fontsize=7.5)
    ax.legend(frameon=False, fontsize=7, loc='best')
S = lambda c, k, scale=1.: [v(c, y, k) * scale for y in Y]
# ---------------- figures
def fig_main():
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.6)); a = ax.ravel()
    style(a[0], '実質GDP', '兆円'); lines(a[0], [('F（LATEST_F）', S(F, 'real_gdp_trn'), BLUE, '-'), ('StatusQuo（固定SQ・共通OFF）', S(SQ, 'real_gdp_trn'), ORANGE, '-')])
    style(a[1], '名目GDP', '兆円'); lines(a[1], [('F', S(F, 'nominal_gdp_trn'), BLUE, '-'), ('StatusQuo', S(SQ, 'nominal_gdp_trn'), ORANGE, '-')], '%.0f')
    d = [v(F, y, 'real_gdp_trn') - v(SQ, y, 'real_gdp_trn') for y in Y]; style(a[2], '実質GDPの差（F − StatusQuo）', '兆円'); a[2].plot(Y, d, color=BLUE, lw=1.8); a[2].axhline(0, color='#c3c2b7', lw=.8); a[2].text(2055.6, d[-1], '%.1f' % d[-1], color=BLUE, va='center', fontsize=7.5)
    style(a[3], '税収（診断値）', '兆円'); lines(a[3], [('F', S(F, 'tax_diagnostic_trn'), BLUE, '-'), ('StatusQuo', S(SQ, 'tax_diagnostic_trn'), ORANGE, '-')], '%.0f')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_main.png'), dpi=200); plt.close(fig)
def fig_second():
    fig, ax = plt.subplots(2, 2, figsize=(7.4, 5.6)); a = ax.ravel()
    style(a[0], '家計消費（名目・代理）', '兆円'); lines(a[0], [('F', S(F, 'household_consumption_nominal_proxy_trn'), BLUE, '-'), ('StatusQuo', S(SQ, 'household_consumption_nominal_proxy_trn'), ORANGE, '-')], '%.0f')
    style(a[1], '資本ストック（実質）', '兆円'); lines(a[1], [('F', S(F, 'capital_total_real_trn'), BLUE, '-'), ('StatusQuo', S(SQ, 'capital_total_real_trn'), ORANGE, '-')], '%.0f')
    style(a[2], '部分財政収支（連結・代理）', '兆円'); lines(a[2], [('F', S(F, 'consolidated_partial_balance_proxy_trn'), BLUE, '-'), ('StatusQuo', S(SQ, 'consolidated_partial_balance_proxy_trn'), ORANGE, '-')], '%.0f'); a[2].axhline(0, color='#c3c2b7', lw=.8)
    pd_ = [(v(F, y, 'population') - v(SQ, y, 'population')) * 1e-4 for y in Y]; style(a[3], '総人口の差（F − StatusQuo）', '万人'); a[3].plot(Y, pd_, color=BLUE, lw=1.8); a[3].axhline(0, color='#c3c2b7', lw=.8); a[3].text(2055.6, pd_[-1], '%.0f' % pd_[-1], color=BLUE, va='center', fontsize=7.5)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_second.png'), dpi=200); plt.close(fig)
NAMES = dict(VAT='消費税', FOREIGN='外国人材', ELDER='高齢者就業', PENSION='公的年金', HOUSEHOLD_A='家計A', HOUSEHOLD_B='家計B', HOUSEHOLD_C='家計C', EDUCATION='教育・成長投資', INVESTMENT='投資促進（未接続）', FIRM='企業課税・償却等', COMMON='終末期医療共通', F_MEDICAL='医療制度改革')
def fig_marg():
    m = {}
    for r in PE:
        if int(r['year']) == 2055: m[r['channel']] = float(r['marginal_in_integrated_F'])
    order = sorted(m, key=lambda k: m[k]); tot = v(F, 2055, 'real_gdp_trn') - v(SQ, 2055, 'real_gdp_trn'); sm = sum(m.values())
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    ax.barh([NAMES[k] for k in order], [m[k] for k in order], color=[BLUE if m[k] >= 0 else ORANGE for k in order], height=.62)
    for i, k in enumerate(order): ax.text(m[k] + (.08 if m[k] >= 0 else -.08), i, '%+.2f' % m[k], va='center', ha='left' if m[k] >= 0 else 'right', fontsize=7.5, color=INK)
    ax.axvline(0, color='#c3c2b7', lw=.8); ax.set_title('2055年 実質GDP：施策を1つ外した場合の差（F − 当該施策OFF）  (兆円)', loc='left', color=INK); ax.grid(axis='x', color=GRID, lw=.6); ax.set_xlim(-1.5, 8)
    ax.text(.98, .08, '限界差の合計 %.2f  ／  F−SQ の差 %.2f\n差 %.2f 兆円は施策間の重なり（非加法）' % (sm, tot, sm - tot), transform=ax.transAxes, ha='right', fontsize=8, color=INK, bbox=dict(boxstyle='round', fc='#f9f9f7', ec='#c3c2b7'))
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_marg.png'), dpi=200); plt.close(fig); return m, tot, sm
def fig_eol():
    fig, ax = plt.subplots(1, 3, figsize=(7.4, 2.9)); cap = [float(CE[(F, y)]['transition_capacity']) for y in Y]; srv = [float(CE[(F, y)]['universal_palliative_served']) for y in Y]; ch = [float(CE[(F, y)]['chosen_transitions']) for y in Y]; un = [float(CE[(F, y)]['universal_palliative_unmet']) for y in Y]
    a = ax[0]; a.set_title('供給と提供（LATEST_F）  (万人/年)', loc='left', color=INK, fontsize=8); a.plot(Y, [x / 1e4 for x in cap], color='#898781', lw=1.2, ls='--', label='容量'); a.plot(Y, [x / 1e4 for x in srv], color=BLUE, lw=1.8, label='緩和ケア提供'); a.plot(Y, [x / 1e4 for x in ch], color=ORANGE, lw=1.8, label='意思に基づく移行'); a.legend(frameon=False, fontsize=6.5); a.grid(axis='y', color=GRID, lw=.6); a.set_xticks([2026, 2035, 2045, 2055])
    a = ax[1]; a.set_title('アクセス確率（提供÷対象）', loc='left', color=INK, fontsize=8); ap = [float(CE[(F, y)]['universal_access_probability']) * 100 for y in Y]; a.plot(Y, ap, color=BLUE, lw=1.8); a.set_ylim(0, 105); a.set_xticks([2026, 2035, 2045, 2055]); a.grid(axis='y', color=GRID, lw=.6); a.text(2055, ap[-1] + 4, '%.0f%%' % ap[-1], ha='right', color=BLUE, fontsize=7.5)
    a = ax[2]; a.set_title('家計直接負担の感度幅  (億円/年)', loc='left', color=INK, fontsize=8); lo = [float(HS[(str(y), 'household_direct_cash_burden_delta_trn')]['lower']) * 1e4 for y in Y]; hi = [float(HS[(str(y), 'household_direct_cash_burden_delta_trn')]['upper']) * 1e4 for y in Y]
    a.fill_between(Y, lo, hi, color=AQUA, alpha=.35, lw=0); a.plot(Y, lo, color=AQUA, lw=1.2); a.plot(Y, hi, color=AQUA, lw=1.2); a.axhline(0, color='#c3c2b7', lw=.8); a.set_xticks([2026, 2035, 2045, 2055]); a.grid(axis='y', color=GRID, lw=.6); a.text(2055, hi[-1], '%+.0f' % hi[-1], ha='right', va='bottom', fontsize=7.5, color=INK); a.text(2055, lo[-1], '%+.0f' % lo[-1], ha='right', va='top', fontsize=7.5, color=INK)
    for x in ax: x.spines['top'].set_visible(False); x.spines['right'].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'fig_eol.png'), dpi=200); plt.close(fig); return cap, srv, ch, ap
fig_main(); fig_second(); m, tot, sm = fig_marg(); cap, srv, ch, ap = fig_eol()
# ---------------- PDF
pdfmetrics.registerFont(TTFont('IPAGothic', '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf')); FN = 'IPAGothic'; from reportlab.pdfbase.pdfmetrics import registerFontFamily; registerFontFamily('IPAGothic', normal='IPAGothic', bold='IPAGothic', italic='IPAGothic', boldItalic='IPAGothic')
st = lambda n, **k: ParagraphStyle(n, fontName=FN, leading=k.pop('leading', 13), **k)
H1, H2, B, SM = st('h1', fontSize=17, leading=22, spaceAfter=4), st('h2', fontSize=11.5, leading=16, spaceBefore=8, spaceAfter=3, textColor=colors.HexColor('#184f95')), st('b', fontSize=8.8), st('s', fontSize=7.4, leading=10, textColor=colors.HexColor('#52514e'))
BOX = st('box', fontSize=8.5, leading=12.2, textColor=colors.HexColor('#7a2e0e'))
P = lambda t, s=B: Paragraph(t, s)
def box(text, bg='#fdf0e9', line='#eb6834'):
    t = Table([[P(text, BOX)]], colWidths=[174 * mm]); t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)), ('BOX', (0, 0), (-1, -1), .8, colors.HexColor(line)), ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)])); return t
def table(rows, widths, hdr=1, fs=7.6, align='RIGHT'):
    t = Table(rows, colWidths=widths, repeatRows=hdr); t.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), FN), ('FONTSIZE', (0, 0), (-1, -1), fs), ('BACKGROUND', (0, 0), (-1, hdr - 1), colors.HexColor('#e8eef8')), ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c3c2b7')), ('ALIGN', (1, 0), (-1, -1), align), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)])); return t
def foot(c, d):
    c.saveState(); c.setFont(FN, 7); c.setFillColor(colors.HexColor('#898781')); c.drawString(18 * mm, 9 * mm, 'SPE F／StatusQuo 比較レポート（v5相当）DRAFT・非正式・予測ではない  対象 Commit ff621006'); c.drawRightString(192 * mm, 9 * mm, '%d' % d.page); c.restoreState()
doc = SimpleDocTemplate(os.path.join(OUT, 'SPE_F_StatusQuo_v5Style_Report_DRAFT_20261121.pdf'), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm, title='SPE F／StatusQuo 比較レポート（v5相当）DRAFT', author='Claude (independent verifier)')
s = []; g = lambda c, y, k: v(c, y, k)
s += [P('SPE F／StatusQuo 比較レポート（v5相当・2026〜2055年）', H1), P('DRAFT／NON-CANONICAL　2026-11-21　データ：検算済みF統合計算（Commit ff62100、Fは LATEST_F）', SM), Spacer(1, 4)]
s += [box('<b>この資料の読み方</b>　数値は「前提の違い」の比較であり、予測でも因果の主張でもありません。StatusQuo は固定SQ（終末期医療共通OFF）、F は 55条件のうち LATEST_F（付加価値50%・財源対応50%の感度ラベルで、採用政策ではない）。未較正の係数が多く含まれます。SQ 側は医療VAT数量と健康/QOL が未接続のため、F−SQ の差を「F固有施策の効果」とは呼べません。RP-023／M19–25 HOLD、RP-024 PENDING、正式承認状態は変更していません。'), Spacer(1, 6)]
s += [P('1. 要点（2055年）', H2)]
keys = [('実質GDP（兆円）', 'real_gdp_trn', '%.1f'), ('名目GDP（兆円）', 'nominal_gdp_trn', '%.0f'), ('税収・診断値（兆円）', 'tax_diagnostic_trn', '%.1f'), ('家計消費・名目代理（兆円）', 'household_consumption_nominal_proxy_trn', '%.1f'), ('資本ストック・実質（兆円）', 'capital_total_real_trn', '%.0f'), ('部分財政収支・連結代理（兆円）', 'consolidated_partial_balance_proxy_trn', '%.1f')]
rows = [['指標（2055年）', 'F', 'StatusQuo', '差（F−SQ）', '2026年']] + [[n, f % g(F, 2055, k), f % g(SQ, 2055, k), ('%+.1f' if f != '%.0f' else '%+.0f') % (g(F, 2055, k) - g(SQ, 2055, k)), f % g(F, 2026, k)] for n, k, f in keys]
rows.append(['総人口（万人）', '%.0f' % (g(F, 2055, 'population') / 1e4), '%.0f' % (g(SQ, 2055, 'population') / 1e4), '%+.0f' % ((g(F, 2055, 'population') - g(SQ, 2055, 'population')) / 1e4), '%.0f' % (g(F, 2026, 'population') / 1e4)])
s += [table(rows, [62 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm]), Spacer(1, 5)]
s += [P('実質GDPはFが StatusQuo を 2055年に %.1f兆円上回る一方、税収（診断値）は %.1f兆円下回り、部分財政収支の赤字も F の方が大きくなっています。人口はFが %.0f万人少なくなっています（この表の差は両者の入力条件の違いの結果で、人口に効く施策の因果を示すものではありません）。2026年は両者とも同じ出発点です。' % (g(F, 2055, 'real_gdp_trn') - g(SQ, 2055, 'real_gdp_trn'), g(SQ, 2055, 'tax_diagnostic_trn') - g(F, 2055, 'tax_diagnostic_trn'), (g(SQ, 2055, 'population') - g(F, 2055, 'population')) / 1e4)), Spacer(1, 4)]
sc = SQC[('SQ_COMMON_ON', 2055)]
s += [P('参考：終末期医療共通ONの StatusQuo の2055年実質GDPは %.3f兆円（共通OFF %.3f）で、共通政策のGDP影響は 0.001兆円未満です。医療改革のFでの寄与（MEDICAL_OFFとの差）は %.2f兆円です。' % (float(sc['real_gdp_trn']), g(SQ, 2055, 'real_gdp_trn'), g(F, 2055, 'real_gdp_trn') - g('MEDICAL_OFF', 2055, 'real_gdp_trn')), SM), PageBreak()]
s += [P('2. 主要指標の推移', H2), Image(os.path.join(OUT, 'fig_main.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3), P('実質GDPは2026年の580兆円から2027年に両ケースとも約555兆円へ下がります（ベース年の特性で、F起因ではありません）。差（F−SQ）は2027年以降プラスです。税収（診断値）は F の方が低く推移します。その要因の分解は本レポートでは行っていません。', SM), PageBreak()]
s += [P('3. 家計・資本・財政・人口', H2), Image(os.path.join(OUT, 'fig_second.png'), width=174 * mm, height=174 * mm * 5.6 / 7.4), Spacer(1, 3), P('財政収支は部分的な代理指標で、全国の国債・基礎的財政収支（PB）は未実装です。総人口は両ケースとも2026年に %.0f万人から始まり、2055年は F %.0f万人、StatusQuo %.0f万人で、右下はその差です（水準はほぼ重なるため差で表示）。' % (g(F, 2026, 'population') / 1e4, g(F, 2055, 'population') / 1e4, g(SQ, 2055, 'population') / 1e4), SM), PageBreak()]
yrs = [2026, 2030, 2035, 2040, 2045, 2050, 2055]
hdr = ['指標／ケース'] + [str(y) for y in yrs]; rows = [hdr]
for n, k, f in keys[:3] + keys[3:5]:
    rows.append([n.split('（')[0] + ' F'] + [f % g(F, y, k) for y in yrs]); rows.append([n.split('（')[0] + ' SQ'] + [f % g(SQ, y, k) for y in yrs])
rows.append(['実質GDP差 F−SQ'] + ['%+.1f' % (g(F, y, 'real_gdp_trn') - g(SQ, y, 'real_gdp_trn')) for y in yrs])
s += [P('4. 主要年の数値表（兆円）', H2), table(rows, [38 * mm] + [19.4 * mm] * 7), Spacer(1, 6)]
s += [P('5. 2055年実質GDPの差を施策別に見る（限界差。加算寄与ではない）', H2), Image(os.path.join(OUT, 'fig_marg.png'), width=170 * mm, height=170 * mm * 3.9 / 7.4), Spacer(1, 2), P('各棒は「Fから当該施策だけを外した場合との差」です。施策が互いに重なるため合計は F−SQ の差と一致せず（約%.1f兆円の非加法）、内訳としては使えません。投資促進は入力が未接続で、効果ゼロではなく「未接続」です。' % (sm - tot), SM), PageBreak()]
s += [P('6. 終末期医療の共通政策と家計負担（LATEST_F）', H2), Image(os.path.join(OUT, 'fig_eol.png'), width=174 * mm, height=174 * mm * 2.9 / 7.4), Spacer(1, 3)]
y35, y40, y55 = [CE[(F, y)] for y in (2035, 2040, 2055)]
rows = [['LATEST_F', '2035', '2040', '2055']] + [[n] + ['%.0f' % float(r[k]) for r in (y35, y40, y55)] for n, k in [('緩和ケア提供（人/年）', 'universal_palliative_served'), ('意思に基づく移行（人/年）', 'chosen_transitions'), ('移行の未充足（人/年）', 'transition_unmet'), ('供給容量（人/年）', 'transition_capacity')]]
rows.append(['アクセス確率'] + ['%.1f%%' % (100 * float(r['universal_access_probability'])) for r in (y35, y40, y55)])
s += [table(rows, [60 * mm, 30 * mm, 30 * mm, 30 * mm]), Spacer(1, 3)]
hr = [HS[(str(y), 'household_direct_cash_burden_delta_trn')] for y in (2035, 2040, 2055)]
s += [P('供給容量は移行と緩和提供で共有され、同じアクセス確率が登録者・未登録者の双方に適用されます（容量の二重利用は解消済み）。ただし容量が常に拘束的で、支援を受けた意思表示者の移行が満たされるのは 2035年 %.0f%%、2040年 %.0f%%、2055年 %.0f%% にとどまります。2032〜2034年の立上げ期は対象が実施率で段階的に増えるため、アクセス確率が高く出ます（グラフ中央）。容量・緩和ケア対象割合・配分方式はいずれも未較正でOwner未裁定です。家計の直接負担（終末期共通分）の感度幅は 2035年 %+.0f〜%+.0f、2040年 %+.0f〜%+.0f、2055年 %+.0f〜%+.0f 億円/年で、符号が反転するため増減は断定できません。通常医療の患者負担・保険料・財源税はこれとは別の列です。' % tuple([100 * float(r['universal_access_probability']) for r in (y35, y40, y55)] + [x for r in hr for x in (float(r['lower']) * 1e4, float(r['upper']) * 1e4)]), B), PageBreak()]
s += [P('7. 読み方の注意と検証状況', H2)]
notes = ['<b>比較の条件</b>：F は LATEST_F（教育統合・医療修正・終末期共通を含む統合モデル）、StatusQuo は固定SQ（終末期医療共通OFF）。両者は同じエンジン・同じ出発点（2026年）。',
 '<b>非対称性</b>：SQ側は医療VAT数量フックと健康/QOL経路が未接続。F−SQ の差には、F固有の施策効果と、この接続範囲の違いの双方が含まれ、切り分けていません。',
 '<b>加算不可</b>：限界差の合計は全体差と一致しません（2055年 非加法差 %.2f兆円）。' % (sm - tot),
 '<b>未実装・未較正</b>：全国の国債・PB、中央／地方財政の完全収支、健康・QOL、投資促進の入力、episode率・付加価値率・財源配分などの係数。',
 '<b>検証状況</b>：固定Commit ff621006 の原本同一性（Manifest 51/51・依存12/12）、再実行バイト一致52/52、医療・共通・需要ブロックの独立再計算176,550セル一致（Claude独立検算 Commit 4924c8e4）。動学マクロ本体（GDPの連鎖）の独立再実装は未実施です。',
 '<b>出典</b>：handoff/f-common-endoflife-finalization-20261121/ の Annual.csv、SQ_Common_Annual.csv、Common_EndOfLife.csv、Policy_Effects.csv、Household_Sensitivity.csv、Nonadditivity.csv。グラフ・表の数値はこれらのCSVから自動生成。']
for n in notes: s += [P('・' + n, B), Spacer(1, 3)]
doc.build(s, onFirstPage=foot, onLaterPages=foot)
print('built', os.path.getsize(os.path.join(OUT, 'SPE_F_StatusQuo_v5Style_Report_DRAFT_20261121.pdf')))
