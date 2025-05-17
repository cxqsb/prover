import numpy as np
import matplotlib.pyplot as plt

def get_base_stars(p_total):
    """
    根据总点数池 (P_total) 计算星星基数。
    """
    if p_total <= 0:
        return 1
    elif p_total <= 5000:
        return 1
    elif p_total <= 7500:
        return 2
    elif p_total <= 16000:
        return 3
    elif p_total <= 17000:
        return 4
    elif p_total <= 18000:
        return 5
    elif p_total <= 19000:
        return 6
    elif p_total <= 22000:
        return 7
    else: # 超过22000，星星基数按规则为0或保持7，这里按7处理，但实际应用中可能需要根据游戏规则精确定义
          # 如果你希望P_total > 22000 时星星基数为0，可以将下一行改为 return 0
        return 7 

# 生成绘图数据
# p_total_values 定义了每个阶梯开始的X坐标
# 包含0, 每个区间的精确结束点, 以及紧随其后的点(如5000, 5000.01)以形成阶梯的垂直部分
p_total_values_for_plot = np.array([
    0, 5000, 5000.01, 7500, 7500.01, 16000, 16000.01, 
    17000, 17000.01, 18000, 18000.01, 19000, 19000.01, 
    22000, 22000.01, 23000 # 稍微超出一点以便观察最后一个区间的行为
])
# p_total_values_for_plot.sort() # 确保顺序，虽然这里已经是排序的

# 直接根据p_total_values_for_plot计算对应的星星基数
base_stars_for_plot = np.array([get_base_stars(p) for p in p_total_values_for_plot])

# --- 开始绘图 ---
try:
    plt.figure(figsize=(12, 7))

    # 直接使用原始计算的x,y值配合drawstyle='steps-post'
    plt.plot(p_total_values_for_plot, base_stars_for_plot, drawstyle='steps-post', label='Base Stars', color='dodgerblue', linewidth=2)

    # 设置图像标题和坐标轴标签 (英文)
    plt.title('Base Stars vs. Total Pool Size (P_total) - New Rules', fontsize=15)
    plt.xlabel('Total Pool Size (P_total)', fontsize=12)
    plt.ylabel('Base Stars', fontsize=12)

    # 设置坐标轴刻度和范围
    plt.xticks(np.arange(0, 24001, 2500)) 
    plt.yticks(np.arange(0, 9, 1))     
    plt.xlim(-500, 23000) # X轴从略小于0开始，以便看清Y轴
    plt.ylim(-0.5, 8)    # Y轴从略小于0开始

    # 添加表示区间端点的垂直虚线
    tier_boundaries = [0, 5000, 7500, 16000, 17000, 18000, 19000, 22000]
    for boundary in tier_boundaries:
        if boundary > 0: #不在Y轴上画线
             plt.axvline(boundary, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)

    # 显示网格
    plt.grid(True, linestyle=':', alpha=0.5)

    # 显示图例 (英文)
    plt.legend(fontsize=10)

    # 调整布局防止标签重叠
    plt.tight_layout() 

    # 显示图像
    plt.show()

except Exception as e:
    print("脚本在绘图时发生错误:")
    print(e)
    import traceback
    traceback.print_exc() # 打印详细的错误追踪信息

input("按回车键退出程序...")