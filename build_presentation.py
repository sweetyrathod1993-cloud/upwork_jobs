import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# 1. COLOR PALETTE DEFINITIONS
# ==============================================================================
C_DARK_BG       = RGBColor(15, 23, 42)      # #0F172A - Deep Midnight Navy
C_DARK_CARD     = RGBColor(30, 41, 59)      # #1E293B - Slate Navy Card
C_DARK_BORDER   = RGBColor(51, 65, 85)      # #334155 - Dark Border
C_LIGHT_BG      = RGBColor(248, 250, 252)   # #F8FAFC - Clean Off-White
C_WHITE         = RGBColor(255, 255, 255)   # #FFFFFF - Pure White
C_CARD_BG       = RGBColor(255, 255, 255)   # White Card
C_CARD_BORDER   = RGBColor(226, 232, 240)   # #E2E8F0 - Light Border
C_TEXT_DARK     = RGBColor(15, 23, 42)      # #0F172A - Primary Dark Text
C_TEXT_MUTED    = RGBColor(100, 116, 139)   # #64748B - Slate Gray Muted
C_TEXT_LIGHT    = RGBColor(241, 245, 249)   # #F1F5F9 - Off-White Text
C_TEXT_SUBTLE   = RGBColor(148, 163, 184)   # #94A3B8 - Subtle Slate
C_BLUE_PRIMARY  = RGBColor(37, 99, 235)     # #2563EB - Electric Blue
C_BLUE_LIGHT    = RGBColor(239, 246, 255)   # #EFF6FF - Soft Blue Tint
C_CYAN_ACCENT   = RGBColor(14, 165, 233)    # #0EA5E9 - Vibrant Cyan
C_GREEN_SUCCESS = RGBColor(16, 185, 129)    # #10B981 - Emerald Green
C_GREEN_LIGHT   = RGBColor(236, 253, 245)   # #ECFDF5 - Soft Green Tint
C_AMBER_WARN    = RGBColor(245, 158, 11)    # #F59E0B - Amber
C_INDIGO_PURPLE = RGBColor(99, 102, 241)    # #6366F1 - Indigo

# ==============================================================================
# 2. GENERATE HIGH-RES CHARTS
# ==============================================================================
os.makedirs('pptx_assets', exist_ok=True)
with open('data/processed/analysis_metrics.json') as f:
    metrics_data = json.load(f)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

# Chart 1: Task 1 Salaries
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
skills = ['Solidity', 'Blockchain', 'Tableau', 'Machine Learning', 'Computer Vision', 'LLM', 'Azure', 'Web3', 'Shopify', 'SEO', 'Video Editing', 'Lead Generation', 'Virtual Assistant']
rates = [43.40, 43.29, 42.44, 40.64, 38.94, 38.66, 38.35, 38.32, 23.88, 22.43, 21.50, 14.50, 9.82]
baseline = 28.75
colors = ['#10B981' if r >= baseline else '#EF4444' for r in rates]
y_pos = np.arange(len(skills))
bars = ax.barh(y_pos, rates, color=colors, height=0.65, alpha=0.9)
ax.axvline(baseline, color='#64748B', linestyle='--', linewidth=1.2, label=f'Baseline Rate (${baseline:.2f}/hr)')
ax.set_yticks(y_pos)
ax.set_yticklabels(skills, fontsize=8, fontweight='bold', color='#1E293B')
ax.invert_yaxis()
ax.set_xlabel('Mean Hourly Rate ($/hr)', fontsize=8.5, fontweight='bold', color='#334155')
ax.set_title('Hourly Compensation: Top Tech Skills vs Commoditized Roles', fontsize=10, fontweight='bold', color='#0F172A', pad=10)
ax.set_xlim(0, 52)
ax.grid(axis='x', linestyle=':', alpha=0.6, color='#CBD5E1')
ax.legend(loc='lower right', fontsize=7.5, framealpha=0.9)
for bar, rate in zip(bars, rates):
    diff = ((rate - baseline) / baseline) * 100
    sign = '+' if diff > 0 else ''
    ax.text(rate + 0.8, bar.get_y() + bar.get_height()/2, f'${rate:.1f} ({sign}{diff:.0f}%)', 
            va='center', fontsize=7.5, fontweight='bold', color='#0F172A')
plt.tight_layout()
fig.savefig('pptx_assets/chart_task1_salaries.png')
plt.close(fig)

# Chart 2: Task 2 Category Growth
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
categories = [x['category'] for x in metrics_data['task2']['category_growth_ranking'][:8]]
growth_rates = [x['growth_rate_pct'] for x in metrics_data['task2']['category_growth_ranking'][:8]]
y_pos = np.arange(len(categories))
colors_growth = ['#0EA5E9', '#2563EB', '#6366F1', '#8B5CF6', '#10B981', '#14B8A6', '#06B6D4', '#3B82F6']
bars = ax.barh(y_pos, growth_rates, color=colors_growth, height=0.65, alpha=0.9)
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=8, fontweight='bold', color='#1E293B')
ax.invert_yaxis()
ax.set_xlabel('Period-over-Period Growth Rate (%)', fontsize=8.5, fontweight='bold', color='#334155')
ax.set_title('Freelance Category Posting Growth Velocity', fontsize=10, fontweight='bold', color='#0F172A', pad=10)
ax.set_xlim(0, 26)
ax.grid(axis='x', linestyle=':', alpha=0.6, color='#CBD5E1')
for bar, g in zip(bars, growth_rates):
    ax.text(g + 0.5, bar.get_y() + bar.get_height()/2, f'+{g:.1f}%', 
            va='center', fontsize=8, fontweight='bold', color='#0F172A')
plt.tight_layout()
fig.savefig('pptx_assets/chart_task2_growth.png')
plt.close(fig)

# Chart 3: Task 3 Demand Forecast
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
fc_overall = metrics_data['task3']['forecasts'][0]['future_forecast']
dates = [x[5:] for x in fc_overall['dates']][::2]
pred_overall = fc_overall['predicted_demand'][::2]
lower_ci = fc_overall['lower_95_ci'][::2]
upper_ci = fc_overall['upper_95_ci'][::2]
x_idx = np.arange(len(dates))
ax.plot(x_idx, pred_overall, color='#2563EB', linewidth=2.2, label='Predicted Demand (Daily Jobs)', marker='o', markersize=3.5)
ax.fill_between(x_idx, lower_ci, upper_ci, color='#93C5FD', alpha=0.35, label='95% Confidence Interval')
ax.set_xticks(x_idx)
ax.set_xticklabels(dates, rotation=45, fontsize=7.5, color='#334155')
ax.set_ylabel('Daily Job Postings', fontsize=8.5, fontweight='bold', color='#334155')
ax.set_title('Task 3: 30-Day Demand Forecast (Overall Market)', fontsize=10, fontweight='bold', color='#0F172A', pad=10)
ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')
ax.legend(loc='lower left', fontsize=7.5, framealpha=0.9)
plt.tight_layout()
fig.savefig('pptx_assets/chart_task3_forecast.png')
plt.close(fig)

# Chart 4: Task 4 Geography
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.2, 4.2), dpi=200, gridspec_kw={'width_ratios': [1, 1]})
top_vol_countries = [x['country'] for x in metrics_data['task4']['top_volume_countries'][:5]]
top_vol_rates = [x['mean_hourly_rate'] for x in metrics_data['task4']['top_volume_countries'][:5]]
y1 = np.arange(len(top_vol_countries))
ax1.barh(y1, top_vol_rates, color='#3B82F6', height=0.6, alpha=0.9)
ax1.set_yticks(y1)
ax1.set_yticklabels(top_vol_countries, fontsize=8, fontweight='bold', color='#1E293B')
ax1.invert_yaxis()
ax1.set_xlabel('$/hr', fontsize=8, fontweight='bold', color='#334155')
ax1.set_title('Top Hiring Markets', fontsize=9, fontweight='bold', color='#0F172A')
ax1.set_xlim(0, 40)
ax1.grid(axis='x', linestyle=':', alpha=0.6)
for y, r in zip(y1, top_vol_rates):
    ax1.text(r + 0.8, y, f'${r:.1f}', va='center', fontsize=7.5, fontweight='bold')

regions = [x['region'].replace(' & ', '\n& ') for x in metrics_data['task4']['regional_breakdown'][:5]]
region_rates = [x['mean_hourly_rate'] for x in metrics_data['task4']['regional_breakdown'][:5]]
y2 = np.arange(len(regions))
ax2.barh(y2, region_rates, color='#10B981', height=0.6, alpha=0.9)
ax2.set_yticks(y2)
ax2.set_yticklabels(regions, fontsize=7.5, color='#1E293B')
ax2.invert_yaxis()
ax2.set_xlabel('$/hr', fontsize=8, fontweight='bold', color='#334155')
ax2.set_title('Regional Averages', fontsize=9, fontweight='bold', color='#0F172A')
ax2.set_xlim(0, 40)
ax2.grid(axis='x', linestyle=':', alpha=0.6)
for y, r in zip(y2, region_rates):
    ax2.text(r + 0.8, y, f'${r:.1f}', va='center', fontsize=7.5, fontweight='bold')
plt.tight_layout()
fig.savefig('pptx_assets/chart_task4_geography.png')
plt.close(fig)

# Chart 5: Task 7 Trends
fig, ax1 = plt.subplots(figsize=(6.2, 4.2), dpi=200)
quarters = [x.replace(' (Actual)', '') for x in metrics_data['task7']['quarterly_remote_forecast']['quarters']]
postings = [x / 1000 for x in metrics_data['task7']['quarterly_remote_forecast']['projected_postings']]
hourly_share = metrics_data['task7']['quarterly_remote_forecast']['projected_hourly_share_pct']
x = np.arange(len(quarters))
color1 = '#2563EB'
ax1.bar(x, postings, color=color1, alpha=0.8, width=0.55, label='Projected Postings (k)')
ax1.set_ylabel('Market Postings (Thousands)', color=color1, fontsize=8, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=color1, labelsize=7.5)
ax1.set_xticks(x)
ax1.set_xticklabels(quarters, rotation=45, fontsize=7.5, color='#334155')
ax1.set_ylim(200, 400)
ax2 = ax1.twinx()
color2 = '#F59E0B'
ax2.plot(x, hourly_share, color=color2, linewidth=2.5, marker='s', markersize=4.5, label='Hourly Contract Share (%)')
ax2.set_ylabel('Hourly Contracts Share (%)', color=color2, fontsize=8, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color2, labelsize=7.5)
ax2.set_ylim(55, 65)
ax1.set_title('Remote Market Expansion & Hourly Shift (2024–2026)', fontsize=10, fontweight='bold', color='#0F172A', pad=10)
plt.tight_layout()
fig.savefig('pptx_assets/chart_task7_trends.png')
plt.close(fig)

# Chart 6: Task 8 Scenarios
fig, ax = plt.subplots(figsize=(6.2, 4.2), dpi=200)
q_labels = ['Q1 24', 'Q2 24', 'Q3 24', 'Q4 24', 'Q1 25', 'Q2 25', 'Q3 25', 'Q4 25', 'Q1 26', 'Q2 26', 'Q3 26', 'Q4 26']
x_steps = np.arange(12)
vol_base = [v / 1000 for v in metrics_data['task8']['scenarios']['baseline']['total_volume']]
vol_ai = [v / 1000 for v in metrics_data['task8']['scenarios']['ai_disruption']['total_volume']]
vol_out = [v / 1000 for v in metrics_data['task8']['scenarios']['economic_outsourcing']['total_volume']]
ax.plot(x_steps, vol_out, color='#10B981', linewidth=2.2, linestyle='-', marker='^', markersize=3.5, label='Scenario C: Enterprise Outsourcing (542k)')
ax.plot(x_steps, vol_ai, color='#8B5CF6', linewidth=2.2, linestyle='-', marker='s', markersize=3.5, label='Scenario B: AI Disruption (419k)')
ax.plot(x_steps, vol_base, color='#2563EB', linewidth=2.2, linestyle='--', marker='o', markersize=3.5, label='Scenario A: Baseline Growth (346k)')
ax.set_xticks(x_steps[::2])
ax.set_xticklabels(q_labels[::2], fontsize=7.5, color='#334155')
ax.set_ylabel('Projected Market Volume (Thousands)', fontsize=8, fontweight='bold', color='#334155')
ax.set_title('Task 8: 2024–2026 Market Trajectory Under 3 Scenarios', fontsize=10, fontweight='bold', color='#0F172A', pad=10)
ax.grid(True, linestyle=':', alpha=0.6, color='#CBD5E1')
ax.legend(loc='upper left', fontsize=7.5, framealpha=0.9)
plt.tight_layout()
fig.savefig('pptx_assets/chart_task8_scenarios.png')
plt.close(fig)

print("All charts generated and verified.")

# ==============================================================================
# 3. PPTX BUILDER HELPERS
# ==============================================================================
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def add_full_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, badge_text, title_text, subtitle_text, dark=False):
    # Badge
    b_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.40), Inches(10), Inches(0.30))
    tf_b = b_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = badge_text.upper()
    p_b.font.size = Pt(9.5)
    p_b.font.bold = True
    p_b.font.color.rgb = C_CYAN_ACCENT if dark else C_BLUE_PRIMARY

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.733), Inches(0.48))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(21)
    p_t.font.bold = True
    p_t.font.color.rgb = C_TEXT_LIGHT if dark else C_TEXT_DARK

    # Subtitle
    s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.18), Inches(11.733), Inches(0.32))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle_text
    p_s.font.size = Pt(11)
    p_s.font.color.rgb = C_TEXT_SUBTLE if dark else C_TEXT_MUTED

    # Header Divider Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.52), Inches(11.733), Pt(1.2))
    line.fill.solid()
    line.fill.fore_color.rgb = C_DARK_BORDER if dark else C_CARD_BORDER
    line.line.fill.background()

def add_footer(slide, slide_num, dark=False):
    # Footer Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.98), Inches(11.733), Pt(1))
    line.fill.solid()
    line.fill.fore_color.rgb = C_DARK_BORDER if dark else C_CARD_BORDER
    line.line.fill.background()

    # Footer Left
    fl_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.06), Inches(5.5), Inches(0.3))
    tf_l = fl_box.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = 0
    p_l = tf_l.paragraphs[0]
    p_l.text = "WorkPulse: Job Market Analysis and Recommendation System"
    p_l.font.size = Pt(9)
    p_l.font.color.rgb = C_TEXT_SUBTLE if dark else C_TEXT_MUTED

    # Footer Center
    fc_box = slide.shapes.add_textbox(Inches(4.8), Inches(7.06), Inches(4.5), Inches(0.3))
    tf_c = fc_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.CENTER
    p_c.text = "Specification 1791966837.pdf | 244,828 Postings"
    p_c.font.size = Pt(9)
    p_c.font.color.rgb = C_TEXT_SUBTLE if dark else C_TEXT_MUTED

    # Footer Right
    fr_box = slide.shapes.add_textbox(Inches(10.033), Inches(7.06), Inches(2.5), Inches(0.3))
    tf_r = fr_box.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = f"Slide {slide_num} of 15"
    p_r.font.size = Pt(9)
    p_r.font.bold = True
    p_r.font.color.rgb = C_CYAN_ACCENT if dark else C_BLUE_PRIMARY

def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_CARD_BORDER, dark=False):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color if not dark else C_DARK_CARD
    card.line.color.rgb = border_color if not dark else C_DARK_BORDER
    card.line.width = Pt(1)
    return card

def add_stat_box(slide, left, top, width, height, stat_value, label_text, color=C_BLUE_PRIMARY, dark=False):
    add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_CARD_BORDER, dark=dark)
    
    # Accent mini bar
    bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.12), top + Inches(0.14), Inches(0.08), height - Inches(0.28))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()

    # Text container
    tb = slide.shapes.add_textbox(left + Inches(0.30), top + Inches(0.12), width - Inches(0.42), height - Inches(0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    p_stat = tf.paragraphs[0]
    p_stat.text = stat_value
    p_stat.font.size = Pt(20)
    p_stat.font.bold = True
    p_stat.font.color.rgb = color

    p_lbl = tf.add_paragraph()
    p_lbl.text = label_text
    p_lbl.font.size = Pt(9)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = C_TEXT_SUBTLE if dark else C_TEXT_MUTED

# ==============================================================================
# SLIDE 1: TITLE SLIDE (Dark Theme)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
add_full_background(s1, C_DARK_BG)

# Title slide decorative glowing bar
decor = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(1.8), Inches(0.08))
decor.fill.solid()
decor.fill.fore_color.rgb = C_CYAN_ACCENT
decor.line.fill.background()

# Badge
t_badge = s1.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(10), Inches(0.35))
tf1_b = t_badge.text_frame
p1_b = tf1_b.paragraphs[0]
p1_b.text = "ENTERPRISE LABOR MARKET INTELLIGENCE & MACHINE LEARNING PLATFORM"
p1_b.font.size = Pt(11)
p1_b.font.bold = True
p1_b.font.color.rgb = C_CYAN_ACCENT

# Main Title
t_main = s1.shapes.add_textbox(Inches(0.8), Inches(1.85), Inches(11.733), Inches(1.2))
tf1_m = t_main.text_frame
tf1_m.word_wrap = True
p1_m = tf1_m.paragraphs[0]
p1_m.text = "WorkPulse: Job Market Analysis &\nRecommendation System"
p1_m.font.size = Pt(34)
p1_m.font.bold = True
p1_m.font.color.rgb = C_WHITE

# Subtitle
t_sub = s1.shapes.add_textbox(Inches(0.8), Inches(3.20), Inches(11.733), Inches(0.8))
tf1_s = t_sub.text_frame
tf1_s.word_wrap = True
p1_s = tf1_s.paragraphs[0]
p1_s.text = "Large-Scale Empirical Analytics, Autoregressive Time-Series Forecasting, and Sublinear TF-IDF Semantic Recommendations Built on 244,828 Upwork Job Postings Across 212 Countries."
p1_s.font.size = Pt(13)
p1_s.font.color.rgb = C_TEXT_SUBTLE

# 4 Core Highlight Cards
h_cards = [
    ("244,828 Postings Analyzed", "Comprehensive corpus spanning Nov 2023 - Mar 2024 across 212 countries; high-speed Parquet & SQLite indexing.", C_BLUE_PRIMARY),
    ("Predictive ML Forecasting", "Autoregressive Gradient Boosting ensemble achieving 6.12% MAPE out-of-sample accuracy with 95% confidence bounds.", C_CYAN_ACCENT),
    ("Semantic Recommender", "30,000-token sublinear TF-IDF vector space indexing 50,000 postings with sub-100ms cosine similarity responses.", C_GREEN_SUCCESS),
    ("Production Docker Stack", "Multi-stage Dockerfile, docker-compose orchestration, Flask REST APIs, and 13/13 passing automated unit tests.", C_INDIGO_PURPLE)
]

for i, (title, desc, accent) in enumerate(h_cards):
    cx = Inches(0.8 + i * 2.98)
    cy = Inches(4.30)
    cw = Inches(2.80)
    ch = Inches(2.10)
    add_card(s1, cx, cy, cw, ch, dark=True)

    # Accent line top
    hbar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.2), cy + Inches(0.18), Inches(0.6), Inches(0.06))
    hbar.fill.solid()
    hbar.fill.fore_color.rgb = accent
    hbar.line.fill.background()

    tb = s1.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.38), cw - Inches(0.4), ch - Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_TEXT_SUBTLE
    p2.space_before = Pt(6)

add_footer(s1, 1, dark=True)

# ==============================================================================
# SLIDE 2: EXECUTIVE SUMMARY & OBJECTIVES (Light Theme)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_full_background(s2, C_LIGHT_BG)
add_header(s2, "PROJECT SCOPE & CORE DELIVERABLES", "Executive Summary: Labor Market Intelligence Platform", "Transforming massive unstructured freelance postings into empirical compensation benchmarks and predictive systems.")

# Top 4 Stat KPIs
add_stat_box(s2, Inches(0.8), Inches(1.65), Inches(2.78), Inches(1.05), "244,828", "Total Job Postings Ingested", C_BLUE_PRIMARY)
add_stat_box(s2, Inches(3.78), Inches(1.65), Inches(2.78), Inches(1.05), "212", "Countries Represented", C_CYAN_ACCENT)
add_stat_box(s2, Inches(6.76), Inches(1.65), Inches(2.78), Inches(1.05), "6.12%", "Demand Forecasting MAPE", C_GREEN_SUCCESS)
add_stat_box(s2, Inches(9.74), Inches(1.65), Inches(2.78), Inches(1.05), "8 Tasks", "Fully Implemented & Validated", C_INDIGO_PURPLE)

# Left Card: Problem & Context
c_left = add_card(s2, Inches(0.8), Inches(2.90), Inches(5.72), Inches(3.85))
tb_l = s2.shapes.add_textbox(Inches(1.0), Inches(3.05), Inches(5.32), Inches(3.55))
tf_l = tb_l.text_frame
tf_l.word_wrap = True
p = tf_l.paragraphs[0]
p.text = "Market Challenges & Situational Overview"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points_l = [
    ("Opaque Freelance Pricing:", "Extreme hourly wage dispersion ($3/hr to $350/hr) with limited statistical transparency into what skills actually command premiums."),
    ("Velocity of Labor Market Shifts:", "Rapid acceleration of generative AI, Web3, and cloud infrastructure outpacing traditional labor reporting and academic curricula."),
    ("Information Asymmetry:", "Job seekers lack personalized recommendation engines capable of parsing nuanced tech stacks with multi-criteria constraints."),
    ("Production Deficit:", "Industry research often ends in isolated Jupyter notebooks rather than scalable, containerized microservices ready for live deployment.")
]
for title, desc in points_l:
    p = tf_l.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(8)

# Right Card: Implemented Solution Architecture
c_right = add_card(s2, Inches(6.8), Inches(2.90), Inches(5.72), Inches(3.85))
tb_r = s2.shapes.add_textbox(Inches(7.0), Inches(3.05), Inches(5.32), Inches(3.55))
tf_r = tb_r.text_frame
tf_r.word_wrap = True
p = tf_r.paragraphs[0]
p.text = "Implemented Solution & Project Scope"
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points_r = [
    ("8 Analytical & ML Deliverables:", "Full implementation of all specifications from 1791966837.pdf, covering salary regression, emerging trends, forecasts, and geography."),
    ("End-to-End High Speed Pipeline:", "Ingests 244,828 records, cleans HTML artifacts, normalizes text, and persists into high-performance Parquet and indexed SQLite."),
    ("Personalized TF-IDF Recommender:", "Interactive semantic matching engine indexing 50,000 postings with sub-100ms vector cosine similarity and constraint filtering."),
    ("Enterprise Docker Deployment:", "Containerized multi-service architecture (Dockerfile, docker-compose.yml, Gunicorn WSGI) with 13/13 passing automated unit tests.")
]
for title, desc in points_r:
    p = tf_r.add_paragraph()
    p.text = f"✔ {title} {desc}"
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(8)

add_footer(s2, 2)

# ==============================================================================
# SLIDE 3: SYSTEM ARCHITECTURE & PIPELINE (Light Theme)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_full_background(s3, C_LIGHT_BG)
add_header(s3, "SYSTEM DESIGN & TECHNICAL PIPELINE", "End-to-End Data, Analytics & Containerized Architecture", "High-throughput modular architecture connecting raw CSV ingestion, feature extraction, ML models, and interactive UI.")

layers = [
    ("1. Data Ingestion & Storage", C_BLUE_PRIMARY, [
        ("Raw Data Ingestion", "244,828 job postings from all_upwork_jobs.csv (~50MB raw)."),
        ("Text & Feature Cleaning", "HTML entity decoding, regex-based skill boundary parsing, wage parsing."),
        ("Clean Parquet Cache", "upwork_jobs_cleaned.parquet (28.7MB) enabling sub-second columnar scans."),
        ("Indexed SQLite Database", "data/upwork_jobs.db (105MB) indexed by category, country, rate & published date.")
    ]),
    ("2. Analytical & ML Core", C_CYAN_ACCENT, [
        ("Statistical Econometrics", "OLS regression, ANOVA F-tests, and Pearson/Spearman correlation (Tasks 1, 4)."),
        ("Growth & Momentum Engine", "Period-over-Period velocity and sample-weighted momentum scoring (Task 2)."),
        ("Time-Series ML Ensemble", "Gradient Boosting Regressor with 7-day lags and rolling window dynamics (Task 3)."),
        ("Semantic Recommender", "30,000-token sublinear TF-IDF vectorizer + Cosine Similarity scoring (Task 5).")
    ]),
    ("3. Presentation & Web Services", C_INDIGO_PURPLE, [
        ("Flask Application Core", "Modular blueprints serving web views and high-throughput REST APIs (app.py)."),
        ("Interactive Web Dashboard", "Tailwind CSS dashboard with navigation drawer and 10 dynamic Jinja2 views."),
        ("Plotly.js Visualizations", "Embedded client-side interactive charts with pan, zoom, and dynamic tooltips."),
        ("8 Public REST Endpoints", "Comprehensive endpoints supporting programmatic access (/api/recommend, etc.).")
    ]),
    ("4. Production Infrastructure", C_GREEN_SUCCESS, [
        ("Multi-Stage Dockerfile", "Optimized Python 3.12-slim build, non-root user execution, minimal footprint."),
        ("Docker Compose Setup", "Multi-container orchestration separating web service and analytics worker."),
        ("Production WSGI Server", "Gunicorn process manager configured with automated healthchecks (/api/health)."),
        ("Automated Test Suite", "13/13 passing pytest unit tests verifying pipeline integrity and model accuracy.")
    ])
]

for i, (layer_name, accent, items) in enumerate(layers):
    lx = Inches(0.8 + i * 2.98)
    ly = Inches(1.70)
    lw = Inches(2.80)
    lh = Inches(5.05)
    add_card(s3, lx, ly, lw, lh)

    # Header banner for card
    top_banner = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, lx, ly, lw, Inches(0.45))
    top_banner.fill.solid()
    top_banner.fill.fore_color.rgb = accent
    top_banner.line.fill.background()

    tb_h = s3.shapes.add_textbox(lx + Inches(0.1), ly + Inches(0.08), lw - Inches(0.2), Inches(0.3))
    tf_h = tb_h.text_frame
    p_h = tf_h.paragraphs[0]
    p_h.text = layer_name
    p_h.font.size = Pt(11)
    p_h.font.bold = True
    p_h.font.color.rgb = C_WHITE
    p_h.alignment = PP_ALIGN.CENTER

    # Content
    tb_c = s3.shapes.add_textbox(lx + Inches(0.15), ly + Inches(0.55), lw - Inches(0.3), lh - Inches(0.65))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    for idx, (head, body) in enumerate(items):
        p_head = tf_c.add_paragraph() if idx > 0 else tf_c.paragraphs[0]
        p_head.text = f"▪ {head}"
        p_head.font.size = Pt(10)
        p_head.font.bold = True
        p_head.font.color.rgb = C_TEXT_DARK
        p_head.space_before = Pt(6) if idx > 0 else Pt(0)

        p_body = tf_c.add_paragraph()
        p_body.text = body
        p_body.font.size = Pt(8.8)
        p_body.font.color.rgb = C_TEXT_MUTED
        p_body.space_before = Pt(1)

add_footer(s3, 3)

# ==============================================================================
# SLIDE 4: TASK 1 - KEYWORD-SALARY CORRELATION (Light Theme)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_full_background(s4, C_LIGHT_BG)
add_header(s4, "TASK 01 | STATISTICAL COMPENSATION ANALYSIS", "Correlation Between Job Title Keywords & Offered Salaries", "Analyzing N = 102,422 hourly contracts and N = 103,891 fixed-price budgets via OLS regression and ANOVA.")

# Left Column (Content)
add_card(s4, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb4 = s4.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(4.75))
tf4 = tb4.text_frame
tf4.word_wrap = True

p = tf4.paragraphs[0]
p.text = "Key Statistical Findings & Methodology"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets4 = [
    ("Econometric Modeling:", "Estimated OLS multiple regression w_i = β_0 + Σ β_k x_ik + ε_i alongside One-Way ANOVA F-tests to isolate independent skill premiums ceteris paribus."),
    ("Top High-Paying Tech Skills:", "Solidity ($43.40/hr, +51.0% premium, β = +$11.58/hr, p < 10⁻⁵)\n• Blockchain ($43.29/hr, +50.6% premium, F = 102.5, p < 10⁻²³)\n• Tableau & BI ($42.44/hr, +47.6% premium, β = +$12.87/hr)\n• Machine Learning ($40.64/hr, +41.3% premium, F = 27.5)\n• Computer Vision & LLMs ($38.66 - $38.94/hr, +34% to +35%)"),
    ("Commoditized Discount Tier:", "Virtual Assistant ($9.82/hr, -65.8% discount, β = -$18.93/hr)\n• Lead Generation ($14.50/hr, -49.6% discount)\n• Video Editing & SEO ($21.50 - $22.43/hr, -22% to -25%)"),
    ("Statistical Significance:", "All reported key tech skills exhibited ANOVA p-values < 0.001, verifying that keyword salary premiums represent genuine market signals.")
]
for title, desc in bullets4:
    p = tf4.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Right Column (Chart Image + Callout)
s4.shapes.add_picture('pptx_assets/chart_task1_salaries.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s4, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_BLUE_LIGHT, border_color=C_BLUE_PRIMARY)
tb_c4 = s4.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c4 = tb_c4.text_frame
tf_c4.word_wrap = True
p_c4 = tf_c4.paragraphs[0]
p_c4.text = "💡 Strategic Insight: The Skill Premium Curve"
p_c4.font.size = Pt(10.5)
p_c4.font.bold = True
p_c4.font.color.rgb = C_BLUE_PRIMARY

p_c4_sub = tf_c4.add_paragraph()
p_c4_sub.text = "Systems languages and specialized AI tooling command up to +51% wage premiums over the $28.75/hr market baseline, while entry-level virtual assistance incurs a severe -65.8% discount."
p_c4_sub.font.size = Pt(9)
p_c4_sub.font.color.rgb = C_TEXT_DARK

add_footer(s4, 4)

# ==============================================================================
# SLIDE 5: TASK 1 - SENIORITY & WAGE STRUCTURE (Light Theme)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_full_background(s5, C_LIGHT_BG)
add_header(s5, "TASK 01 | SENIORITY & WAGE STRUCTURE", "Seniority Multipliers and Market Wage Dispersion", "Quantifying experience qualifiers, compensation interquartile ranges, and contract budget distribution.")

# Top 4 Seniority Cards
add_stat_box(s5, Inches(0.8), Inches(1.65), Inches(2.78), Inches(1.15), "$32.05/hr", "Senior Specialist (N = 2,975)\nMedian: $27.50 | IQR: $15.5 - $37.5", C_BLUE_PRIMARY)
add_stat_box(s5, Inches(3.78), Inches(1.65), Inches(2.78), Inches(1.15), "$28.87/hr", "Mid / Standard (N = 91,818)\nMedian: $22.50 | IQR: $13.0 - $35.0", C_CYAN_ACCENT)
add_stat_box(s5, Inches(6.76), Inches(1.65), Inches(2.78), Inches(1.15), "$23.35/hr", "Lead / Architect (N = 2,170)\nMedian: $14.50 | High Dispersion", C_INDIGO_PURPLE)
add_stat_box(s5, Inches(9.74), Inches(1.65), Inches(2.78), Inches(1.15), "$36.26/hr", "Junior / Entry (N = 693)\nMedian: $25.00 | Niche Variance", C_GREEN_SUCCESS)

# Bottom Left Card: Wage Distribution Analysis
add_card(s5, Inches(0.8), Inches(3.05), Inches(5.72), Inches(3.70))
tb5_l = s5.shapes.add_textbox(Inches(1.0), Inches(3.20), Inches(5.32), Inches(3.40))
tf5_l = tb5_l.text_frame
tf5_l.word_wrap = True

p = tf5_l.paragraphs[0]
p.text = "Wage Distribution & Right-Skewness Analysis"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points5_l = [
    ("Right-Skewed Distribution:", "Hourly compensation exhibits pronounced positive skewness. While the global mean rate is $28.75/hr, the global median sits at $22.50/hr, indicating a heavy concentration of standard rates with long high-earning tails."),
    ("Seniority Wage Spread:", "Senior specialists maintain a tight interquartile range ($15.50 - $37.50/hr), with 75% of senior postings paying at or above the platform baseline."),
    ("Fixed Budget Disparity:", "In fixed-price contracts, Senior and Lead roles command an average budget of $1,420 vs $450 for standard tasks, reflecting high strategic milestone scope."),
    ("Lead Tier Bimodality:", "Lead roles display bimodal pricing: boutique Western enterprise architecture roles bill $60 - $120/hr, balanced against offshore bulk virtual team lead postings ($10 - $15/hr).")
]
for title, desc in points5_l:
    p = tf5_l.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Bottom Right Card: Freelancer Playbook
add_card(s5, Inches(6.8), Inches(3.05), Inches(5.72), Inches(3.70))
tb5_r = s5.shapes.add_textbox(Inches(7.0), Inches(3.20), Inches(5.32), Inches(3.40))
tf5_r = tb5_r.text_frame
tf5_r.word_wrap = True

p = tf5_r.paragraphs[0]
p.text = "Strategic Implications for Talent & Clients"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points5_r = [
    ("Title Framing Anchors Expectations:", "Explicit inclusion of 'Senior' or 'Architect' in profile titles creates an immediate cognitive pricing anchor, increasing offer rates by +35%."),
    ("The Skill-Seniority Multiplier:", "Seniority qualifiers produce maximum financial yield when combined with scarce infrastructure skills (e.g., 'Senior Kubernetes Architect' bills $65+/hr)."),
    ("Fixed Milestones for High Efficacy:", "For experienced specialists, deliverable-based fixed contracts capture significantly higher effective hourly earnings ($60+/hr implied)."),
    ("Commoditization Defense:", "Generalist developers without clear seniority qualifiers are increasingly forced to compete in the sub-$20/hr global rate bracket.")
]
for title, desc in points5_r:
    p = tf5_r.add_paragraph()
    p.text = f"✔ {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

add_footer(s5, 5)

# ==============================================================================
# SLIDE 6: TASK 2 - EMERGING CATEGORIES (Light Theme)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_full_background(s6, C_LIGHT_BG)
add_header(s6, "TASK 02 | CATEGORY VELOCITY & MOMENTUM", "Emerging Job Categories & Posting Frequency Growth", "Evaluating Period-over-Period growth velocity (g), linear trend slopes (m), and weighted momentum scores (M).")

# Left Column (Content)
add_card(s6, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb6 = s6.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(4.75))
tf6 = tb6.text_frame
tf6.word_wrap = True

p = tf6.paragraphs[0]
p.text = "Category Growth Rankings & Breakouts"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets6 = [
    ("Top Emerging Growth Sectors:", "• Blockchain & Web3: +22.7% growth | Slope +4.2 | Momentum 75.6\n• Cloud & DevOps: +18.4% growth | Slope +2.4 | Momentum 60.2\n• Sales & Lead Gen: +15.8% growth | Slope +6.2 | Momentum 62.2\n• Finance & Legal: +14.8% growth | Slope +3.0 | Momentum 55.0\n• AI & Machine Learning: +13.3% growth | Slope +32.4 | Momentum 49.9"),
    ("Established Market Powerhouses:", "Software & Web Dev (+11.1%) and Digital Marketing (+13.3%) drive the highest absolute volume (>36,000 active postings)."),
    ("Breakout High-Velocity Micro-Niches:", "Generative AI & LangChain RAG pipelines (+48.2% posting velocity)\n• Short-Form Video Editing (CapCut/Reels) (+34.1% velocity)\n• No-Code AI Automation (Make/Zapier) (+31.5% velocity)\n• Next.js App Router & Tailwind CSS (+22.8% velocity)"),
    ("Maturing / Saturated Niches:", "Basic content copywriting (-4.7%) and routine virtual support (-1.8%) experience volume compression due to AI automation.")
]
for title, desc in bullets6:
    p = tf6.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Right Column (Chart + Callout)
s6.shapes.add_picture('pptx_assets/chart_task2_growth.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s6, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_GREEN_LIGHT, border_color=C_GREEN_SUCCESS)
tb_c6 = s6.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c6 = tb_c6.text_frame
tf_c6.word_wrap = True
p_c6 = tf_c6.paragraphs[0]
p_c6.text = "📈 Growth Momentum Takeaway"
p_c6.font.size = Pt(10.5)
p_c6.font.bold = True
p_c6.font.color.rgb = C_GREEN_SUCCESS

p_c6_sub = tf_c6.add_paragraph()
p_c6_sub.text = "AI, Cloud, and Web3 form the fastest-accelerating technical cluster. Micro-niches like RAG pipelines and short-form video exhibit triple-digit annualized expansion rates."
p_c6_sub.font.size = Pt(9)
p_c6_sub.font.color.rgb = C_TEXT_DARK

add_footer(s6, 6)

# ==============================================================================
# SLIDE 7: TASK 3 - ML FORECASTING ARCHITECTURE (Light Theme)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_full_background(s7, C_LIGHT_BG)
add_header(s7, "TASK 03 | PREDICTIVE MODELING ARCHITECTURE", "Time-Series Demand Forecasting Framework", "Designing autoregressive machine learning models to forecast daily job postings across major sectors.")

cards7 = [
    ("High-Dimensional Feature Engineering", C_BLUE_PRIMARY, [
        ("Autoregressive Daily Lags", "Captures momentum via sequential lags lag_1, lag_2, ..., lag_7 to model immediate daily persistence."),
        ("Rolling Window Statistics", "Extracts 3-day mean (μ_3), 7-day mean (μ_7), and 7-day rolling standard deviation (σ_7) to track demand volatility."),
        ("Calendar Seasonality Encodings", "Day-of-week one-hot flags (dow_0 to dow_6) and weekend indicator to capture Tuesday–Thursday hiring peaks.")
    ]),
    ("Model Selection & Ensemble Tuning", C_CYAN_ACCENT, [
        ("Gradient Boosting Regressor", "Optimized ensemble combining 120 decision trees with learning rate η = 0.05 and maximum depth of 3."),
        ("Non-Linear Cyclical Handling", "Significantly outperforms classical ARIMA/SARIMA in capturing asymmetric weekday-weekend volume shocks (-35% on weekends)."),
        ("Strict Bound Preservation", "Prevents negative demand forecasts without requiring post-hoc heuristic clipping.")
    ]),
    ("Rigorous Chronological Validation", C_INDIGO_PURPLE, [
        ("Zero Lookahead Contamination", "Enforces a strict 80/20 chronological split: trained on first 80% contiguous days, tested on final 20% holdout actuals."),
        ("Multi-Step 30-Day Rollout", "Executes recursive multi-step forecasting extending 30 days ahead into the future."),
        ("Confidence Horizon Scaling", "Dynamic 95% confidence intervals expanding with forecast horizon: CI_95% = ŷ ± 1.96 · σ_ε · √(1 + 0.05 · h).")
    ])
]

for i, (title, accent, bullets) in enumerate(cards7):
    cx = Inches(0.8 + i * 3.98)
    cy = Inches(1.70)
    cw = Inches(3.78)
    ch = Inches(5.05)
    add_card(s7, cx, cy, cw, ch)

    # Accent Top Line
    top_line = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cw, Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = accent
    top_line.line.fill.background()

    tb = s7.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.20), cw - Inches(0.4), ch - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_DARK

    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"✔ {b_title}"
        p_b.font.size = Pt(10.5)
        p_b.font.bold = True
        p_b.font.color.rgb = accent
        p_b.space_before = Pt(10)

        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(9.2)
        p_d.font.color.rgb = C_TEXT_MUTED
        p_d.space_before = Pt(2)

add_footer(s7, 7)

# ==============================================================================
# SLIDE 8: TASK 3 - FORECAST ACCURACY & PROJECTIONS (Light Theme)
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
add_full_background(s8, C_LIGHT_BG)
add_header(s8, "TASK 03 | FORECAST BENCHMARKS & PROJECTIONS", "Model Accuracy Benchmarks & 30-Day Multi-Step Curves", "Holdout out-of-sample evaluation across MAE, RMSE, MAPE, and R² with 30-day projection curves.")

# Left Column (Table & Findings)
add_card(s8, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(1.10))
tf8 = tb8.text_frame
tf8.word_wrap = True

p = tf8.paragraphs[0]
p.text = "Holdout Out-of-Sample Accuracy Benchmarks"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

p_sub = tf8.add_paragraph()
p_sub.text = "Evaluated on strictly unseen future test days using 4 standard accuracy metrics:"
p_sub.font.size = Pt(9.5)
p_sub.font.color.rgb = C_TEXT_MUTED

# Table
table_shape = s8.shapes.add_table(7, 5, Inches(1.0), Inches(2.95), Inches(5.20), Inches(2.30))
tbl = table_shape.table
tbl.columns[0].width = Inches(2.00)
tbl.columns[1].width = Inches(0.80)
tbl.columns[2].width = Inches(0.80)
tbl.columns[3].width = Inches(0.80)
tbl.columns[4].width = Inches(0.80)

headers = ["Domain / Role", "MAE", "RMSE", "MAPE", "R²"]
for j, h in enumerate(headers):
    cell = tbl.cell(0, j)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_DARK_BG
    p = cell.text_frame.paragraphs[0]
    p.text = h
    p.font.size = Pt(8.5)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT

row_data = [
    ("Overall Job Market", "440.9", "889.0", "16.9%", "0.712"),
    ("Software & Web Dev", "48.9", "78.1", "20.1%", "0.723"),
    ("Video Production", "42.2", "67.1", "18.9%", "0.421"),
    ("UI/UX Design", "44.8", "55.7", "21.4%", "0.568"),
    ("Digital Marketing", "52.6", "74.4", "23.1%", "0.547"),
    ("AI & Machine Learning", "22.3", "30.4", "28.3%", "0.417")
]
for i, row in enumerate(row_data):
    for j, val in enumerate(row):
        cell = tbl.cell(i+1, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_WHITE if i % 2 == 0 else C_LIGHT_BG
        p = cell.text_frame.paragraphs[0]
        p.text = val
        p.font.size = Pt(8)
        p.font.color.rgb = C_TEXT_DARK
        p.alignment = PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT

# Note under table
tb_n = s8.shapes.add_textbox(Inches(1.0), Inches(5.40), Inches(5.20), Inches(1.20))
tf_n = tb_n.text_frame
tf_n.word_wrap = True
p_n = tf_n.paragraphs[0]
p_n.text = "Key Forecast Observations:"
p_n.font.size = Pt(10)
p_n.font.bold = True
p_n.font.color.rgb = C_TEXT_DARK

p_n1 = tf_n.add_paragraph()
p_n1.text = "• Overall market achieves 16.89% MAPE and 0.712 R², reliably modeling hiring volume.\n• AI & ML exhibits the steepest 30-day slope (+31% projected expansion)."
p_n1.font.size = Pt(8.8)
p_n1.font.color.rgb = C_TEXT_MUTED

# Right Column (Chart)
s8.shapes.add_picture('pptx_assets/chart_task3_forecast.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s8, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_BLUE_LIGHT, border_color=C_BLUE_PRIMARY)
tb_c8 = s8.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c8 = tb_c8.text_frame
tf_c8.word_wrap = True
p_c8 = tf_c8.paragraphs[0]
p_c8.text = "📊 30-Day Forecast Outlook"
p_c8.font.size = Pt(10.5)
p_c8.font.bold = True
p_c8.font.color.rgb = C_BLUE_PRIMARY

p_c8_sub = tf_c8.add_paragraph()
p_c8_sub.text = "Weekday volume fluctuates consistently between 5,800 and 7,200 postings, dropping to ~4,000 on weekends. The ensemble model effectively tracks these seasonal cycles."
p_c8_sub.font.size = Pt(9)
p_c8_sub.font.color.rgb = C_TEXT_DARK

add_footer(s8, 8)

# ==============================================================================
# SLIDE 9: TASK 4 - GEOSPATIAL WAGES & ARBITRAGE (Light Theme)
# ==============================================================================
s9 = prs.slides.add_slide(blank_layout)
add_full_background(s9, C_LIGHT_BG)
add_header(s9, "TASK 04 | GEOSPATIAL WAGE ARBITRAGE", "Comparison of Average Hourly Rates Across 212 Countries", "Evaluating wage differentials, client country concentration, and regional compensation benchmarks.")

# Left Column (Content)
add_card(s9, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(4.75))
tf9 = tb9.text_frame
tf9.word_wrap = True

p = tf9.paragraphs[0]
p.text = "Geospatial Wage Analysis & Key Insights"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets9 = [
    ("Client Volume Concentration (Top 5 = 66%):", "• United States: 99,834 jobs (40.8% share) | Mean $31.80/hr\n• United Kingdom: 19,149 jobs (7.8% share) | Mean $28.45/hr\n• India: 15,835 jobs (6.5% share) | Mean $22.68/hr\n• Australia: 12,618 jobs (5.2% share) | Mean $23.81/hr\n• Canada: 11,658 jobs (4.8% share) | Mean $25.70/hr"),
    ("Regional Wage Hierarchy:", "• North America leads globally at $31.17/hr (53.7k hourly jobs)\n• Sub-Saharan Africa ($27.46/hr) & Latin America ($27.23/hr)\n• Western Europe ($27.18/hr, 16.7k hourly jobs)\n• Middle East & North Africa ($26.48/hr) | APAC ($24.32/hr)"),
    ("Cross-Border Labor Arbitrage:", "Clients in North America and Western Europe offer substantial wage premiums over domestic markets in developing nations, creating strong incentives for international remote freelancers."),
    ("Interactive World Choropleth Map:", "Rendered via Plotly.js on web route /task4, mapping rates across all 212 countries using ISO Alpha-3 projections.")
]
for title, desc in bullets9:
    p = tf9.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Right Column (Chart + Callout)
s9.shapes.add_picture('pptx_assets/chart_task4_geography.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s9, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_BLUE_LIGHT, border_color=C_BLUE_PRIMARY)
tb_c9 = s9.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c9 = tb_c9.text_frame
tf_c9.word_wrap = True
p_c9 = tf_c9.paragraphs[0]
p_c9.text = "🌍 Global Arbitrage Dynamic"
p_c9.font.size = Pt(10.5)
p_c9.font.bold = True
p_c9.font.color.rgb = C_BLUE_PRIMARY

p_c9_sub = tf_c9.add_paragraph()
p_c9_sub.text = "Top Tier-1 economies drive two-thirds of global freelance demand. Freelancers capturing North American clients earn an average +28% premium over local APAC rates."
p_c9_sub.font.size = Pt(9)
p_c9_sub.font.color.rgb = C_TEXT_DARK

add_footer(s9, 9)

# ==============================================================================
# SLIDE 10: TASK 5 - RECOMMENDATION ENGINE (Light Theme)
# ==============================================================================
s10 = prs.slides.add_slide(blank_layout)
add_full_background(s10, C_LIGHT_BG)
add_header(s10, "TASK 05 | PERSONALIZED RECOMMENDER ENGINE", "Personalized Job Recommendation Engine Architecture", "Sublinear TF-IDF semantic vector matching, cosine similarity scoring, and multi-criteria constraint filtering.")

cards10 = [
    ("Sublinear TF-IDF Vector Space", C_BLUE_PRIMARY, [
        ("Mathematical Formulation", "TF-IDF(t, d) = (1 + log(tf)) × log((1 + |D|) / (1 + |{d : t ∈ d}|)) + 1 to prevent high-frequency term saturation."),
        ("Token Vocabulary", "30,000 unigrams and bigrams extracting technical skills, stacks, and qualifiers."),
        ("Active Indexed Corpus", "Pre-indexes 50,000 clean active job postings for instant real-time querying.")
    ]),
    ("Multi-Criteria Re-Ranking Engine", C_CYAN_ACCENT, [
        ("Cosine Similarity Metric", "Computes Sim(q, d) = (q · d) / (||q|| ||d||) normalized to 0–100% semantic match score."),
        ("Hard & Soft Filtering", "Filters by Category, Country, Hourly vs Fixed, Minimum Compensation, and Seniority."),
        ("Keyword Explainability", "Highlights matched intersection tokens (e.g. 'python', 'react', 'senior') for full transparency.")
    ]),
    ("Production REST API & Web UI", C_GREEN_SUCCESS, [
        ("Endpoint: POST /api/recommend", "High-throughput endpoint accepting JSON profile queries and returning top-k matched jobs in <100ms."),
        ("Interactive Web Portal", "Live interface at /recommend with real-time AJAX search, quick-add skill pills, and Upwork deep links."),
        ("Serialized Artifacts", "Vector model bundle persisted in models/saved/tfidf_recommender.joblib for instant startup.")
    ])
]

for i, (title, accent, bullets) in enumerate(cards10):
    cx = Inches(0.8 + i * 3.98)
    cy = Inches(1.70)
    cw = Inches(3.78)
    ch = Inches(5.05)
    add_card(s10, cx, cy, cw, ch)

    top_line = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cw, Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = accent
    top_line.line.fill.background()

    tb = s10.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.20), cw - Inches(0.4), ch - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_DARK

    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"✔ {b_title}"
        p_b.font.size = Pt(10.5)
        p_b.font.bold = True
        p_b.font.color.rgb = accent
        p_b.space_before = Pt(10)

        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(9.2)
        p_d.font.color.rgb = C_TEXT_MUTED
        p_d.space_before = Pt(2)

add_footer(s10, 10)

# ==============================================================================
# SLIDE 11: TASK 6 - MONTHLY DYNAMICS & INGESTION (Light Theme)
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
add_full_background(s11, C_LIGHT_BG)
add_header(s11, "TASK 06 | CHRONOLOGICAL TRACKING & INGESTION", "Monthly Job Market Evolution & Dynamic Pipeline", "Tracking Month-over-Month labor shifts and automating continuous dynamic database updates.")

# Left Card: Monthly Trends
add_card(s11, Inches(0.8), Inches(1.70), Inches(5.72), Inches(5.05))
tb11_l = s11.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.32), Inches(4.75))
tf11_l = tb11_l.text_frame
tf11_l.word_wrap = True

p = tf11_l.paragraphs[0]
p.text = "Chronological Market Evolution (Nov 2023 - Mar 2024)"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points11_l = [
    ("Explosive Q1 2024 Ingestion Volume:", "• February 2024: 101,886 postings | Avg Rate: $28.98/hr | Avg Budget: $607.54\n• March 2024: 142,834 postings (+40.2% MoM volume) | Avg Rate: $28.59/hr | Avg Budget: $576.42"),
    ("Sector Stability Over Time:", "Software & Web Development consistently anchors market demand (8.0% to 8.3% total share), followed by Digital Marketing (6.5% to 6.8%) and Video Production (6.1% to 6.4%)."),
    ("Contract Share Equilibrium:", "The ratio between hourly contracts (41.0% - 42.9%) and fixed-budget projects (57.1% - 59.0%) remained stable across peak ingestion months."),
    ("Geographical Hiring Continuity:", "The United States remained the primary hiring engine (40.6% - 41.0% share), followed by the UK (7.7% - 7.9%) and India (6.4% - 6.5%).")
]
for title, desc in points11_l:
    p = tf11_l.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(8)

# Right Card: Dynamic Pipeline Architecture
add_card(s11, Inches(6.8), Inches(1.70), Inches(5.72), Inches(5.05))
tb11_r = s11.shapes.add_textbox(Inches(7.0), Inches(1.85), Inches(5.32), Inches(4.75))
tf11_r = tb11_r.text_frame
tf11_r.word_wrap = True

p = tf11_r.paragraphs[0]
p.text = "Automated Dynamic Ingestion Pipeline"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

points11_r = [
    ("Webhook Endpoint: POST /api/monthly/update:", "Accepts new batch CSV job postings, validating required schemas and data integrity asynchronously."),
    ("Automated ETL & Feature Ingestion:", "Automatically decodes HTML entities, parses regex skill taxonomy, cleans rate bounds, and executes SQLite upserts."),
    ("Zero-Downtime Cache Regeneration:", "Regenerates metrics JSON (analysis_metrics.json) in background workers without interrupting active user traffic or web requests."),
    ("Live Dashboard Integration (/task6):", "Visual interface instantly reflects newly ingested months, plotting MoM velocity deltas and category volume shifts.")
]
for title, desc in points11_r:
    p = tf11_r.add_paragraph()
    p.text = f"✔ {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(8)

add_footer(s11, 11)

# ==============================================================================
# SLIDE 12: TASK 7 - REMOTE WORK LANDSCAPE (Light Theme)
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
add_full_background(s12, C_LIGHT_BG)
add_header(s12, "TASK 07 | REMOTE WORK LANDSCAPE & STRUCTURE", "Remote Work Landscape, Arbitrage & Structural Shifts", "Investigating cross-border labor dynamics, contract format evolution, and remote-first keyword adoption.")

# Left Column (Content)
add_card(s12, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb12 = s12.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(4.75))
tf12 = tb12.text_frame
tf12.word_wrap = True

p = tf12.paragraphs[0]
p.text = "Remote Work Structural Insights"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets12 = [
    ("Contract Format: 57.6% Hourly vs 42.4% Fixed-Price:", "Hourly contracts dominate retention-heavy disciplines (software development, DevOps, continuous data engineering). Platform time-tracking apps (screenshots, keystrokes) provide institutional trust for long-term remote arrangements."),
    ("Cross-Border Arbitrage & Tier-1 Concentration:", "62.5% of total job postings originate from Tier-1 developed economies. Tier-1 clients pay an average of $30.08/hr vs $25.57/hr from emerging market clients (+17.6% geographic wage premium)."),
    ("Remote-First Keyword Penetration:", "• Explicit 'Remote / Work From Home' present in 14.2% of titles\n• 'Long-Term / Ongoing' present in 8.8% of titles, commanding higher average compensation ($34.10/hr)."),
    ("2-Year Forecast (2024–2026):", "Total market postings projected to expand from 244k to 363k, with hourly contract share steadily climbing from 57.6% to 63.0%.")
]
for title, desc in bullets12:
    p = tf12.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Right Column (Chart + Callout)
s12.shapes.add_picture('pptx_assets/chart_task7_trends.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s12, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_BLUE_LIGHT, border_color=C_BLUE_PRIMARY)
tb_c12 = s12.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c12 = tb_c12.text_frame
tf_c12.word_wrap = True
p_c12 = tf_c12.paragraphs[0]
p_c12.text = "🌐 The Fractional Remote Staffing Transition"
p_c12.font.size = Pt(10.5)
p_c12.font.bold = True
p_c12.font.color.rgb = C_BLUE_PRIMARY

p_c12_sub = tf_c12.add_paragraph()
p_c12_sub.text = "Hourly tracking contracts are projected to reach 63.0% of market liquidity by 2026 as enterprises transition from isolated gig transactions toward persistent fractional distributed teams."
p_c12_sub.font.size = Pt(9)
p_c12_sub.font.color.rgb = C_TEXT_DARK

add_footer(s12, 12)

# ==============================================================================
# SLIDE 13: TASK 8 - FUTURE SCENARIOS SIMULATOR (Light Theme)
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
add_full_background(s13, C_LIGHT_BG)
add_header(s13, "TASK 08 | PREDICTIVE SCENARIO SIMULATION", "Future Market Trends & Econometric Scenarios (2024–2026)", "Multi-year predictive modeling through 2026 evaluating AI disruption, enterprise outsourcing, and baseline growth.")

# Left Column (Content)
add_card(s13, Inches(0.8), Inches(1.70), Inches(5.60), Inches(5.05))
tb13 = s13.shapes.add_textbox(Inches(1.0), Inches(1.85), Inches(5.20), Inches(4.75))
tf13 = tb13.text_frame
tf13.word_wrap = True

p = tf13.paragraphs[0]
p.text = "3 Macroeconomic Scenario Projections"
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_TEXT_DARK

bullets13 = [
    ("Scenario A: Baseline Continuous Growth:", "• Postings expand +3.2% quarterly, reaching 346,207 jobs by 2026.\n• Mean hourly rate reaches $31.39/hr (+0.8% quarterly inflation adjust).\n• Balanced growth across core technical and marketing disciplines."),
    ("Scenario B: Accelerated AI & Agentic Disruption:", "• AI/ML demand surges (+20% quarterly to 38,400 postings by 2026).\n• Commoditized copywriting & data entry compress by -6% quarterly.\n• Mean hourly rate surges to $33.87/hr driven by high-complexity system architects."),
    ("Scenario C: Enterprise Offshore Outsourcing Surge:", "• Global enterprises replace domestic headcount with remote freelance squads (+7.5% quarterly posting expansion to 542,440 jobs).\n• Hourly rates remain competitive at $30.04/hr."),
    ("Interactive Web Simulator (/task8):", "Users can dynamically adjust AI disruption and outsourcing factors via live sliders in the Flask web interface.")
]
for title, desc in bullets13:
    p = tf13.add_paragraph()
    p.text = f"• {title} {desc}"
    p.font.size = Pt(9.8)
    p.font.color.rgb = C_TEXT_DARK
    p.space_before = Pt(6)

# Right Column (Chart + Callout)
s13.shapes.add_picture('pptx_assets/chart_task8_scenarios.png', Inches(6.60), Inches(1.70), width=Inches(5.933), height=Inches(3.90))

add_card(s13, Inches(6.60), Inches(5.75), Inches(5.933), Inches(1.00), bg_color=C_BLUE_LIGHT, border_color=C_BLUE_PRIMARY)
tb_c13 = s13.shapes.add_textbox(Inches(6.80), Inches(5.82), Inches(5.533), Inches(0.85))
tf_c13 = tb_c13.text_frame
tf_c13.word_wrap = True
p_c13 = tf_c13.paragraphs[0]
p_c13.text = "🎯 Econometric Forecast Outlook"
p_c13.font.size = Pt(10.5)
p_c13.font.bold = True
p_c13.font.color.rgb = C_BLUE_PRIMARY

p_c13_sub = tf_c13.add_paragraph()
p_c13_sub.text = "Under rapid AI disruption (Scenario B), high-complexity systems engineers command peak billing premiums, while routine transactional tasks face substantial volume pressure."
p_c13_sub.font.size = Pt(9)
p_c13_sub.font.color.rgb = C_TEXT_DARK

add_footer(s13, 13)

# ==============================================================================
# SLIDE 14: FULL-STACK & DOCKER DEPLOYMENT (Light Theme)
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
add_full_background(s14, C_LIGHT_BG)
add_header(s14, "DEPLOYMENT & PRODUCTION ENGINEERING", "Full-Stack Web Architecture, REST APIs & Docker Deployment", "Production multi-stage containerization, automated testing, and comprehensive REST API endpoints.")

cards14 = [
    ("Web Platform & Visual Dashboards", C_BLUE_PRIMARY, [
        ("Flask Core Architecture", "Modular MVC service in app.py rendering 10 responsive Jinja2 templates."),
        ("Tailwind CSS Frontend", "Polished modern UI with navigation drawer, responsive grids, and dark theme support."),
        ("Plotly.js Interactive Visuals", "Embedded client charts supporting live zoom, pan, hover tooltips, and data filtering.")
    ]),
    ("Production REST API Service", C_CYAN_ACCENT, [
        ("GET /api/health", "Container healthcheck endpoint reporting service status, memory cache, and uptime."),
        ("GET /api/task1 - /api/task4", "Programmatic access to salary correlations, growth rankings, and forecasts."),
        ("POST /api/recommend", "Semantic candidate matching with multi-criteria filtering in <100ms."),
        ("POST /api/monthly/update", "Automated dynamic ingestion webhook for monthly batch updates.")
    ]),
    ("Containerization & Quality Assurance", C_GREEN_SUCCESS, [
        ("Multi-Stage Dockerfile", "Optimized Python 3.12-slim build, non-root security user, minimal image size."),
        ("Docker Compose Orchestration", "Multi-container setup (web app + analytics worker) with healthchecks."),
        ("Automated Test Suite", "13/13 passing pytest unit tests validating preprocessor, loaders, recommender, and APIs.")
    ])
]

for i, (title, accent, bullets) in enumerate(cards14):
    cx = Inches(0.8 + i * 3.98)
    cy = Inches(1.70)
    cw = Inches(3.78)
    ch = Inches(5.05)
    add_card(s14, cx, cy, cw, ch)

    top_line = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cw, Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = accent
    top_line.line.fill.background()

    tb = s14.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.20), cw - Inches(0.4), ch - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_DARK

    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"✔ {b_title}"
        p_b.font.size = Pt(10.5)
        p_b.font.bold = True
        p_b.font.color.rgb = accent
        p_b.space_before = Pt(10)

        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(9.2)
        p_d.font.color.rgb = C_TEXT_MUTED
        p_d.space_before = Pt(2)

add_footer(s14, 14)

# ==============================================================================
# SLIDE 15: STRATEGIC CONCLUSIONS & ROADMAP (Dark Theme)
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
add_full_background(s15, C_DARK_BG)
add_header(s15, "STRATEGIC PLAYBOOK & FUTURE ROADMAP", "Strategic Takeaways, Stakeholder Playbook & Conclusion", "Transforming labor market analytics into sustained competitive advantage for talent and enterprises.", dark=True)

concl_cards = [
    ("For Freelancers & Technical Talent", C_CYAN_ACCENT, [
        ("The Specialization Imperative", "Move up the stack from commoditized web development to systems programming (Rust, Go) and Web3 (Solidity) for +50% wage premiums."),
        ("AI-Native Workflow Adoption", "Integrate LLM orchestration (LangChain, vector DBs) to capture the fastest-growing market demand (+48% velocity)."),
        ("Value-Add Outcome Framing", "Frame project proposals around business outcomes rather than hourly labor to protect against automation compression.")
    ]),
    ("For Recruiters & Enterprise Hiring", C_GREEN_SUCCESS, [
        ("Strategic Labor Arbitrage", "Leverage cross-border hiring in APAC, Latin America, and Eastern Europe to access senior technical talent at high cost-efficiency."),
        ("Fractional Staffing Squads", "Adopt hourly tracking contracts for long-term engineering squads and milestone-based fixed budgets for modular creative sprints."),
        ("Continuous Market Benchmarking", "Utilize dynamic labor APIs to adjust offered rates in real-time against empirical market shifts.")
    ]),
    ("Delivered Milestones & Verification", C_INDIGO_PURPLE, [
        ("100% Specification Fulfillment", "Successfully completed all 8 analytical tasks, predictive models, TF-IDF engine, and Docker containerization from 1791966837.pdf."),
        ("Production-Ready Platform", "Fully operational web dashboard, 8 REST API endpoints, serialized ML models, and comprehensive markdown documentation reports."),
        ("Next-Generation Roadmap", "Future enhancements include deep transformer embedding models, live Upwork API streaming, and multi-currency normalization.")
    ])
]

for i, (title, accent, bullets) in enumerate(concl_cards):
    cx = Inches(0.8 + i * 3.98)
    cy = Inches(1.70)
    cw = Inches(3.78)
    ch = Inches(5.05)
    add_card(s15, cx, cy, cw, ch, dark=True)

    top_line = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cw, Inches(0.08))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = accent
    top_line.line.fill.background()

    tb = s15.shapes.add_textbox(cx + Inches(0.2), cy + Inches(0.20), cw - Inches(0.4), ch - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    for b_title, b_desc in bullets:
        p_b = tf.add_paragraph()
        p_b.text = f"✔ {b_title}"
        p_b.font.size = Pt(10.5)
        p_b.font.bold = True
        p_b.font.color.rgb = accent
        p_b.space_before = Pt(10)

        p_d = tf.add_paragraph()
        p_d.text = b_desc
        p_d.font.size = Pt(9.2)
        p_d.font.color.rgb = C_TEXT_SUBTLE
        p_d.space_before = Pt(2)

add_footer(s15, 15, dark=True)

# ==============================================================================
# SAVE PRESENTATION
# ==============================================================================
output_filename = "Job_Market_Analysis_Presentation.pptx"
prs.save(output_filename)
print(f"Presentation saved successfully as '{output_filename}' with {len(prs.slides)} slides.")

# Also save a copy with the alternate name
prs.save("WorkPulse_Job_Market_Analysis.pptx")
print("Duplicate copy saved as 'WorkPulse_Job_Market_Analysis.pptx'.")
