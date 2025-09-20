alternative_symbol = {
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
    "汽": "气",
    "0": "零",
    "零": "〇",
    "进": "入",
    "一轴加": "一号轴加",
    "A": "a",
    "B": "b",
    # "高加": "加热器",  # 加热器和高加不能互换，因为很多地方都有加热器这个词，很容易导致排除加热器时出错
    # "低加": "加热器",
    "凝泵": "凝结水泵",
    "水位": "液位",
    "ASME": "asme",
    "BEST": "best",
}

# 数据采集系统中为绝对压力的测点
pressure_absolute = [
    "低排",
    "低压缸排汽",
    "小机排汽",
    "七段抽汽",
    "八段抽汽",
    "高压汽源至汽封蒸汽冷却器进汽压力",
    "大气压",
    "环境压力",
    "七号低加",
    "7号低加",
    "8A低加",
    "8B低加",
    "9A低加",
    "9B低加",  # "高压缸前后轴封", "中压缸前轴封", "中压缸后轴封","轴封加热器进汽压力", "高压缸前后轴封漏汽母管",
]

# 数据采集系统中为相对压力的测点
pressure_relative = [
    "主汽门",
    "调节级",
    "高压缸排汽",
    "再热蒸汽",
    "再热汽门",
    "中压缸进汽",
    "中压缸排汽",
    "低压缸进汽",
    "一段抽汽",
    "二段抽汽",
    "三段抽汽",
    "四段抽汽",
    "五段抽汽",
    "六段抽汽",
    "高加进汽",
    "高加",
    "5号低加",
    "6号低加",
    "小机进汽",
    "除氧器进汽",
    "最终给水",
    "给水泵出水",
    "凝泵",
    "再热减温水",
    "高压门杆漏汽",
    "蒸汽冷却器",
    "低温省煤器进水压力",
    "低温省煤器",
    "蒸冷器",
    "低省",
    "凝结水",
    "前置泵",
    "汽泵",
    "循环水",
]

name_alias = {
    # excel中的测点名和StandardPoint中的测点名的对应关系
    "漏汽量": {
        "高压门杆漏汽量": "leakage.高压门杆漏汽量",
        "高压门杆漏汽焓": "leakage.高压门杆漏汽焓",
        "高压门杆一漏流量": "leakage.高压门杆一漏流量",
        "高压门杆二漏流量": "leakage.高压门杆二漏流量",
        "高压门杆三漏流量": "leakage.高压门杆三漏流量",
        "高压门杆四漏流量": "leakage.高压门杆四漏流量",
        "高压前轴封漏汽量": "leakage.高压前轴封漏汽量",
        "高压前轴封漏汽焓": "leakage.高压前轴封漏汽焓",
        "高压前轴封一漏流量": "leakage.高压前轴封一漏流量",
        "高压前轴封二漏流量": "leakage.高压前轴封二漏流量",
        "高压前轴封三漏流量": "leakage.高压前轴封三漏流量",
        "高压前轴封四漏流量": "leakage.高压前轴封四漏流量",
        "高压后轴封漏汽量": "leakage.高压后轴封漏汽量",
        "高压后轴封漏汽焓": "leakage.高压后轴封漏汽焓",
        "高压后轴封一漏流量": "leakage.高压后轴封一漏流量",
        "高压后轴封二漏流量": "leakage.高压后轴封二漏流量",
        "高压后轴封三漏流量": "leakage.高压后轴封三漏流量",
        "高压后轴封四漏流量": "leakage.高压后轴封四漏流量",
        "中压前轴封漏汽量": "leakage.中压前轴封漏汽量",
        "中压前轴封漏汽焓": "leakage.中压前轴封漏汽焓",
        "中压前轴封一漏流量": "leakage.中压前轴封一漏流量",
        "中压前轴封二漏流量": "leakage.中压前轴封二漏流量",
        "中压前轴封三漏流量": "leakage.中压前轴封三漏流量",
        "中压前轴封四漏流量": "leakage.中压前轴封四漏流量",
        "中压后轴封漏汽量": "leakage.中压后轴封漏汽量",
        "中压后轴封漏汽焓": "leakage.中压后轴封漏汽焓",
        "中压后轴封一漏流量": "leakage.中压后轴封一漏流量",
        "中压后轴封二漏流量": "leakage.中压后轴封二漏流量",
        "中压后轴封三漏流量": "leakage.中压后轴封三漏流量",
        "中压后轴封四漏流量": "leakage.中压后轴封四漏流量",
        "低压前轴封漏汽量": "leakage.低压前轴封漏汽量",
        "低压前轴封漏汽焓": "leakage.低压前轴封漏汽焓",
        "低压前轴封一漏流量": "leakage.低压前轴封一漏流量",
        "低压前轴封二漏流量": "leakage.低压前轴封二漏流量",
        "低压前轴封三漏流量": "leakage.低压前轴封三漏流量",
        "低压前轴封四漏流量": "leakage.低压前轴封四漏流量",
        "低压后轴封漏汽量": "leakage.低压后轴封漏汽量",
        "低压后轴封漏汽焓": "leakage.低压后轴封漏汽焓",
        "低压后轴封一漏流量": "leakage.低压后轴封一漏流量",
        "低压后轴封二漏流量": "leakage.低压后轴封二漏流量",
        "低压后轴封三漏流量": "leakage.低压后轴封三漏流量",
        "低压后轴封四漏流量": "leakage.低压后轴封四漏流量",
    }
}

StandardPoint = {
    # 该变量主要记录了汽轮机性能计算所需要的所有参数在excel表格中的位置信息，附带也记录了相关参数的数值。
    # 当调用systemdemo.js中的refreshTestPoints()方法后，该变量的信息会自动更新。
    "datetime": {
        "name": "日期时间",
        "include": ["时间", "日期"],
        "exclude": ["手抄", "1", "2"],
        "href": {
            "start_date": [],
            "start": [], # "数据整理!{Y}2",
            "end": [],
        },
        "value": {
            "start_date": [],
            "start": [], # "2021-12-12 12:00",
            "end": [], # "2021-12-12 13:30",
        },
        "exists": False,
    },
    "inlet_super_high": {
        "name": "超高压缸进汽",
        "include": ["超高压缸进汽", "超高压进汽"],
        "exclude": [],
        "href": {
            "P": [], # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [], # 流量索引
            "dP": [], # 差压索引
        },
        "value": {
            "P": 0, # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
        },
    },
    "adjust_steam_super_high": {
        "name": "超高压缸调门后",
        "include": ["超高压缸调门后", "超高压调门后"],
        "exclude": [],
        "href": {
            "P": [], # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [], # 流量索引
            "dP": [], # 差压索引
        },
        "value": {
            "P": 0, # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
        },
    },
    "outlet_super_high": {
        "name": "超高压缸排汽",
        "include": ["超高压缸调门后", "超高压调门后"],
        "exclude": [],
        "href": {
            "P": [],  # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [],  # 流量索引
            "dP": [],  # 差压索引
        },
        "value": {
            "P": 0,  # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
        },
    },
    "main_steam": {
        "name": "主蒸汽", # 联合循环机组中的高压蒸汽
        "include": ["主蒸汽", "主汽门前", "主汽", "高压缸进汽", "高压蒸汽"],
        "exclude": ["中压", "低压", "小机"],
        "watch": {# 监视该测点中某参数的引用位置
                 "F": []  # 例如["汽机!{Y}23"]，表示汽机工作表中第23行引用了主汽流量，当主汽流量有值时，需要更新"汽机!{Y}23"
                 },
        "href": {
            "P": [], # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [], # 流量索引
            "dP": [], # 差压索引
            "power": [], # 功率索引
            "U": [], # 电压索引
            "I": [], # 电流索引
        },
        "value": {
            "P": 0, # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
        },
    },
    "mid_main_steam": {# 联合循环机组中有高压主汽、中压主汽、低压主汽等不同位置的测点
                      "name": "中压主蒸汽",
                      "include": ["中压主汽", "中压蒸汽", "中压主蒸汽", "中压过热器出口"],
                      "exclude": ["高压", "低压", "小机", "中压缸进汽", "中压主汽门前"], # 中压缸进汽不是中压主汽，中压主汽和高排混合后，经再热器后成为中压缸进汽
        "watch": {# 监视该测点中某参数的引用位置
                 "F": [] # 例如["汽机!{Y}23"]，表示汽机工作表中第23行引用了主汽流量，当主汽流量有值时，需要更新"汽机!{Y}23"
                 },
        "href": {
            "P": [], # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [], # 流量索引
            "dP": [], # 差压索引
            "power": [], # 功率索引
            "U": [], # 电压索引
            "I": [], # 电流索引
                         },
        "value": {
            "P": 0, # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
                         },
    },
    "low_main_steam": {# 联合循环机组中有高压主汽、中压主汽、低压主汽等不同位置的测点
                      "name": "低压主蒸汽",
                      "include": ["低压主汽", "低压蒸汽", "低压主蒸汽", "低压过热器出口"], # 低压主汽门前流量就是低压主蒸汽流量
                      "exclude": ["高压", "中压", "小机", "低压缸进汽"],  # 低压缸进汽不是低压主汽，低压主汽和中排混合后成为低压缸进汽
        "watch": {# 监视该测点中某参数的引用位置
                 "F": [] # 例如["汽机!{Y}23"]，表示汽机工作表中第23行引用了主汽流量，当主汽流量有值时，需要更新"汽机!{Y}23"
                 },
        "href": {
            "P": [], # 压力索引，例如["数据整理!{Y}4"]，这里的{Y}表示列索引未定
            "T": [],
            "H": [],
            "S": [],
            "F": [], # 流量索引
            "dP": [], # 差压索引
            "power": [], # 功率索引
            "U": [], # 电压索引
            "I": [], # 电流索引
                         },
        "value": {
            "P": 0, # 压力值
            "T": 0,
            "H": 0,
            "S": 0,
                         },
    },
    "adjust_steam": {
        "name": "调节级",
        "include": ["调节级"],
        "exclude": [],
        "exists": False, # 默认不存在调节级
    },
    "outlet_high": {
        "name": "高压缸排汽",
        "include": ["高压缸排汽", "高排", "冷再热蒸"],
        "exclude": [],
    },
    "cold_reheat_steam": {
        "name": "冷再热蒸汽",
        "include": ["冷再热", "冷再",],
        "exclude": [],
        "href": {"P": None, "T": None, "F": None},
        "value": {"P": None}
    },
    "inlet_medium": {# 再热蒸汽和中压主汽不是一个测点，中压主汽和高排混合后进入再热器加热后，成为热再蒸汽
                    "name": "再热蒸汽",
                    "include": ["再热汽门前", "热再", "再热", "中压缸进汽", "中压主汽门前"],
                    "exclude": ["冷再", "再热减温水", "再减"],
                    },
    "hot_reheat_steam": {
        "name": "该测点等同于测点：inlet_medium"
    },
    "outlet_medium": {
        "name": "中压缸排汽",
        "include": ["中排", "中压缸排汽"],
        "exclude": [],
    },
    "inlet_low": {
        "name": "低压缸进汽",  # 低压缸进汽和低压蒸汽不是一个测点，低压蒸汽和中排混合后成为低压缸进汽，低压主汽门前指的是低压主蒸汽流量
        "include": ["低压缸进汽"],
        "exclude": ["低压蒸汽", "低压主汽门前"]
    },
    "outlet_low": {
        "name": "低压缸排汽",
        "include": ["低压缸排汽", "背压"],
        "exclude": ["小机"],
        "href": {
            "H_等熵": [],
            "F_V": [], # 体积流量
            "sv": [], # 比容
            "velocity": [], # 流速
        }
    },
    "pump_turbine_vapor_out": {
        "name": "小机排汽",
        "include": ["小机排汽", "BEST机排汽"],
        "exclude": []
    },
    "extract_0": {
        "name": "零段抽汽",
        "include": ["零段抽汽", "零抽"],
        "exclude": ["至"],
        "href": {
            "P": [],
            "T": [],
            "压损": [],
        },
    },
    "extract_1": {
        "name": "一段抽汽",
        "include": ["一段抽汽", "一抽"],
        "exclude": ["至"],
        "href": {
            "P": [],
            "T": [],
            "E": [], # 能量
            "压损": [],
        },
    },
    "heater_1": {# 与抽汽级数对应的加热器名称，软件内部使用
                "name": "一号高加",  # 加热器外部显示的名称
                "drain_to": None, # 疏水去向，"heater_2"
                "href": {
                   "上端差": [],
                   "下端差": [],
                   "温升": [],
                   "F": [], # 流经一号高加的给水流量
                   },
                },
    "heater_2": {# 与抽汽级数对应的加热器名称，软件内部使用
                "name": "二号高加",
                "drain_to": None, # 疏水去向，"heater_3"
                "href": {
                   "上端差": [],
                   "下端差": [],
                   "温升": [],
                   },
                },
    "heater_3": {
        "name": "三号高加",
        "drain_to": None, # 疏水去向，"deaerator_drain_water_in"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
            "Q": [], # 高加水侧吸热量
        },
    },
    "heater_pre_3": {
        "name": "三号高加",
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
            "Q": [], # 高加水侧吸热量
        },
    },
    "heater_4": {
        "name": "四号高加",
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_5": {
        "name": "五号低加",
        "drain_to": None, # 疏水去向，"heater_6"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_6": {
        "name": "六号低加",
        "drain_to": None, # 疏水去向，"heater_7"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_7": {
        "name": "七号低加",
        "drain_to": None, # 疏水去向，heater_6_water_in，打入六号低加入口
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_8": {
        "name": "八号低加",
        "drain_to": None, # 疏水去向，"heater_9"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_9": {
        "name": "九号低加",
        "drain_to": None, # 疏水去向，"condenser"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_10": {
        "name": "十号低加",
        "drain_to": None, # 疏水去向，"condenser"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_11": {
        "name": "十一号低加",
        "drain_to": None, # 疏水去向，"condenser"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater_12": {
        "name": "十二号低加",
        "drain_to": None, # 疏水去向，"condenser"
        "href": {
            "上端差": [],
            "下端差": [],
            "温升": [],
        },
    },
    "heater": {
        "name": "加热器",
        "value": {
            "高加级数": None,
            "低加起始级数": None,
            "低加结束级数": None,
        }
    },
    "heater_1_vapor_in": {
        "name": "一号高加进汽",
        "include": ["一号高加进汽", "一进", "一高加进汽", "#1高加进汽"],
        "exclude": [],
    },
    "heater_1_vapor_out": {
        "name": "一号高加疏水",
        "include": ["一号高加疏水", "一高加疏水", "#1高加疏水"],
        "exclude": [],
        "exists": False,  # 测点是否存在，默认不存在，get_高加级数()方法会根据各个高加的疏水测点是否存在来确定高加是否存在
    },
    "heater_1_water_in": {
        "name": "一号高加进水",
        "include": ["一号高加进水", "一高加进水", "#1高加进水"],
        "exclude": [],
    },
    "heater_1_water_out": {
        "name": "一号高加出水",
        "include": ["一号高加出水", "一高加出水", "#1高加出水", ],
        "exclude": [],
        "link": None, # link指定了该点的替代点，如"1号高加出水"通常就是"2号高加进水"
        "href": {
            # href指定了该点在excel表格中的引用位置
            "P": [],
        },
    },
    "ultra_water_out": {
        "name": "最终给水",
        "include": ["最终给水"],
        "exclude": [],
        "link": ["heater_1_water_out"], # link指定了该点的替代点，按顺序查找替代点
        "href": {
            "P": [],
        },
    },
    "extract_2": {"name": "二段抽汽", "include": ["二段抽汽", "二抽"], "exclude": ["至"]},
    "heater_2_vapor_in": {
        "name": "二号高加进汽",
        "include": ["二号高加进汽", "二高加进汽", "#2高加进汽"],
        "exclude": [],
    },
    "heater_2_vapor_out": {
        "name": "二号高加疏水",
        "include": ["二号高加疏水", "二高加疏水", "#2高加疏水"],
        "exclude": [],
    },
    "heater_2_water_in": {
        "name": "二号高加进水",
        "include": ["二号高加进水", "二高加进水", "#2高加进水"],
        "exclude": [],
    },
    "heater_2_water_out": {
        "name": "二号高加出水",
        "include": ["二号高加出水", "二高加出水", "#2高加出水"],
        "exclude": [],
    },
    "extract_3": {"name": "三段抽汽", "include": ["三段抽汽", "三抽"], "exclude": ["至"]},
    "heater_pre_3_vapor_in": {
        "name": "蒸冷器进汽",
        "include": ["蒸冷器进汽"],
        "exclude": [],
    },
    "heater_pre_3_vapor_out": {
        "name": "蒸冷器进汽",
        "include": ["蒸冷器进汽"],
        "exclude": [],
    },
    "heater_pre_3_water_in": {
        "name": "蒸冷器进水",
        "include": ["蒸冷器进水"],
        "exclude": [],
    },
    "heater_pre_3_water_out": {
        "name": "蒸冷器出水",
        "include": ["蒸冷器出水"],
        "exclude": [],
    },
    "heater_3_vapor_in": {
        "name": "三号高加进汽",
        "include": ["三号高加进汽", "三高加进汽", "#3高加进汽"],
        "exclude": [],
    },
    "heater_3_vapor_out": {
        "name": "三号高加疏水",
        "include": ["三号高加疏水", "三高加疏水", "#3高加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_3_water_in": {
        "name": "三号高加进水",
        "include": ["三号高加进水", "三高加进水", "#3高加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_3_water_out": {
        "name": "三号高加出水",
        "include": ["三号高加出水", "三高加出水", "#3高加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_4": {
        "name": "四段抽汽", "include": ["四段抽汽", "四抽"], "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_4_vapor_in": {
        "name": "四号高加进汽",
        "include": ["四号高加进汽", "四高加进汽", "#4高加进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_4_vapor_out": {
        "name": "四号高加疏水",
        "include": ["四号高加疏水", "四高加疏水", "#4高加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_4_water_in": {
        "name": "四号高加进水",
        "include": ["四号高加进水", "四高加进水", "#4高加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_4_water_out": {
        "name": "四号高加出水",
        "include": ["四号高加出水", "四高加出水", "#4高加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_5": {
        "name": "五段抽汽", "include": ["五段抽汽", "五抽"],
        "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_5_vapor_in": {
        "name": "五号低加进汽",
        "include": ["五号低加进汽", "五低加进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_5_vapor_out": {
        "name": "五号低加疏水",
        "include": ["五号低加疏水", "五低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_5_water_in": {
        "name": "五号低加进水",
        "include": ["五号低加进水", "五低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_5_water_out": {
        "name": "五号低加出水",
        "include": ["五号低加出水", "五低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_6": {
        "name": "六段抽汽", "include": ["六段抽汽", "六抽"],
        "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_6_vapor_in": {
        "name": "六号低加进汽",
        "include": ["六号低加进汽", "六低加进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_6_vapor_out": {
        "name": "六号低加疏水",
        "include": ["六号低加疏水", "六低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_6_water_in": {
        "name": "六号低加进水",
        "include": ["六号低加进水", "六低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_6_water_out": {
        "name": "六号低加出水",
        "include": ["六号低加出水", "六低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_7": {
        "name": "七段抽汽", "include": ["七段抽汽", "七抽汽"],
        "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_7_vapor_in": {
        "name": "七号低加进汽",
        "include": ["七号低加进汽", "七低加进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_7_vapor_out": {
        "name": "七号低加疏水",
        "include": ["七号低加疏水", "七低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_7_water_in": {
        "name": "七号低加进水",
        "include": ["七号低加进水", "七低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_7_water_out": {
        "name": "七号低加出水",
        "include": ["七号低加出水", "七低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_8": {
        "name": "八段抽汽", "include": ["八段抽汽", "八抽"],
        "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "extract_9": {
        "name": "九段抽汽", "include": ["九段抽汽", "九抽"],
        "exclude": ["至"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8_vapor_in": {
        "name": "八号低加进汽",
        "include": ["八号低加进汽", "八低加进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8A_vapor_in": {
        "name": "八A加热器进汽",
        "include": ["八A加热器进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8B_vapor_in": {
        "name": "八B加热器进汽",
        "include": ["八B加热器进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8_vapor_out": {
        "name": "八号低加疏水",
        "include": ["八号低加疏水", "八低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8A_vapor_out": {
        "name": "八A号低加疏水",
        "include": ["八A号低加疏水", "八A低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8B_vapor_out": {
        "name": "八B号低加疏水",
        "include": ["八B号低加疏水", "八B低加疏水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8_water_in": {
        "name": "八号低加进水",
        "include": ["八号低加进水", "八低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8A_water_in": {
        "name": "八A号低加进水",
        "include": ["八A号低加进水", "八A低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8B_water_in": {
        "name": "八B号低加进水",
        "include": ["八B号低加进水", "八B低加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8_water_out": {
        "name": "八号低加出水",
        "include": ["八号低加出水", "八低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8A_water_out": {
        "name": "八A号低加出水",
        "include": ["八A号低加出水", "八A低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_8B_water_out": {
        "name": "八B号低加出水",
        "include": ["八B号低加出水", "八B低加出水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "heater_9_vapor_in": {
        "name": "九号低加进汽",
        "include": ["九低加进汽", "九号低加进汽"],
        "exclude": [],
    },
    "heater_9A_vapor_in": {
        "name": "九A加热器进汽",
        "include": ["九A低加进汽", "九A号低加进汽"],
        "exclude": [],
    },
    "heater_9B_vapor_in": {
        "name": "九B低加进汽",
        "include": ["九B低加进汽", "九A号低加进汽"],
        "exclude": [],
    },
    "heater_9_vapor_out": {
        "name": "九号低加疏水",
        "include": ["九低加疏水", "九号低加疏水"],
        "exclude": [],
    },
    "heater_9A_vapor_out": {
        "name": "九A低加疏水",
        "include": ["九A低加疏水", "九A号低加疏水"],
        "exclude": [],
    },
    "heater_9B_vapor_out": {
        "name": "九B低加疏水",
        "include": ["九B低加疏水", "九B号低加疏水"],
        "exclude": [],
    },
    "heater_9_water_in": {
        "name": "九号低加进水",
        "include": ["九低加进水", "九号低加进水"],
        "exclude": [],
    },
    "heater_9A_water_in": {
        "name": "九A低加进水",
        "include": ["九A低加进水", "九A号低加进水"],
        "exclude": [],
    },
    "heater_9B_water_in": {
        "name": "九B低加进水",
        "include": ["九B低加进水", "九B号低加进水"],
        "exclude": [],
    },
    "heater_9_water_out": {
        "name": "九号低加出水",
        "include": ["九低加出水", "九号低加出水"],
        "exclude": [],
    },
    "heater_9A_water_out": {
        "name": "九A低加出水",
        "include": ["九A低加出水", "九A号低加出水"],
        "exclude": [],
    },
    "heater_9B_water_out": {
        "name": "九B低加出水",
        "include": ["九B低加出水", "九B号低加出水"],
        "exclude": [],
    },
    "heater_10_vapor_in": {
        "name": "十号低加进汽",
        "include": ["十低加进汽", "十号低加进汽"],
        "exclude": [],
    },
    "heater_10_vapor_out": {
        "name": "十号低加疏水",
        "include": ["十低加疏水", "十号低加疏水"],
        "exclude": [],
    },
    "heater_10_water_in": {
        "name": "十号低加进水",
        "include": ["十低加进水", "十号低加进水"],
        "exclude": [],
    },
    "heater_10_water_out": {
        "name": "十号低加出水",
        "include": ["十低加出水", "十号低加出水"],
        "exclude": [],
    },
    "heater_11_vapor_in": {
        "name": "十一号低加进汽",
        "include": ["十一低加进汽", "十一号低加进汽"],
        "exclude": [],
    },
    "heater_11_vapor_out": {
        "name": "十一号低加疏水",
        "include": ["十一低加疏水", "十一号低加疏水"],
        "exclude": [],
    },
    "heater_11_water_in": {
        "name": "十一号低加进水",
        "include": ["十一低加进水", "十一号低加进水"],
        "exclude": [],
    },
    "heater_11_water_out": {
        "name": "十一号低加出水",
        "include": ["十一低加出水", "十一号低加出水"],
        "exclude": [],
    },
    "heater_12_vapor_in": {
        "name": "十二号低加进汽",
        "include": ["十二低加进汽", "十二号低加进汽"],
        "exclude": [],
    },
    "heater_12_vapor_out": {
        "name": "十二号低加疏水",
        "include": ["十二低加疏水", "十二号低加疏水"],
        "exclude": [],
    },
    "heater_12_water_in": {
        "name": "十二号低加进水",
        "include": ["十二低加进水", "十二号低加进水"],
        "exclude": [],
    },
    "heater_12_water_out": {
        "name": "十二号低加出水",
        "include": ["十二低加出水", "十二号低加出水"],
        "exclude": [],
    },

    "seal_heater_1_water_in": {
        "name": "一号轴加进水",
        "include": ["一号轴加进水", "轴加进水"],
        "exclude": [],
    },
    "seal_heater_2_water_in": {
        "name": "二号轴加进水",
        "include": ["二号轴加进水", "二轴加进水"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "seal_heater_vapor_in": {
        "name": "汽封加热器进汽",
        "include": ["汽封加热器进汽", "轴封加热器进汽", "轴加进汽",],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "seal_heater_water_in": {
        "name": "汽封加热器进水",
        "include": ["汽封加热器进", "轴封加热器进", "轴加进", "凝结水加热器进"],
        "exclude": ["进汽"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "seal_heater_water_out": {
        "name": "汽封加热器出水",
        "include": ["汽封加热器出水", "轴封加热器出水", "轴加出水", "轴加后", "凝结水加热器出"],
        "exclude": ["出汽"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    }, #  # ------------------------------
    # 热井至加热器之间测点
    # ----------------------------
    "heat_well_out": {
        "name": "热井出水",
        "include": ["热井出"],
        "exclude": []
    },
    "water_condense_pump_in": {
        "name": "凝泵进口",
        "include": ["凝泵进", "凝结水泵进"],
        "exclude": [],
    },
    "water_condense_pump_A_in": {
        "name": "凝泵A进",
        "include": ["凝泵A进"],
        "exclude": [],
    },
    "water_condense_pump_B_in": {
        "name": "凝泵B进",
        "include": ["凝泵B进"],
        "exclude": [],
    },

    "water_condense_pump_out": {
        "name": "凝泵出水",
        "include": ["凝泵出", "凝结水泵出", "凝结水温度", "凝结水压力", "余热锅炉凝结水"],
        "exclude": ["除氧器", "轴加出", "FGH", "低压汽包入口"],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },

    "pump_condense_water_out": {
        "name": "该测点别名为：water_condense_pump_out"
    },

    "water_condense_pump_A_out": {
        "name": "凝泵A出水",
        "include": ["凝泵A出"],
        "exclude": [],
    },
    "water_condense_pump_B_out": {
        "name": "凝泵B出水",
        "include": ["凝泵B出"],
        "exclude": [],
    },


    "hrsg_low_water_in": {
        "name": "余热锅炉入口低压给水",
        "include": ["凝结水预热器入口", "余热锅炉入口", "低压省煤器入口"],
        "exclude": ["烟气"],

    },


    "eco_low_water_out": {
        "name": "余热锅炉低压省煤器出口",
        "include": ["低压省煤器出口", "凝结水预热器出口"],
        "link": ["hrsg_low_water_out"],  # 当低压省煤器出口参数没有时，查找
    },


    #  # ------------------------------
    # 低加出口至高加进口之间测点
    # ----------------------------
    "main_condense_water": {# 该测点为进凝泵出口管道测点
                           "name": "主凝结水",
                           "include": [
                              "主凝结水",
                               "余热锅炉进口凝结水",
                              ],
                           "exclude": ["凝结水流量"], # 凝结水流量一般指的是除氧器进水流量，但凝结水的其他参数指的一般是凝泵出口参数
                           },
    "deaerator_vapor_in": {
        "name": "除氧器进汽",
        "include": ["除氧器进汽"],
        "exclude": [],
    },
    "deaerator_drain_water_in": {
        "name": "进除氧器疏水",
        "include": ["进除氧器疏水"],
        "exclude": [],
    },
    "deaerator_water_in": {
        "name": "除氧器进水",
        "include": [
            "除氧器进水",
            "进除氧器凝结水",
            "除氧器进口凝结水", "ASME喷嘴入口凝结水"],
        "exclude": [],
    },
    "deaerator_water_out": {
        "name": "除氧器出水",
        "include": ["除氧器出水", "除氧器下水"],
        "exclude": [],
    },
    "deaerator_water_lvl": {
        "name": "除氧器水位",
        "include": ["除氧器水位", "除氧器液位"],
        "exclude": [],
        "href": {"start": [], "end": [], "as_F": []}, # 开始水位，结束水位，当量流量
    },
    "pump_turbine_vapor_in": {
        "name": "小机进汽",
        "include": ["小机进汽", "给水泵汽轮机进汽", "BEST机进汽"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "best_adjust_steam": {
        "name": "BEST机调门后",
        "include": ["BEST机调门后"],
        "exclude": [],
    },

    "pump_before_water_in": {
        "name": "前置泵进水",
        "include": ["前置泵进"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "pump_before_water_out": {
        "name": "前置泵出水",
        "include": ["前置泵出"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "feed_pump_in": {
        "name": "给水泵进水",
        "include": ["给水泵进", "汽泵进"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "feed_pump_out": {
        "name": "给水泵出水",
        "include": ["给水泵出", "汽泵出"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    "final_feed_water": {
        "name": "最终给水", "include": ["最终给水"], "exclude": [],
        "href": {
            "P": None,
            "T": None,
            "F": None,
            "F_计算值": None,
        },
        "value": {"P": None, "T": None, }
    },
    "feed_water_low": {
        "name": "低压给水", # 燃机测点
        "include": ["低压给水", "低压汽包进", "低压汽包入口"],
        "exclude": []
    },

    "feed_water_mid": {# 中压给水流量（运行值）
                      "name": "中压给水",
                      "include": ["中压给水"],
                      "exclude": ["燃料", "FGH"],
                      },

    "feed_water_high": {
        "name": "高压给水",
        "include": ["高压给水"],

    },

    "drum_low_water_in": {
        "name": "低压汽包入口",
        "include": ["低压汽包入口"],
        "exclude": [],
        "link": ["eco_low_water_out"], # 低压汽包入口给水可以取低压省煤器出水
    },


    "drum_low": {
        "name": "低压汽包",
        "include": ["低压汽包"]
    },

    "drum_mid": {
        "name": "中压汽包",
        "include": ["中压汽包"]
    },

    "drum_high": {
        "name": "高压汽包",
        "include": ["高压汽包"]
    },

    "water_reheater_reducing": {
        "name": "再热减温水",
        "include": ["再减", ["再热", "减温水"], ["中压", "减温水"]],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },
    # water_overheat_reducing_1: {"include": ["过热一级减温水"], "exclude": []},
    # water_overheat_reducing_2: {"include": ["过热二级减温水"], "exclude": []},
    "water_overheat_reducing": {
        "name": "过热减温水",
        "include": ["过热减温水", "过热器减温水", "过减"],
        "exclude": [],
        "href": {"P": None, "T": None, },
        "value": {"P": None, "T": None, }
    },

    "p_env": {
        "name": "大气压力",
        "include": ["大气压力"],
        "exclude": []
    },
    "env": {
        "name": "环境",
        "include": ["大气压力", "环境温度", "干球温度", "相对湿度", ["空气", "湿度"], ["大气", "湿度"], ["环境", "湿度"], "大气温度"], # 相对湿度和湿度有两种写法
        "exclude": ["出口", "变化"],  # 排除类似 环境温度变化量 这类参数

    },

    "condenser_water_lvl": {
        "name": "凝汽器水位",
        "include": ["凝汽器水位", "凝汽器液位", "排汽装置液位", "排汽装置水位"],
        "exclude": [],
        "href": {"start": [], "end": [], "as_F": []}, # 开始水位，结束水位，当量流量
    },
    "condenser": {
        "name": "凝汽器",
        "include": [],
        "href": {},

    },
    "economizer_water_outlet": {
        "name": "低温省煤器出水",
        "include": ["省煤器出", "省煤器回", "低省出", "低省回"],
        "exclude": [],
        "link": ["hrsg_low_water_out"], # 联合循环中，余热锅炉低压省煤器出口就是低压省煤器出口
    },
    "economizer_water_inlet": {
        "name": "低温省煤器进水",
        "include": ["省煤器进水", "低省进口"],
        "exclude": [],
        "link": ["hrsg_low_water_in"], # 联合循环中，余热锅炉低压省煤器进口就是低温省煤器进口
    },


    "bypass_high_water": {
        "name": "高加旁路给水",
        "include": ["高加旁路给水"],
        "href": {
            "F": [], # 高加旁路给水流量，默认为0
        },
    },



    "condenser_recycled_water_in": {
        "name": "凝汽器循环水进水",
        "include": [["循环水", "入"], ["循环水", "进"]], # 元素为列表表示元素的所有子元素必须都包含才匹配
        "exclude": ["A", "a", "B", "b", "塔"],  # 排除时，多个同义词都要排除
    },
    "condenser_A_recycled_water_in": {
        "name": "凝汽器A侧循环水进水",
        "include": [["循环水", "A", "入"], ["循环水", "A", "进"]],
        "exclude": ["B", "b", "塔"],
    },
    "condenser_B_recycled_water_in": {
        "name": "凝汽器B侧循环水进水",
        "include": [["循环水", "B", "入"], ["循环水", "B", "进"]],
        "exclude": ["A", "a", "塔"],
    },
    "condenser_recycled_water_out": {
        "name": "凝汽器循环水出水",
        "include": [["循环水", "出"], ["循环水", "回"]],
        "exclude": ["A", "a", "B", "b", "塔"],
    },
    "condenser_A_recycled_water_out": {
        "name": "凝汽器A侧循环水出水",
        "include": [["循环水", "A", "出"], ["循环水", "A", "回"]],
        "exclude": ["B", "b", "塔"],
    },
    "condenser_B_recycled_water_out": {
        "name": "凝汽器B侧循环水出水",
        "include": [["循环水", "B", "出"], ["循环水", "B", "回"]],
        "exclude": ["A", "a", "塔"],
    },
    "gas_turbine_in": {
        "name": "燃气轮机进口空气",
        "include": ["压气机入口", "燃机入口空气", "入口空气", "压气机进口", ["空气滤网", "温度"]],
        "exclude": ["冷却塔"],
        "href": {"T": None, },
        "value": {"T": None, },
    },

    "gas_turbine_out": {
        "name": "燃机排气",
        "include": ["燃机排气", "余热锅炉入口烟气", "余热锅炉进口烟气"],
        "exclude": [],
        "href": {"T": None, },
        "value": {"T": None, },
    },

    "regulator_station": {
        "name": "调压站天然气",
        "include": ["调压站"],
        "exclude": [],
    },

    "fgh_gas_in": {
        "name": "FGH进口天然气",
        "include": ["FGH入口天然气", "前置模块天然气", "前置模块燃料气", "前置模块进口燃料气"],
        "exclude": [],
    },

    "fgh_gas_out": {
        "name": "FGH出口天然气",
        "include": ["FGH出口天然气", "性能加热器出口燃料气", "FGH出口燃气", "性能加热器出口天然气", "燃料加热器出口天然气", "燃料加热器出口燃料气"],
        "exclude": [],
    },

    "fgh_water_in": {
        "name": "FGH进水",
        "include": ["FGH入口凝结水", "燃料加热器进水", "FGH进水", "性能加热器进水"],
        "exclude": [],
    },

    "fgh_water_out": {
        "name": "FGH回水",
        "include": ["FGH出口凝结水", "燃料加热器回水", "FGH回水", "性能加热器回水"],
        "exclude": [],
    },

    "group": {
        "name": "机组",
        "include": [],
        "exclude": [],
        "href": {
            "hr": [],
            "hr_correct1": [],
            "hr_correct2": [],
            "net_power": [], # 机组净功率
            "shaft_power": [], # 机组轴功率 = 发电机功率/发电机效率
        },
    },
    "generator_gas_turbine": {# 对于多轴联合循环机组有多个发电机，需要分开处理
                             "name": "燃机发电机",
                             "include": ["燃机发电机"], # 用户的测点名为"功率"时，一般指的都是发电机输出功率
                             "exclude": ["励磁"],
                             "href": {
                                "power": [],
                                "eta": [], # 发电机效率
                                "factor": [], # 功率因数
                                "freq": [], # 发电机频率
                                "p_h2": [], # 氢压
                                },
                             },
    "generator_turbine": {
        "name": "汽轮机发电机",
        "include": ["汽机发电机", "汽轮发电机", "汽轮机发电机"], # 用户的测点名为"功率"时，一般指的都是发电机输出功率
        "exclude": ["励磁"],
        "href": {
            "power": [],
            "eta": [], # 发电机效率
            "factor": [], # 功率因数
            "freq": [], # 发电机频率
            "p_h2": [], # 氢压
        },
    },
    "generator": {
        "name": "发电机",
        "include": ["功率", "发电机", "总负荷"], # 用户的测点名为"功率"时，一般指的都是发电机输出功率
        "exclude": ["励磁", "燃机", "燃气轮机"],
        "href": {
            "power": [],
            "eta": [], # 发电机效率
            "factor": [], # 功率因数
            "freq": [], # 发电机频率
            "p_h2": [], # 氢压
        },
    },
    "excitation": {
        "name": "励磁",
        "include": ["励磁"],
        "href": {
            "U": [],
            "I": [],
            "power": [],
        }
    },
    "turbine_high": {
        "name": "高压缸",
        "include": ["高压缸效率"],
        "exclude": [],
        "href": {
            "eta": [],
            "主汽至一抽段流量": [],
            "一抽至高排段流量": [],
            "shaft_power": [],
        },
    },
    "turbine_medium": {
        "name": "中压缸",
        "include": ["中压缸效率"],
        "exclude": [],
        "href": {
            "eta": [],
            "四抽至中排段流量": [],
            "四抽至中排段功率": [],
            "shaft_power": [],
        },
    },
    "turbine_low": {
        "name": "低压缸",
        "include": ["低压缸效率", "低压缸末级叶片环形面积", "排汽面积"],
        "exclude": [],
        "href": {
            "eta": [],
            "eta_计算值": [],
            "eta1": [],
            "shaft_power": [],
            "area": [], # 排汽面积
            "loss_排汽": [], # 排汽损失
        },
    },

    "reheater": {
        "name": "再热器",
        "include": ["再热器"],
        "exclude": ["压力", "温度", "流量"],
        "href": {
            "压损": []
        }
    },

    "hrsg_flue_out": {
        "name": "余热锅炉排烟",
        "include": ["余热锅炉排烟", "余热锅炉排气"],

    },


    "leakage": {
        "name": "漏汽信息", "include": ["漏汽"], "exclude": [],
        "href": {
            "高压端漏汽总量": [],
            "高压门杆漏汽量": [],
            "高压门杆一漏流量": [],
            "高压门杆二漏流量": [],
            "高压前轴封漏汽量": [],
            "高压前轴封一漏流量": [],
            "高压后轴封漏汽量": [],
            "中压前轴封漏汽量": [],
            "中压前轴封漏汽焓": [],
            "中压后轴封漏汽量": [],
        },
        "value": {},
        "obj": None,  # 字典中的对象值不能是new Leakage()，否则会报错，且错误非常难以察觉
    },
    "leakage_known": {
        "name": "明漏量",
        "include": ["明漏量"],
        "exclude": ["不明"],
        "href": {"F": []},
    },
    "leakage_unknown": {
        "name": "不明漏量",
        "include": ["不明漏量"],
        "exclude": [""],
        "href": {
            "F": [],
            "percentage_boiler": [],
            "percentage_turbine": [],
            "rate": [], # 不明漏率
        },
    },

    "design_para": {
        "name": "设计参数",
        "href": {
            "T0": [], # 设计环境温度
            "P0": [], # 设计大气压力
            "humid0": [], # 设计环境湿度
        }
    },

    "curve_correct": {
        "name": "修正曲线",
        "href": {
            "f_T0_power": None, # 环境温度对功率的修正曲线
            "f_P0_power": None, # 大气压力对功率的修正曲线
            "f_humid0_power": None, # 环境湿度对功率的修正曲线
            "f_T0_hr": None, # 环境温度对热耗率的修正曲线
            "f_P0_hr": None, # 大气压力对热耗率的修正曲线
            "f_humid0_hr": None, # 环境湿度对热耗率的修正曲线
        }
    },

    "correct_factor": {
        "name": "修正系数",
        "href": {
            "delta_T0": [], # 试验环境温度和设计环境温度差值
            "delta_P0": [],
            "delta_humid0": [],
            "f_T0_power": [], # 环境温度对功率的修正系数
            "f_P0_power": [], # 大气压力对功率的修正系数
            "f_humid0_power": [], # 环境湿度对功率的修正系数
            "f_T0_hr": [], # 环境温度对热耗率的修正系数
            "f_P0_hr": [], # 大气压力对热耗率的修正系数
            "f_humid0_hr": [], # 环境湿度对热耗率的修正系数
        },

    },

    
}
