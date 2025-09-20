from ExcelOp import ExcelOp
import pandas as pd
import eu as eu
from turbine import create_turbine_sheet

excel: ExcelOp | None = None
proj_settings: dict = {}
sp = eu.StandardPoint  # 储存核心的测点信息


def load_data(file=r"C:\Users\54067\Desktop\华能瑞金电厂二期3号机组机组性能考核试验-计算测试.xlsm"):
    global excel
    excel = ExcelOp(file)


def refreshTestPoints():
    """
    该方法扫描”数据整理“工作表中第2列变量名，并根据参数名将excel中的引用位置链接到enum.StandardTestPoint中，以方便后续计算时直接引用测点，在后续计算时则可以使用 main_steam.P 等方式引用测点的数据所在的位置。

    * @param {boolean} 是否需要递归调用以确保初始化扫描测点
    * @type {string}
    """
    rows = excel.getLastRowIndexOfSheet("数据整理")
    for i in range(2, rows):
        # 遍历每一行的测点名，前四行分别是”项目“，”开始日期“，”开始时间“，”结束时间“，因此从第5行开始
        user_defined_name = excel.get_cell_value(i, 2, "数据整理")
        if user_defined_name and not pd.isna(user_defined_name):
            # 将当前测点分配到标准测点清单中
            dispatch_point(user_defined_name, i, "数据整理", sp)
            if "取压方式" in user_defined_name:  # 数据整理下方的流量原件计算区域不扫描
                break


def dispatch_point(var_name, i, sheet, sp1):
    """
    将用户自定义的变量参数归类到标准测点清单中，var_name为试验期间 用户输入的测点名，例如"高压主汽温度"。该方法操作后，每个找到的测点将会增加exists属性，用于记录机组中是否存在该标准测点。
     sp1是标准测点对象，只能是eu.StandardPoint或者eu.StandardPointOrigin
     例如：
     dispatch_point("高压蒸汽压力", 20, "数据整理")，该语句会将eu.StandardPoint中main_steam.P参数的href设置为数据整理表中的第20行，以后使用main_steam.P引用时，会自动引用到指定位置的数据
     * @param var_name 测点名成
     * @param i 测点所属的行号
     * @returns {Array}
    """
    # 首先获得用户输入测点名的可能变化，如：1号高加=一号高加
    # 只有下划线前的字符串用来判断测点位置，后面的字符串是表号和单位，弃掉，否则会影响A、B侧之类测点的判断
    var_name = var_name.split("_")[0]
    var_name = var_name.split("(")[0]  # 括号里的字符串为备注信息，也不参与测点信息判断
    name_list = extend_list_by_alternative_symbols(var_name)
    # 获取对应的标准测点名
    _sd = get_standard_point(name_list)
    if _sd is not None:
        if sheet == "数据整理":
            bak_info = str(excel.get_cell_value_by_pos(f"数据整理!A{i}"))
            if bak_info == "参考" or "不准" in bak_info:
                return None
        standard_point = _sd[0]
        para = _sd[1]

        if sp1.get(standard_point).get("href") is None:
            # 如果当前测点没有href属性，就创建
            sp1[standard_point]["href"] = {}
        # 当前测点有href属性，但不存在对应的para参数时，创建对应参数数据
        para_s = sp1[standard_point]["href"].get(para)
        href = sheet + "!{Y}" + str(i)
        if para_s is None or len(para_s) == 0:
            sp1[standard_point]["href"][para] = [href, ]
            sp1[standard_point]["exists"] = True
            if "heater" in standard_point:
                for i in ["1", "2", "3", "pre_3", "4", "5", "6", "7", "8", "9"]:
                    pos_name = ["heater_" + i + "_vapor_in", "heater_" + i + "_vapor_out", "heater_" + i + "_water_in",
                                "heater_" + i + "_water_out", ]
                    if standard_point in pos_name:  # 如果发现任一个加热器的测点，则加热器存在
                        sp1["heater_" + i]["exists"] = True
                    break
        else:
            if href not in para_s:
                sp1[standard_point]["href"][para].append(href)

    return None


def extend_list_by_alternative_symbols(origin_list, alter_symbol=None):
    """
     * 将列表中的可替换字符串更换形式，从而形成更全面的字符串
     *
     *     例如：
     *     origin=["1号高加进汽压力"]
     *     origin=extend_list_by_alternative_symbols(origin, {"1": "一", "汽": "气"})
     *     则结果为：
     *     origin=['1号高加进汽压力', '一号高加进汽压力', '1号高加进气压力', '一号高加进气压力']
    """
    if not alter_symbol:
        alter_symbol = eu.alternative_symbol

    if isinstance(origin_list, str):
        origin_list = [origin_list]

    for item in origin_list:
        for k, v in alter_symbol.items():
            new_item = item.replace(k, v)
            if new_item not in origin_list:
                origin_list.append(new_item)

            new_item = item.replace(v, k)
            if new_item not in origin_list:
                origin_list.append(new_item)

    return origin_list


def get_standard_point(name_list, sp=eu.StandardPoint):
    """
     *  获取给定的name_list属于哪个测点，该测点只指定了位置，不指定具体的参数，如高压主蒸汽，但是压力还是温度不确定
     *  例如:
     *  get_standard_point(["高压主汽压力", "高压主气压力"])， 返回["main_steam", "P"]
    """

    # --------------------------- 先判断name_list属于StandardPoint中哪一个测点下 --------------------------------
    matched_pos = None
    for k, v in sp.items():
        include = v.get("include")  # 有些点没有include，因此不能用中括号方式取值
        exclude = v.get("exclude")
        if not include:  # 如果include为空，则进行下一次循环
            continue

        for cur_name in name_list:  # 遍历用户传入的测点名
            for instr in include:
                if isinstance(instr, str):  # 如果include中的元素是字符串
                    if instr in cur_name:  # 如果用户传入的测点名字符串中包含StandardPoint中指定的include名，则处理该测点
                        flag = True
                        if exclude:
                            for ex_str in exclude:
                                if ex_str in cur_name:
                                    flag = False
                                    break

                        if flag:  # 如果测点名没有被exclude排除掉，则继续
                            matched_pos = k  # 如果找到了测点，则退出循环
                            break

                    else:
                        pass
                        # 如果未找到测点，则继续判断name_list中的下一个同义词测点名是否匹配当前测点位置

                elif isinstance(instr, list):  # 如果include中的元素是列表
                    matched = True
                    for _instr in instr:
                        if _instr not in cur_name:
                            matched = False
                            break

                    if matched:
                        flag = True
                        if exclude:
                            for ex_str in exclude:
                                if ex_str in cur_name:
                                    flag = False
                                    break

                        if flag:
                            matched_pos = k
                            break

            if matched_pos is not None:
                break

        if matched_pos is not None:
            break

    # --------------------------- 先判断name_list属于StandardPoint中哪一个测点下 --------------------------------
    if matched_pos is None:
        return None
    elif matched_pos in ["regulator_station", "fgh_gas_in", "fgh_gas_out", "fgh_water_in", "fgh_water_out",
                         "generator_gas_turbine", "hrsg_flue_out", "feed_water_mid", "feed_water_low"]:
        proj_settings.__setattr__("group_type", "联合循环1")

    # --------------------------- 匹配具体的值类型 --------------------------------------------
    _name = name_list[0]
    para = None
    if "压力" in _name or "背压" in _name:
        para = "P"
    elif "温度" in _name:
        para = "T"
    elif "差压" in _name and "差压计算" not in _name:  # 差压计算的一般是流量
        para = "dp"
    elif "流量" in _name:
        para = "F"
    elif "焓值" in _name:
        para = "H"
    elif "熵值" in _name:
        para = "S"
    elif "功率因数" in _name:
        para = "factor"
    elif "功率" in _name:
        para = "power"
    elif "频率" in _name:
        para = "freq"
    elif "电压" in _name:
        para = "U"
    elif "电流" in _name:
        para = "I"
    elif "面积" in _name:  # (lodash.includes(_name, "面积")) {
        para = "area"
    elif "效率" in _name:  # (lodash.includes(_name, "效率")) {
        para = "eta"
    else:  # 水位测点单独处理
        if matched_pos == "condenser_water_lvl" or matched_pos == "deaerator_water_lvl":
            if "开始" in _name:
                para = "start"
            elif "结束" in _name:  # (lodash.includes(_name, "结束")) {
                para = "end"

        elif matched_pos == "datetime":  # 日期时间测点单独处理
            if "日期" in _name:  # (lodash.includes(_name, "日期")) {
                para = "start_date"
            elif "开始" in _name:  # (lodash.includes(_name, "开始")) {
                para = "start"
            elif "结束" in _name:  # (lodash.includes(_name, "结束")) {
                para = "end"

        elif matched_pos == "leakage_known":
            para = "F"
        elif matched_pos == "leakage_unknown":  # 不明漏量测点单独处理
            if "占比" in _name or "百分比" in _name:
                if "炉侧" in _name or "锅炉" in _name:
                    para = "percentage_boiler"
                else:
                    para = "percentage_turbine"
    # --------------------------- 匹配具体的值类型 --------------------------------------------

    return [matched_pos, para]


def init_turbine():
    # 高加级数 = get_高加级数()
    # 低加级数 = get_低加级数()
    pass


def 漏汽(start_row):
    """
    从start_row行开始填充计算的漏汽信息
    """
    data = [
        ["漏汽量", "主蒸汽流量", "t/h"],  # row + 2
        ["", "", ""],
        ["", "超高压缸前轴封漏汽流量", "t/h"],
        ["", "超高压缸前轴封一漏流量", "t/h"],
        ["", "超高压缸前轴封一漏焓值", "t/h"],
        ["", "超高压缸前轴封一漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸前轴封二漏流量", "t/h"],
        ["", "超高压缸前轴封二漏焓值", "t/h"],
        ["", "超高压缸前轴封二漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸前轴封三漏流量", "t/h"],
        ["", "超高压缸前轴封三漏焓值", "t/h"],
        ["", "超高压缸前轴封三漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸前轴封四漏流量", "t/h"],
        ["", "超高压缸前轴封四漏焓值", "t/h"],
        ["", "超高压缸前轴封四漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸后轴封漏汽流量", "t/h"],
        ["", "超高压缸后轴封一漏流量", "t/h"],
        ["", "超高压缸后轴封一漏焓值", "t/h"],
        ["", "超高压缸后轴封一漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸后轴封二漏流量", "t/h"],
        ["", "超高压缸后轴封二漏焓值", "t/h"],
        ["", "超高压缸后轴封二漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸后轴封三漏流量", "t/h"],
        ["", "超高压缸后轴封三漏焓值", "t/h"],
        ["", "超高压缸后轴封三漏能量", "t/h"],
        ["", "", ""],
        ["", "超高压缸后轴封四漏流量", "t/h"],
        ["", "超高压缸后轴封四漏焓值", "t/h"],
        ["", "超高压缸后轴封四漏能量", "t/h"],
        ["", "", ""],
        ["", "高压门杆漏汽量", "t/h"],  # row + 4
        ["", "高压门杆漏汽焓", "kJ/kg"],
        ["", "高压门杆一漏流量", "t/h"],
        ["", "高压门杆二漏流量", "t/h"],  # row + 7
        ["", "高压门杆三漏流量", "t/h"],  # row + 8
        ["", "高压门杆四漏流量", "t/h"],  # row + 9
        ["", "", ""],
        ["", "高压前轴封漏汽量", "t/h"],  # row + 11
        ["", "高压前轴封漏汽焓", "kJ/kg"],
        ["", "高压前轴封一漏流量", "t/h"],  # row + 13
        ["", "高压前轴封二漏流量", "t/h"],
        ["", "高压前轴封三漏流量", "t/h"],
        ["", "高压前轴封四漏流量", "t/h"],
        ["", "", ""],
        ["", "高压后轴封漏汽量", "t/h"],  # row + 18
        ["", "高压后轴封漏汽焓", "kJ/kg"],
        ["", "高压后轴封一漏流量", "t/h"],  # row + 20
        ["", "高压后轴封二漏流量", "t/h"],
        ["", "高压后轴封三漏流量", "t/h"],
        ["", "高压后轴封四漏流量", "t/h"],
        ["", "", ""],
        ["", "中压前轴封漏汽量", "t/h"],  # row + 25
        ["", "中压前轴封漏汽焓", "kJ/kg"],
        ["", "中压前轴封一漏流量", "t/h"],  # row + 27
        ["", "中压前轴封二漏流量", "t/h"],
        ["", "中压前轴封三漏流量", "t/h"],
        ["", "中压前轴封四漏流量", "t/h"],
        ["", "", ""],
        ["", "中压后轴封漏汽量", "t/h"],  # row + 32
        ["", "中压后轴封漏汽焓", "kJ/kg"],
        ["", "中压后轴封一漏流量", "t/h"],  # row + 34
        ["", "中压后轴封二漏流量", "t/h"],
        ["", "中压后轴封三漏流量", "t/h"],
        ["", "中压后轴封四漏流量", "t/h"],
        ["", "", ""],
        ["", "低压前轴封漏汽量", "t/h"],  # row + 39
        ["", "低压前轴封漏汽焓", "kJ/kg"],
        ["", "低压前轴封一漏流量", "t/h"],  # row + 41
        ["", "低压前轴封二漏流量", "t/h"],
        ["", "低压前轴封三漏流量", "t/h"],
        ["", "低压前轴封四漏流量", "t/h"],  # row + 44
        ["", "", ""],
        ["", "低压后轴封漏汽量", "t/h"],  # row + 46
        ["", "低压后轴封漏汽焓", "kJ/kg"],
        ["", "低压后轴封一漏流量", "t/h"],  # row + 48
        ["", "低压后轴封二漏流量", "t/h"],
        ["", "低压后轴封三漏流量", "t/h"],
        ["", "低压后轴封四漏流量", "t/h"],  # row + 51
        ["", "", ""],
        ["", "均压箱至低压后轴封供汽流量", "t/h"]
    ]

    excel.set_cells("汽机", start_row + 2, 1, data)
    # excel.set_cells_color("汽机", start_row + 2, 1, 4)


if __name__ == '__main__':
    load_data()
    refreshTestPoints()
    create_turbine_sheet(excel,"汽机")
    漏汽(5)
