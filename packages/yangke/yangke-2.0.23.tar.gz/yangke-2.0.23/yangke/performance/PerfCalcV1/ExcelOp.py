import re
from yangke.common.fileOperate import read_excel
import pandas as pd
import math
import xlwings as xw


class ExcelOp:
    def __init__(self, file):
        self.file = file
        self.new_file = file.replace(".xlsx", "_new.xlsx")
        self.data = read_excel(file, index_col=None, header=None)

    def set_formula(self, sheet, row, col, formula):
        """
        实时修改Excel文件中指定sheet、行和列的公式
        :param sheet: sheet名称
        :param row: 行号(从1开始)
        :param col: 列号(从1开始)或列字母(如'A')
        :param formula: Excel公式字符串
        """
        if isinstance(col, str):
            col = self.column_char_2_num(col)

        # 使用xlwings实时修改Excel公式
        with xw.App(visible=False) as app:
            wb = app.books.open(self.new_file)
            ws = wb.sheets[sheet]
            ws.range((row, col)).formula = formula
            wb.save()
            wb.close()

    def set_formulas(self, sheet, formulas):
        """
        批量修改Excel中多个单元格的公式
        :param sheet: sheet名称
        :param formulas: 公式列表，格式为[{"row":行号,"col":列号或列字母,"formula":公式},...]
        """
        with xw.App(visible=False) as app:
            wb = app.books.open(self.new_file)
            ws = wb.sheets[sheet]

            for formula_item in formulas:
                row = formula_item["row"]
                col = formula_item["col"]
                formula = formula_item["formula"]

                if isinstance(col, str):
                    col = self.column_char_2_num(col)

                ws.range((row, col)).formula = formula

            wb.save()
            wb.close()

    def set_cell_color(self, sheet, row, col, color):
        """
        实时修改Excel文件中指定sheet、行和列的颜色
        :param sheet: sheet名称
        :param row: 行号(从1开始)
        :param col: 列号(从1开始)或列字母(如'A')
        :param color: 颜色
        """
        if isinstance(col, str):
            col = self.column_char_2_num(col)

        with xw.App(visible=False) as app:
            wb = app.books.open(self.new_file)
            ws = wb.sheets[sheet]
            ws.range((row, col)).color = color
            wb.save()
            wb.close()

    def set_cells_color(self, sheet, cells):
        """
        批量设置Excel中多个单元格的颜色
        :param sheet: sheet名称
        :param cells: 单元格列表，格式为[{"row":行号,"col":列号或列字母,"color":颜色},...]
        """
        with xw.App(visible=False) as app:
            wb = app.books.open(self.new_file)
            ws = wb.sheets[sheet]

            for cell in cells:
                row = cell["row"]
                col = cell["col"]
                color = cell["color"]

                if isinstance(col, str):
                    col = self.column_char_2_num(col)

                ws.range((row, col)).color = color

            wb.save()
            wb.close()

    def get_row_from_pos_string(self, pos_string):
        """
         * 从形如"汽机!D23"的字符串中获取行号，即23，如果pos_string是数据，则只读取数组中的第一个单元
        """
        if not pos_string:
            return None

        if isinstance(pos_string, list):
            pos_string = pos_string[0]

        pos_string = str(pos_string)
        pos_string = pos_string.strip()
        if not pos_string:
            return None
        _sb_ = pos_string.split("!")
        sub_pos = _sb_[-1]  # 取_sb_列表的最后一项
        # 取匹配到的第一个数字字符串,re.search() 只会匹配第一个符合条件的结果，找到后立即停止，不会继续向后搜索
        match = re.search(r'\d+', sub_pos)
        _sb_ = match.group()
        if _sb_:
            return int(_sb_)
        else:
            return None

    def get_col_from_pos_string(self, pos_string):
        if not pos_string:  # 空字符串也会返回None
            return None

        if isinstance(pos_string, list):
            pos_string = pos_string[0]

        pos_string = str(pos_string)
        pos_string = pos_string.strip()
        if not pos_string:
            return None
        _sb_ = pos_string.split("!");
        sub_pos = _sb_[-1]  # 取_sb_列表的最后一项
        _sb_ = re.search(r'[A-Za-z]+', sub_pos)  # 取匹配到的第一个字符串
        if _sb_:
            return _sb_.group().strip()
        else:
            return None

    def column_char_2_num(self, y):
        """
        *将Excel中以字母表示的列名转换为数字，因为程序中只能识别以数字排序的列，如A表示第1列
        * @ type {string}
        """
        if isinstance(y, int):
            return y
        y = y.strip()
        y = y.upper()

        if len(y) == 1:
            y = ord(y) - 64  # 'A'的编码是65，'A'列即第1列，excel中从(1, 1)开始，没有(0, 0)单元格。
        elif len(y) == 2:
            _ = y[0]
            _ = (ord(_) - 64) * 26
            y = ord(y[1]) - 64 + _
        else:
            print("列索引超范围，目前只支持A-ZZ之间的列索引，出错列索引为：" + y)
            raise Exception("列索引超范围，目前只支持A-ZZ之间的列索引，出错列索引为：" + y)
        return y

    def num_2_column_char(self, y: int | str):
        """
        将数字索引转换为excel的列名，如第1列返回'A'
        """
        if isinstance(y, str):
            return y
        res = ""
        x = math.floor(y / 26)
        if x > 0:
            res = chr(x + 64)
        x = y % 26
        res = res + chr(x + 64)
        return res

    def get_cell_value_by_pos(self, pos_str):
        """
         * 根据位置字符串表示的单元的值，如pos="原始数据!E20", pos="E20"等
         * @private
        """
        _ = pos_str.split("!")
        if len(_) == 1:
            sheet_name = None
        else:
            sheet_name = _[0]

        row = self.get_row_from_pos_string(pos_str)
        col = self.get_col_from_pos_string(pos_str)
        res = self.get_cell_value(row, col, sheet_name)
        return res

    def get_cell_value(self, row, col, sheet):
        """
        获取excel中某个单元格的值
        """
        df = self.data[sheet]
        if isinstance(col, str):
            col = self.column_char_2_num(col)

        return df.iat[row - 1, col - 1]

    def getLastRowIndexOfSheet(self, sheet):
        """
        获取指定sheet内容的行数
        """
        if sheet is None or self.data is None:
            return None

        df = self.data[sheet]
        return df.shape[0]

    def getLastColumnIndexOfSheet(self, sheet):
        if sheet is None or self.data is None:
            return None

        df = self.data[sheet]
        return df.shape[1]

    def set_cells(self, sheet, row, col, data):
        """
        设置excel中单元格区域的值，该操作只修改内存数据，如果要修改excel文件，需要调用save方法。
        """
        if self.data.get(sheet) is None:
            self.data[sheet] = pd.DataFrame()

    def add_sheet(self, sheet_name):
        self.data[sheet_name] = pd.DataFrame()

    def has_sheet(self, sheet_name):
        if self.data.get(sheet_name) is None:
            return False
        else:
            return True

    def form_formula2(self, func_str: str, y, row):
        """
        * 替换{row-1}之类的参数
        """
        if not func_str.startswith("="):
            func_str = "=" + func_str

        if not isinstance(y, str):
            y = self.num_2_column_char(y)

        # 使用正则表达式找到所有{...}模式的变量
        var_name_list = set(re.findall(r'\{([^}]+)\}', func_str))

        for item in var_name_list:
            # 尝试解析+操作
            parts = item.split("+")
            if len(parts) > 1:
                try:
                    offset = int(parts[1])
                    dest = f"{y}{row + offset}"
                except ValueError:
                    dest = f"{y}{row}"
            else:
                # 尝试解析-操作
                parts = item.split("-")
                if len(parts) > 1:
                    try:
                        offset = int(parts[1])
                        dest = f"{y}{row - offset}"
                    except ValueError:
                        dest = f"{y}{row}"
                else:
                    # 没有操作符，直接使用row
                    dest = f"{y}{row}"

            # 替换所有匹配项
            func_str = func_str.replace(f"{{{item}}}", dest)

        return func_str

    def save(self):
        """
        将self.data写入本地文件
        """
        pass
