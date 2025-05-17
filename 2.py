import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox
from matplotlib.ticker import MultipleLocator # 导入MultipleLocator

MINIMUM_BID = 100
MAX_TOTAL_POOL = 22000
STAR_MULTIPLIER = 5

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
    if your_bid_b < MINIMUM_BID:
        return 0.0
    p_total = your_bid_b + p_others_current
    if p_total <= 0 or p_total > MAX_TOTAL_POOL:
        return 0.0 
    star_prize = get_final_star_prize(p_total)
    if star_prize == 0 or p_total == 0: 
        return 0.0
    efficiency = star_prize / p_total 
    return efficiency

# --- 绘图设置 ---
fig, ax = plt.subplots(figsize=(14, 9))
plt.subplots_adjust(left=0.1, bottom=0.30) 

b_plot_max = 10000 
b_2d_plot_range = np.linspace(MINIMUM_BID, b_plot_max, 300) 
initial_p_others = 1300.0

initial_efficiencies = [calculate_efficiency(b, initial_p_others) for b in b_2d_plot_range]
line, = ax.plot(b_2d_plot_range, initial_efficiencies, lw=2, color='deepskyblue')
optimal_point_marker, = ax.plot([], [], 'ro', markersize=8, label='Optimal B (Max Efficiency)')

ax.set_xlabel(f'Your Bid (B) points (Minimum {MINIMUM_BID})')
ax.set_ylabel('Cost-Effectiveness (Efficiency = Star_Prize / P_total)')
ax.grid(True, linestyle=':', alpha=0.5)
ax.set_ylim(bottom=-0.0001) 
ax.set_xlim(left=0, right=b_plot_max + 100) # X轴从0开始，以便看到500的刻度

# --- 修改X轴刻度部分 ---
if b_plot_max <= 2000:
    x_tick_step = 100
elif b_plot_max <= 10000: # 当b_plot_max在2001到10000之间时
    x_tick_step = 500     # 设置刻度间隔为500
else: # 如果b_plot_max大于10000
    x_tick_step = 1000
ax.xaxis.set_major_locator(MultipleLocator(x_tick_step))
plt.xticks(rotation=30, ha="right") # 旋转标签以防重叠
# --- X轴刻度修改结束 ---

info_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

def update_plot_and_linked_widgets(p_others_current_val_str):
    try:
        p_others_current = float(p_others_current_val_str)
    except ValueError:
        p_others_current = slider_p_others.val # 转换失败则使用滑块当前值

    p_others_current = np.clip(p_others_current, slider_p_others.valmin, slider_p_others.valmax)
    
    # 更新文本框和滑块（如果值有变化）
    # 使用 {:.0f} 避免科学计数法和小数点
    if text_box_p_others.text != f"{p_others_current:.0f}":
        text_box_p_others.set_val(f"{p_others_current:.0f}")
    if abs(slider_p_others.val - p_others_current) > 1e-6: # 避免浮点数比较问题
        slider_p_others.set_val(p_others_current)

    efficiency_values = [calculate_efficiency(b_val, p_others_current) for b_val in b_2d_plot_range]
    line.set_ydata(efficiency_values)
    
    max_eff_2d = 0
    optimal_b_val = -1
    if len(efficiency_values) > 0:
        valid_efficiencies = np.array(efficiency_values)
        if np.any(valid_efficiencies > 0):
            max_eff_2d = np.max(valid_efficiencies)
            optimal_b_indices = np.where(np.isclose(valid_efficiencies, max_eff_2d))[0]
            if len(optimal_b_indices) > 0:
                optimal_b_val = b_2d_plot_range[optimal_b_indices[0]]
    
    if optimal_b_val != -1 and max_eff_2d > 0:
        optimal_point_marker.set_data([optimal_b_val], [max_eff_2d])
        optimal_point_marker.set_label(f'Optimal B: {optimal_b_val:.0f}\nMax Eff: {max_eff_2d:.5f}')
        info_str = f'P_others: {p_others_current:.0f}\nOptimal B: {optimal_b_val:.0f}\nMax Efficiency: {max_eff_2d:.5f}'
    else:
        optimal_point_marker.set_data([], [])
        optimal_point_marker.set_label('Optimal B (Max Efficiency)')
        info_str = f'P_others: {p_others_current:.0f}\nNo positive efficiency found.'

    info_text.set_text(info_str)
    ax.set_title(f'Efficiency vs. Your Bid (P_others = {p_others_current:.0f}, No Rakeback)')
    
    current_max_y = 0.001 # 默认最小Y轴上限
    if max_eff_2d > 0 :
        current_max_y = max_eff_2d * 1.15
    ax.set_ylim(bottom=-0.0001, top=max(0.001, current_max_y) )


    ax.legend(loc='upper right')
    fig.canvas.draw_idle()

slider_ax = plt.axes([0.15, 0.12, 0.7, 0.03], facecolor='lightgoldenrodyellow')
slider_p_others = Slider(
    ax=slider_ax,
    label='P_others (Slide or Type Below)',
    valmin=0,
    valmax=MAX_TOTAL_POOL - MINIMUM_BID, 
    valinit=initial_p_others,
    valstep=100 
)
slider_p_others.on_changed(update_plot_and_linked_widgets)

textbox_ax = plt.axes([0.35, 0.05, 0.3, 0.04]) 
text_box_p_others = TextBox(textbox_ax, 'Set P_others & Enter:', initial=f"{initial_p_others:.0f}")

def submit_p_others_from_textbox(text):
    try:
        p_val = float(text)
        slider_p_others.set_val(p_val) 
    except ValueError:
        print(f"Invalid input for P_others: '{text}'. Please enter a number.")
        text_box_p_others.set_val(f"{slider_p_others.val:.0f}")

text_box_p_others.on_submit(submit_p_others_from_textbox)

try:
    update_plot_and_linked_widgets(initial_p_others) 
    plt.show()
except Exception as e:
    print("--- SCRIPT ERROR ---")
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()

input("按回车键退出程序...")