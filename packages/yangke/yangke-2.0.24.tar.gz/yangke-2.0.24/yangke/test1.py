# import torch
# print(torch.cuda.is_available())

from iapws import IAPWS97

# 定义一个函数，用于计算水的物性值
def water_properties(S=7.467626249, P=0.1):
    # T 为温度，单位为摄氏度
    # P 为压力，单位为MPa
    # 返回一个字典，包含水的物性值
    return IAPWS97(T=T+273.15, P=P)

# 调用函数，计算水的物性值
props = IAPWS97(s=6.763, P=2.806)
print(props.h)
