import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# --- 游戏规则和计算函数 ---
MINIMUM_BID = 500 
MAX_TOTAL_POOL = 22000
STAR_MULTIPLIER = 5
B_PLOT_UPPER_LIMIT = 10000 # 固定X轴“你的出价B”的绘图上限

def get_final_star_prize(p_total):
    base_stars = 0
    if p_total <= 0: base_stars = 0
    elif p_total <= 5000: base_stars = 1
    elif p_total <= 7500: base_stars = 2
    elif p_total <= 16000: base_stars = 3
    elif p_total <= 17000: base_stars = 4
    elif p_total <= 18000: base_stars = 5
    elif p_total <= 19000: base_stars = 6
    elif p_total <= MAX_TOTAL_POOL: base_stars = 7
    else: base_stars = 0 
    return base_stars * STAR_MULTIPLIER

def calculate_efficiency(your_bid_b, p_others_current):
    if your_bid_b < MINIMUM_BID: return 0.0
    p_total = your_bid_b + p_others_current
    if p_total <= 0 or p_total > MAX_TOTAL_POOL: return 0.0 
    star_prize = get_final_star_prize(p_total)
    if star_prize == 0 or p_total == 0: return 0.0
    efficiency = star_prize / p_total 
    return efficiency
# --- Streamlit 应用代码 ---

st.set_page_config(layout="centered") 
st.title("Proof Contest - 出价划算度分析器 (X轴固定上限)")
st.markdown("调整侧边栏“他人点数池”查看在不同情况下的划算度曲线。")

# --- 使用 Session State 初始化和保存P_others的值 ---
if 'p_others_val' not in st.session_state:
    st.session_state.p_others_val = 1300  # P_others 初始值

# --- 将P_others控件放到侧边栏 ---
st.sidebar.subheader("调整参数:")
current_p_others_input = st.sidebar.slider(
    label="他人已在池中的点数 (P_others):",
    min_value=0,
    max_value=MAX_TOTAL_POOL - MINIMUM_BID, # P_others的上限
    value=st.session_state.p_others_val,
    step=100,
    key="p_others_slider_key_v4" 
)
if current_p_others_input != st.session_state.p_others_val:
    st.session_state.p_others_val = current_p_others_input
    st.rerun() # 值改变时，重新运行整个脚本

# --- 图表生成和显示 ---
current_p_others_for_plot = st.session_state.p_others_val

# X轴（你的出价B）的实际绘图上限
# 它不应超过B_PLOT_UPPER_LIMIT，也不能使得 P_total 超过 MAX_TOTAL_POOL
actual_b_plot_limit_on_graph = min(B_PLOT_UPPER_LIMIT, MAX_TOTAL_POOL - current_p_others_for_plot)
if actual_b_plot_limit_on_graph < MINIMUM_BID:
    actual_b_plot_limit_on_graph = MINIMUM_BID # 至少绘制到最低出价（如果可行）

b_2d_plot_range_streamlit = np.linspace(MINIMUM_BID, actual_b_plot_limit_on_graph, 300) 

# 为了更精确地捕捉断点，可以插入一些关键的B值
critical_b_values_streamlit = []
tier_total_pools_streamlit = [5000, 7500, 16000, 17000, 18000, 19000, MAX_TOTAL_POOL]
for p_thresh in tier_total_pools_streamlit:
    b_at_thresh = p_thresh - current_p_others_for_plot
    if MINIMUM_BID <= b_at_thresh <= actual_b_plot_limit_on_graph :
        critical_b_values_streamlit.append(b_at_thresh)
        critical_b_values_streamlit.append(b_at_thresh + 1) # 确保捕捉跳变后
if len(critical_b_values_streamlit) > 0:
    b_2d_plot_range_streamlit = np.unique(np.sort(np.concatenate((b_2d_plot_range_streamlit, critical_b_values_streamlit))))
    b_2d_plot_range_streamlit = b_2d_plot_range_streamlit[b_2d_plot_range_streamlit <= actual_b_plot_limit_on_graph]
    b_2d_plot_range_streamlit = b_2d_plot_range_streamlit[b_2d_plot_range_streamlit >= MINIMUM_BID]


efficiency_values_streamlit = []
if len(b_2d_plot_range_streamlit) > 0 and b_2d_plot_range_streamlit[0] >= MINIMUM_BID : # 仅当有有效B值时计算
    efficiency_values_streamlit = [calculate_efficiency(b_val, current_p_others_for_plot) for b_val in b_2d_plot_range_streamlit]

fig_streamlit, ax_streamlit = plt.subplots(figsize=(10, 5)) 

if len(b_2d_plot_range_streamlit) > 0 and len(efficiency_values_streamlit) == len(b_2d_plot_range_streamlit):
    ax_streamlit.plot(b_2d_plot_range_streamlit, efficiency_values_streamlit, marker='.', linestyle='-', markersize=3, color='deepskyblue')

    max_eff_2d_streamlit = 0
    optimal_b_val_streamlit = -1
    if len(efficiency_values_streamlit) > 0:
        valid_efficiencies_streamlit = np.array(efficiency_values_streamlit)
        if np.any(valid_efficiencies_streamlit > 0):
            max_eff_2d_streamlit = np.max(valid_efficiencies_streamlit)
            optimal_b_indices_streamlit = np.where(np.isclose(valid_efficiencies_streamlit, max_eff_2d_streamlit))[0]
            if len(optimal_b_indices_streamlit) > 0:
                optimal_b_val_streamlit = b_2d_plot_range_streamlit[optimal_b_indices_streamlit[0]]
                ax_streamlit.scatter([optimal_b_val_streamlit], [max_eff_2d_streamlit], color='red', s=80, zorder=5, 
                                     label=f'Optimal B: {optimal_b_val_streamlit:.0f}\nMax Eff: {max_eff_2d_streamlit:.5f}')
    ax_streamlit.legend(loc='upper right', fontsize='small')
    current_plot_ylim_top = 0.001 # 默认Y轴上限
    if max_eff_2d_streamlit > 0:
        current_plot_ylim_top = max_eff_2d_streamlit * 1.2 
    ax_streamlit.set_ylim(bottom=0, top=max(0.001, current_plot_ylim_top)) 
else:
    ax_streamlit.text(0.5, 0.5, "No valid Bids to plot for current P_others\n (e.g., P_others too high)", 
                      horizontalalignment='center', verticalalignment='center', transform=ax_streamlit.transAxes)


ax_streamlit.set_xlabel(f'Your Bid (B) points (Min {MINIMUM_BID}, Max Displayed {B_PLOT_UPPER_LIMIT})', fontsize=10) 
ax_streamlit.set_ylabel('Cost-Effectiveness (Efficiency)', fontsize=10) 
ax_streamlit.set_title(f'Efficiency vs. Your Bid (P_others = {current_p_others_for_plot:.0f})', fontsize=12) 

# --- X轴刻度固定为500 ---
# 使用 B_PLOT_UPPER_LIMIT 来决定刻度逻辑，而不是动态的 actual_b_plot_limit_on_graph
# 这样即使用户的B轴实际绘制范围较小，刻度标准也是一致的
if B_PLOT_UPPER_LIMIT <= 2000:
    x_tick_step = 100
elif B_PLOT_UPPER_LIMIT <= 10000: 
    x_tick_step = 500 # X轴上限为10000时，刻度间隔500
else:
    x_tick_step = 1000
ax_streamlit.xaxis.set_major_locator(MultipleLocator(x_tick_step))
ax_streamlit.set_xlim(left=0, right=B_PLOT_UPPER_LIMIT + x_tick_step * 0.1) # X轴显示上限固定
plt.setp(ax_streamlit.get_xticklabels(), rotation=30, ha="right", fontsize=8) 
plt.setp(ax_streamlit.get_yticklabels(), fontsize=8) 
ax_streamlit.grid(True, linestyle=':', alpha=0.5)

st.pyplot(fig_streamlit, clear_figure=True) 

# --- 在主页面显示最优策略文本 ---
st.markdown("---")
st.subheader(f"当前分析条件下的最优策略 (基于P_others = {current_p_others_for_plot:.0f}的静态分析):")
if optimal_b_val_streamlit != -1 and max_eff_2d_streamlit > 0:
    target_p_total_for_optimal_b = optimal_b_val_streamlit + current_p_others_for_plot
    stars_at_optimal = get_final_star_prize(target_p_total_for_optimal_b)
    st.success(f"为达到当前计算出的最高划算度 (约 {max_eff_2d_streamlit:.5f} 星星/点):")
    st.success(f" • 一个关键的出价目标 (B) 是: **{optimal_b_val_streamlit:.0f}** 点")
    st.success(f" • 这个出价会使总点数池 (P_total) 达到: **{target_p_total_for_optimal_b:.0f}** 点 (预计获得 {stars_at_optimal} 星)")
    st.markdown("...") #之前的风险提示
else:
    st.warning(f"在当前 P_others={current_p_others_for_plot:.0f} 下，未能找到划算度为正的出价策略 (在B的分析上限 {actual_b_plot_limit_on_graph:.0f} 之内)。")
    st.warning(f"这可能是因为在当前P_others下，即使是最低出价 {MINIMUM_BID} 点也会导致总池超过 {MAX_TOTAL_POOL} 点。")
    st.warning(f"如果你的可用点数大于等于 {MINIMUM_BID} 点，且 {MINIMUM_BID + current_p_others_for_plot <= MAX_TOTAL_POOL}，可以考虑出价 {MINIMUM_BID} 点作为尝试，但请自行评估其划算度。")

st.caption("这是一个交互式分析工具。调整左侧边栏的参数，图表和最优策略会自动更新。")