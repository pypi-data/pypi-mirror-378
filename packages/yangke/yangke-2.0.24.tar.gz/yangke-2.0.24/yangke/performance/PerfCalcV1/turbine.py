from yangke.performance.PerfCalcV1.ExcelOp import ExcelOp


def create_turbine_sheet(excel_op: ExcelOp, sheet_name=None):
    if sheet_name is None:
        sheet_name = "汽机"

    if excel_op.has_sheet("数据整理"):
        # 如果当前工作簿中存在“数据整理”工作表
        if not excel_op.has_sheet(sheet_name):
            # 如果不存在sheet_name代表的工作表，则创建
            excel_op.add_sheet(sheet_name)
            # 新创建的"汽机"工作表需要添加表头
            add_title_region(excel_op, sheet_name)
        else:
            print("已经存在名为" + sheet_name + "的工作表！")

    else:
        print("未找到“数据整理”工作表，因此无法获得计算所需的数据源，无法计算汽轮机性能，请检查！")
        return False
    return True




def add_title_region(excel_op: ExcelOp, sheet_name):
    """
    添加数据计算表的表头，表头包括"项目", "开始日期", "开始时间", "结束时间"
    """
    cols = excel_op.getLastColumnIndexOfSheet(sheet_name)
    formulas = []
    row=1
    for i in range(2, cols):
        y_char = excel_op.num_2_column_char(i)
        formulas.append({"row": row, "col": i, "formula": excel_op.form_formula2("数据整理!{row}", y_char, row)})
        formulas.append({"row": row+1, "col": i, "formula": excel_op.form_formula2("数据整理!{row+1}", y_char, row)})
        formulas.append({"row": row+2, "col": i, "formula": excel_op.form_formula2("数据整理!{row+2}", y_char, row)})
        formulas.append({"row": row+3, "col": i, "formula": excel_op.form_formula2("数据整理!{row+3}", y_char, row)})
    excel_op.set_formulas(sheet_name, formulas)
