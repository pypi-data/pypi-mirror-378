import datetime
import time
import toml
from pathlib import Path
import pandas as pd
import requests
from yangke.base import timeout
from yangke.common.config import logger
import baostock as bs
import tushare as ts
import akshare as ak


class StockData:
    def __init__(self, license=None):
        """
        获取股票数据的类，该类只负责数据获取，数据的存储在storage.py中
        """
        super().__init__()
        # 从settings.toml加载license（当入参为None时）
        if license is None:
            settings_path = Path.cwd() / "settings.toml"
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = toml.load(f)
                self.license = settings.get("license")
                self.tushare_token = settings.get(
                    "tushare_token")  # 加载tushare token
                if not self.license:
                    logger.info("settings.toml中未找到有效的license字段，正在添加...")
                    settings["license"] = "请在这里填入您的【麦蕊智数】许可证密钥"
                    # 添加tushare token字段
                    settings["tushare_token"] = "请在这里填入您的tushare token，不填写则不能使用tushare的接口"
                    with open(settings_path, "w", encoding="utf-8") as f:
                        toml.dump(settings, f)
                    logger.info(f"已在settings.toml文件中添加license字段，请进行填写。")
                    raise ValueError("请在settings.toml文件中填入有效的license字段")
            except FileNotFoundError:
                logger.info("未找到settings.toml文件，正在生成新文件...")
                default_settings = {
                    "license": "请在这里填入您的【麦蕊智数】许可证密钥"
                }
                try:
                    with open(settings_path, "w", encoding="utf-8") as f:
                        toml.dump(default_settings, f)
                    logger.info(f"已生成新的settings.toml文件，路径: {settings_path}")
                    raise ValueError("请在settings.toml文件中填入有效的license字段")
                except Exception as e:
                    logger.error(f"生成settings.toml文件时出错: {str(e)}")
                    raise
            except toml.TomlDecodeError:
                raise ValueError("settings.toml文件格式错误")
            except ValueError as e:
                logger.error(f"请填写settings.toml文件中的license字段！")
                exit(0)

        else:
            self.license = license
        self.pre_url = 'https://y.mairui.club'

    def get_market(self, symbol):
        """
        获取股票所属的板块
        """
        symbol = str(symbol)
        if symbol.startswith('60'):
            return '主板'
        elif symbol.startswith('00'):
            return "主板"
        elif symbol.startswith('30'):
            return '创业板'
        elif symbol.startswith('68'):
            return '科创板'
        elif symbol.startswith('82'):
            return '优先股'
        elif symbol.startswith('83'):
            return '普通股'
        elif symbol.startswith('87'):
            return '普通股'
        elif symbol.startswith('4'):
            return '北交所'
        return None

    def get_type_szsh(self, symbol):
        """
        判断股票所属的交易所，代码来自网络

        沪市股票包含上证主板和科创板和B股：沪市主板股票代码是60开头、科创板股票代码是688开头、B股代码900开头。
        深市股票包含主板、中小板、创业板和B股：深市主板股票代码是000开头、中小板股票代码002开头、创业板300开头、B股代码200开头
        """
        symbol = str(symbol)
        if symbol.find('60', 0, 3) == 0:
            gp_type = 'sh'
        elif symbol.find('68', 0, 4) == 0:
            gp_type = 'sh'
        elif symbol.find('90', 0, 4) == 0: # 沪市B股
            gp_type = 'sh'
        elif symbol.find('00', 0, 3) == 0:
            gp_type = 'sz'
        elif symbol.find('30', 0, 4) == 0:
            gp_type = 'sz'
        elif symbol.find('20', 0, 4) == 0:
            gp_type = 'sz'
        else:
            logger.error(f"股票{symbol}所属的交易所未识别")
        return gp_type

    def get_all_stock_basic_info(self) -> pd.DataFrame | None:
        """
        获得上海和深圳证券交易所目前上市的所有股票代码
        """
        url = f'{self.pre_url}/hslt/list/{self.license}'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 主动触发HTTP错误异常
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                df.rename(columns={"dm": "symbol", "mc": "name",
                                   "jys": "exchange"}, inplace=True)
                # 统一股票代码格式为6位数字
                df['symbol'] = df['symbol'].apply(
                    lambda x: x[:6] if '.' in x else x)
                # 将exchange列统一改为小写
                df['exchange'] = df['exchange'].str.lower()
                # 移除lambda函数，直接使用函数引用
                df['market'] = df['symbol'].apply(self.get_market)
                df = df.sort_values(by='symbol', ascending=True)
                df = df.reset_index().drop(columns='index')
                return df
            else:
                logger.debug(f"获取数据失败，检查网络或证书，尝试连接{url}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"获取股票基本信息失败: {str(e)}")
            logger.debug(f"请求URL: {url}")
            logger.debug(f"响应状态码: {getattr(response, 'status_code', '无响应')}")
            return None

    @timeout(200)
    def get_daily_akshare(self, symbol, end_date: datetime.date = None):
        try:
            # 获取股票历史数据
            df = ak.stock_zh_a_hist(
                symbol=symbol[:6],  # 取前6位股票代码
                period="daily",
                start_date="19901219",
                end_date=datetime.date.today().strftime("%Y%m%d"),
                adjust=""  # 默认不复权；qfq-前复权；hfq-后复权
            )

            if df.empty:
                logger.warning(f"akshare未找到{symbol}当日数据")
                return None

            # 重命名列以保持与其他方法一致
            df.rename(columns={
                "日期": "trade_date",
                "开盘": "open",
                "最高": "high",
                "最低": "low",
                "收盘": "close",
                "成交量": "vol",
                "成交额": "amount",
                "换手率": "换手率"
            }, inplace=True)

            # 添加缺失的指标列并填充None
            for col in ["市值", "流通市值", "市盈率", "市净率"]:
                df[col] = None

            # 格式化日期为YYYY-MM-DD
            df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")

            return df[["trade_date", "open", "high", "low", "close", "vol", "amount",
                       "换手率", "市值", "流通市值", "市盈率", "市净率"]]

        except Exception as e:
            logger.error(f"akshare获取{symbol}数据异常: {str(e)}")
            return None

    @timeout(1000)
    def get_daily(self, symbol, end_date: datetime.date = None):  # 需要拆分为单独的函数，分别设置超时时间
        """
        获取指定股票的日线数据
        """
        # "https://y.mairui.club/zs/hfsjy/000001/dn/lincense", symbol=="000048"报错
        # 根据《股票列表》得到的股票代码和分时级别获取历史交易数据，交易时间从远到近排序。目前 分时级别 支持5分钟、15分钟、30分钟、60分钟、日
        # 周月年级别（包括前后复权），对应的值分别是 5m（5分钟）、15m（15分钟）、30m（30分钟）、60m（60分钟）、dn(日线未复权)、dq（日线前复权）
        # 、dh（日线后复权）、wn(周线未复权)、wq（周线前复权）、wh（周线后复权）、mn(月线未复权)、mq（月线前复权）、mh（月线后复权）、
        # yn(年线未复权)、yq（年线前复权）、yh（年线后复权）
        url = f'{self.pre_url}/zs/hfsjy/{symbol}/dn/{self.license}'
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 404:
                logger.error(f"股票{symbol}日线数据未找到, URL: {url}")
                if symbol == "000508":
                    logger.debug("该股已退市")
                return None
            elif response.status_code == 200:
                res = pd.DataFrame(response.json())
                if res.empty:
                    logger.warning(f"股票{symbol}日线数据为空, URL: {url}")
                    return res

                res.rename(columns={"d": "trade_date",
                                    "o": "open", "h": "high",
                                    "l": "low", "c": "close",
                                    "v": "vol", "e": "amount",
                                    "hs": "换手率",
                                    "sz": "市值",  # 总市值
                                    "lt": "流通市值",
                                    "pe": "市盈率",
                                    "sjl": "市净率"
                                    },
                           inplace=True)

                if end_date is None:
                    return res
                # 如果res中的trade_date的最后一天不是end_date，则下载end_date到res中的trade_date的最后一天之间的数据
                if end_date is not None:
                    if isinstance(end_date, datetime.date):
                        end_date = end_date.strftime("%Y-%m-%d")
                    logger.debug(
                        f"end_date: {end_date}, res_last_date: {res.iloc[-1]['trade_date']}")
                    # 检查是否需要补充数据
                    if not res.empty and res.iloc[-1]["trade_date"] != end_date:
                        try:
                            start_date = datetime.datetime.strptime(
                                res.iloc[-1]["trade_date"], "%Y-%m-%d").date() + datetime.timedelta(days=1)
                            end_date_dt = datetime.datetime.strptime(
                                end_date, "%Y-%m-%d").date()
                            if start_date >= end_date_dt:
                                logger.warning(
                                    f"开始日期{start_date}不能大于等于结束日期{end_date}")
                                return res

                            append_data = self.get_daily_range(
                                symbol, start_date, end_date_dt)
                            if append_data is not None and not append_data.empty:
                                # 将字符串日期转换为日期对象进行比较
                                append_data_dates = pd.to_datetime(
                                    append_data["trade_date"])
                                res_dates = pd.to_datetime(res["trade_date"])
                                append_data = append_data[~append_data_dates.isin(
                                    res_dates)]
                                res = pd.concat(
                                    [res, append_data], ignore_index=True)
                                # 按trade_date排序
                                res["trade_date"] = pd.to_datetime(
                                    res["trade_date"])
                                res = res.sort_values("trade_date")
                                res["trade_date"] = res["trade_date"].dt.strftime(
                                    "%Y-%m-%d")
                                res = res[['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount', '换手率']]
                        except Exception as e:
                            logger.warning(f"补充数据时出错: {str(e)}")
                return res
            return None
        except requests.exceptions.SSLError:
            logger.debug("请求数据发生SSLError，使用akshare重试")
            return self.get_daily_akshare(symbol, end_date)
        except requests.exceptions.ReadTimeout:
            logger.warning("麦蕊智数获取日线数据报错，使用akshare重试")
            return self.get_daily_akshare(symbol, end_date)
        except requests.exceptions.ConnectionError:
            logger.warning(f"麦蕊智数获取日线数据报错ConnectionError，使用akshare重试")
            return self.get_daily_akshare(symbol, end_date)

    def get_daily_sh_index(self, end_date=None):
        """
        获取上证指数的日线
        """
        symbol = 'sh000001'
        return self.get_daily(symbol, end_date)

    def get_daily_sz_index(self, end_date=None):
        """
        获取深证指数的日线
        """
        symbol = ''
        return self.get_daily(symbol, end_date)

    @timeout(100)
    def get_single_day_data(self, symbol):
        """
        获取指定股票的日线数据
        http://api1.mairui.club/hsrl/ssjy/股票代码(如000001)/您的licence
        """
        url = f'{self.pre_url}/hsrl/ssjy/{symbol}/{self.license}'
        # 添加超时参数，避免程序无限期挂起
        response = requests.get(url, timeout=10)
        res = pd.DataFrame([response.json()])
        res.rename(columns={"t": "trade_date",
                            "o": "open", "h": "high",
                            "l": "low", "p": "close",
                            "v": "vol", "cje": "amount",
                            "hs": "换手率",
                            "sz": "市值",  # 总市值
                            "lt": "流通市值",
                            "pe": "市盈率",
                            "sjl": "市净率"
                            },
                   inplace=True)
        return res

    @timeout(1000)
    def _get_daily_all(self, last_day_desired: datetime.date):
        """
        https://y.mairui.club/hsrl/ssjy/all/lincense
        http://a.mairui.club/hsrl/ssjy/all/lincense  该地址已测试，失效
        https://api.mairuiapi.com/hslt/list/LICENCE-66D8-9F96-0C7F0FBCD073
        :@param last_day_desired: 最近的一个完整的工作日，如果当前时间>15:00且当天不是假期，则为当前工作日，否则为上一个工作日
        """
        url = f'http://a.mairui.club/hsrl/ssjy/all/{self.license}'
        response = None
        try:
            response = requests.get(url, timeout=40)
            response.raise_for_status()  # 主动触发HTTP错误异常，会被requests.exceptions.RequestException捕获

            json_res = response.json()
            res = pd.DataFrame(json_res)
            res.rename(columns={
                "t": "trade_date",
                "o": "open", "h": "high",
                "l": "low", "p": "close",
                "v": "vol", "cje": "amount",
                "hs": "换手率",
                "sz": "市值",
                "lt": "流通市值",
                "pe": "市盈率",
                "sjl": "市净率",
                "dm": "symbol"
            }, inplace=True)
            logger.debug(f"{res.shape=}")
            if res.empty:
                logger.warning(f"麦蕊智数获取当日股票数据为空, 尝试akshare, URL: {url}")
                raise requests.exceptions.RequestException(f"麦蕊智数获取当日股票数据为空, 尝试akshare, URL: {url}")
            return res

        except requests.exceptions.JSONDecodeError:
            logger.error(f"JSON解析失败: {response.text}")
            raise requests.exceptions.RequestException(f"JSON解析失败: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {str(e)}")
            raise requests.exceptions.RequestException(f"请求失败: {str(e)}")

    @timeout(1000)
    def _get_daily_all1(self, last_day_desired: datetime.date):
        """
        新浪财经-沪深京 A 股数据, 重复运行本函数会被新浪暂时封 IP, 建议增加时间间隔。
        单次返回沪深京 A 股上市公司的实时行情数据
        """
        logger.debug(f"akshare获取数据中...")
        res = ak.stock_zh_a_spot_em()
        res.rename(columns={
            "代码": "symbol",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "最新价": "close",
            "成交量": "vol",
            "成交额": "amount",
            "换手率": "换手率",
            "总市值": "市值",
            "流通市值": "流通市值",
            "市盈率-动态": "市盈率",
            "市净率": "市净率"
        }, inplace=True)
        # akshare获取的数据需要根据情况分为以下两类：
        # 1. 如果是交易日的9：00-15：00获取，则得到的是当前日期的实时数据，不是上一个交易日的数据。
        # 2. 如果是假日或交易日15：00以后获取，则获得的数据时最新的交易日数据，是可以直接返回的

        if datetime.datetime.now().hour >= 15 or datetime.datetime.now().hour < 8:  # 当天15点以后或8电之前
            res['trade_date'] = last_day_desired.strftime('%Y%m%d')
        else:
            if datetime.datetime.today() > last_day_desired:
                res['trade_date'] = last_day_desired.strftime('%Y%m%d')

        logger.debug(f"akshare获取到当日所有股票交易数据：{res.shape=}")
        return res[["symbol", "open", "high", "low", "close", "vol", "amount", "trade_date",
                    "换手率", "市值", "流通市值", "市盈率", "市净率"]]

    def _get_daily_all2(self, last_day_desired: datetime.date):
        """
        新浪财经-沪深京 A 股数据, 重复运行本函数会被新浪暂时封 IP, 建议增加时间间隔。
        单次返回沪深京 A 股上市公司的实时行情数据
        """
        logger.debug(f"akshare获取数据中...")
        res = ak.stock_zh_a_spot()
        res.rename(columns={
            "代码": "symbol",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "最新价": "close",
            "成交量": "vol",
            "成交额": "amount",
            "换手率": "换手率",  # 无该项
            "总市值": "市值",  # 无该项
            "流通市值": "流通市值",  # 无该项
            "市盈率-动态": "市盈率",  # 无该项
            "市净率": "市净率"  # 无该项
        }, inplace=True)
        # akshare获取的数据需要根据情况分为以下两类：
        # 1. 如果是交易日的9：00-15：00获取，则得到的是当前日期的实时数据，不是上一个交易日的数据。
        # 2. 如果是假日或交易日15：00以后获取，则获得的数据时最新的交易日数据，是可以直接返回的

        if datetime.datetime.now().hour >= 15 or datetime.datetime.now().hour < 8:  # 当天15点以后或8电之前
            res['trade_date'] = last_day_desired.strftime('%Y%m%d')
        else:
            if datetime.datetime.today() > last_day_desired:
                res['trade_date'] = last_day_desired.strftime('%Y%m%d')

        logger.debug(f"akshare获取到当日所有股票交易数据：{res.shape=}")
        return res[["symbol", "open", "high", "low", "close", "vol", "amount", "trade_date"]]

    # @timeout(100)
    def get_daily_all(self, last_day_desired: datetime.date):
        """
        获取所有股票当天的交易数据
        """
        try:
            res = self._get_daily_all(last_day_desired=last_day_desired)
            # res1 = self._get_daily_all1(last_day_desired=last_day_desired)
            # res2 = self._get_daily_all2(last_day_desired=last_day_desired)
        except requests.exceptions.RequestException as e:
            try:
                res = self._get_daily_all1(last_day_desired=last_day_desired)
            except requests.exceptions.RequestException as e:
                res = self._get_daily_all2(last_day_desired=last_day_desired)
        return res

    @timeout(100)
    def get_daily_range(self, symbol, start_date: datetime.date, end_date: datetime.date, method='default'):
        """
        下载指定股票的指定日期范围的数据，不复权
        https://y.mairui.club/hsstock/history/000001.SZ/d/n/{license}?st=20250501&et=20250516
        分时级别支持1分钟、5分钟、15分钟、30分钟、60分钟、日线、周线、月线、年线，对应的请求参数分别为1、5、15、30、60、d、w、m、y
        除权方式有不复权、前复权、后复权、等比前复权、等比后复权，对应的参数分别为n、f、b、fr、br

        @param symbol: 股票代码
        @param start_date: 开始日期(格式:YYYYMMDD)
        @param end_date: 结束日期(格式:YYYYMMDD)
        @return: 包含历史数据的DataFrame，列名与get_daily方法一致
        """
        if end_date < start_date:
            logger.error(f"end_date必须在start_date之后，当前{start_date=}，{end_date=}")
        if method == 'default':
            if "." in symbol:
                symbol = symbol.upper()
            else:
                symbol = f"{symbol}.{self.get_type_szsh(symbol).upper()}"

            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")
            url = f'{self.pre_url}/hsstock/history/{symbol}/d/n/{self.license}?st={start_str}&et={end_str}'
            try:
                response = requests.get(url, timeout=60)
                if response.status_code == 404:
                    logger.error(
                        f"股票{symbol}在{start_date}至{end_date}范围内的数据未找到, URL: {url}")
                    return self.get_daily_range(symbol, start_date, end_date, method='baostock')
                elif response.status_code == 200:
                    res = pd.DataFrame(response.json())
                    res.rename(columns={
                        "t": "trade_date",
                        "o": "open", "h": "high",
                        "l": "low", "c": "close",
                        "v": "vol", "a": "amount",
                    }, inplace=True)
                    # 将trade_date转换为YYYY-MM-DD格式
                    res["trade_date"] = pd.to_datetime(
                        res["trade_date"]).dt.strftime("%Y-%m-%d")
                    res = res[["trade_date", "open", "high",
                               "low", "close", "vol", "amount"]]
                    return res
                return self.get_daily_range(symbol, start_date, end_date, method='baostock')
            except requests.exceptions.RequestException as e:
                logger.error(f"获取股票{symbol}历史数据失败，将从baostock重试: {str(e)}")
                logger.debug(f"请求URL: {url}")
                return self.get_daily_range(symbol, start_date, end_date, method='baostock')
        elif method == 'baostock':
            logger.debug(f"baostock获取数据中...")
            if "." in symbol and symbol.index('.') == 6:
                _1, _2 = symbol.split('.')
                symbol = f"{_2}.{_1}".lower()
            elif "." in symbol and symbol.index('.') == 2:
                symbol = symbol.lower()
            else:
                symbol = f"{self.get_type_szsh(symbol)}.{symbol}".lower()

            try:
                # 登录系统
                lg = bs.login()
                if lg.error_code != '0':
                    logger.error(f"baostock登录失败: {lg.error_msg}")
                    return self.get_daily_range(symbol, start_date, end_date, method='tushare')

                # 获取历史K线数据
                rs = bs.query_history_k_data_plus(
                    symbol,
                    "date,code,open,high,low,close,volume,amount,adjustflag",
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    frequency="d",  # d表示日线
                    adjustflag="3"  # 3表示不复权
                )

                if rs.error_code != '0':
                    logger.error(f"获取股票{symbol}历史数据失败: {rs.error_msg}")
                    bs.logout()
                    return self.get_daily_range(symbol, start_date, end_date, method='tushare')

                # 处理结果集
                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())

                result = pd.DataFrame(data_list, columns=rs.fields)
                bs.logout()

                # 重命名列以保持与其他方法一致
                result.rename(columns={
                    "date": "trade_date",
                    "volume": "vol",
                    "amount": "amount"
                }, inplace=True)
                # 将成家量单位从“股”转换为“手”
                result['vol'] = result['vol'].astype(float) / 100

                return result[["trade_date", "open", "high", "low", "close", "vol", "amount"]]
            except Exception as e:
                logger.error(f"baostock获取数据异常: {str(e)}")
                try:
                    bs.logout()
                except:
                    pass
                return self.get_daily_range(symbol, start_date, end_date, method='tushare')
        elif method == 'tushare':
            try:
                # 初始化pro接口
                pro = ts.pro_api(self.tushare_token)  # 使用类中已有的license

                # 构建股票代码
                if "." in symbol and symbol.index('.') == 6:
                    symbol = symbol.upper()
                elif "." in symbol and symbol.index('.') == 2:
                    _1, _2 = symbol.split('.')
                    symbol = f"{_2}.{_1}".upper()
                else:
                    symbol = f"{symbol}.{self.get_type_szsh(symbol).upper()}"

                # 获取数据
                df = pro.daily(
                    ts_code=symbol,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                    fields=[
                        "trade_date",
                        "open",
                        "high",
                        "low",
                        "close",
                        "vol",
                        "amount"
                    ]
                )

                if df.empty:
                    logger.warning(
                        f"tushare未找到{symbol}在{start_date}至{end_date}范围内的数据")
                    return None

                # 重命名列以保持与其他方法一致
                df.rename(columns={
                    "vol": "vol",
                    "amount": "amount"
                }, inplace=True)

                # 确保trade_date列是日期类型
                df["trade_date"] = pd.to_datetime(df["trade_date"])
                df.sort_values("trade_date", inplace=True)
                # 格式化日期为YYYY-MM-DD
                df["trade_date"] = pd.to_datetime(
                    df["trade_date"]).dt.strftime("%Y-%m-%d")

                return df[["trade_date", "open", "high", "low", "close", "vol", "amount"]]

            except Exception as e:
                logger.error(f"tushare获取数据异常: {str(e)}")
                return None
        return None


if __name__ == '__main__':
    sd = StockData()
    sd.get_all_stock_basic_info()
