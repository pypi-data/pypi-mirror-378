#2.0.0
import sqlite3
import os
from datetime import datetime
import xiaokang.常用 as 常用
import inspect


class 数据库操作:
    # 2025年08月29日14时01分43秒
    def __init__(self, 数据库文件, 操作日志="", 报错日志=""):
        self.数据库文件 = 数据库文件
        self.操作日志 = 操作日志
        self.报错日志 = 报错日志
        # 创建目录，确保目录存在，exist_ok=True 表示如果目录已经存在，不会报错。
        os.makedirs(os.path.split(操作日志)[0], exist_ok=True)
        os.makedirs(os.path.split(报错日志)[0], exist_ok=True)

    # 2025年08月29日14时04分31秒
    def 写日志(self, 内容):
        if not self.操作日志:
            return
        时间戳 = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        调用者 = inspect.stack()[1].function
        日志内容 = f"{时间戳}\t{调用者}\t{内容}\n"
        with open(self.操作日志, "a", encoding="utf-8") as f:
            f.write(日志内容)

    # 2025年08月29日14时04分54秒
    def 连接(self):
        # 判断是否连接
        if hasattr(self, "conn"):
            self.写日志("数据库已连接，跳过连接")
            self.连接情况 = True
            return True,'数据库已连接'
        self.写日志("准备连接……")
        try:
            self.conn = sqlite3.connect(self.数据库文件)
            self.cursor = self.conn.cursor()
            self.写日志("数据库连接成功")
            self.连接情况 = True
            return True, "数据库连接成功"
        except Exception:
            self.写日志("数据库连接报错")
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            self.连接情况 = False
            return False, 错误

    # 2025年08月29日14时09分03秒
    def 提交(self):
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法提交")
            return False, "未发现连接对象，无法提交"
        self.写日志("准备提交……")
        try:
            self.conn.commit()
            self.写日志("事务提交成功")
            return True, "事务提交成功"
        except Exception:
            self.写日志("事务提交报错")
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误

    # 2025年08月29日14时11分37秒
    def 断开(self):
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，已跳过断开")
            return False, "未发现连接对象，已跳过断开"
        self.写日志("准备断开……")
        try:
            self.conn.commit()
            self.写日志("事务提交成功")
            self.conn.close()
            self.写日志("数据库连接断开")
            self.连接情况 = False
            del self.conn
            del self.cursor
            return True, "数据库连接断开"
        except Exception:
            self.写日志("数据库连接断开报错")
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误

    # 2025年08月29日14时13分37秒
    def 执行SQL(self, sql):
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法执行SQL")
            return False, "未发现连接对象，无法执行SQL"
        self.写日志("准备执行SQL……")
        try:
            self.写日志(f"执行SQL：{sql}")
            self.cursor.execute(sql)
            结果 = self.cursor.fetchall()
        except Exception:
            self.写日志("执行SQL报错")
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误
        return True, 结果

    # 2025年08月29日14时16分00秒
    def 创建表(self, 表名: str, 字段: list, 字段类型: dict = {}, 默认值="TEXT"):
        """
        创建表('Information', ['A','b','c'], {'A'='integer','b'='text','c'='real'}, 默认值="TEXT"):
        仅接收这三种值['integer','text','real','bolo']，其他值默认TEXT
        """
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法创建表")
            return False, "未发现连接对象，无法创建表"
        self.写日志("准备创建表……")
        try:
            sql = f'CREATE TABLE "{表名}" ('
            for 字 in 字段:
                sql += f'"{字}" {字段类型.get(字, 默认值)},'
            sql = sql.rstrip(",") + ");"
            self.写日志(f"创建表：{sql}")
            self.cursor.execute(sql)
            self.提交()
        except Exception:
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误
        return True, "创建成功"

    # 2025年08月29日16时16分37秒
    def 读取数据(self, 表: str, 查看字段: list, 判断匹配: list = [], 显示行数: list = []):
        """
        SELECT id, name, age, email FROM users WHERE age > 18 ORDER BY id ASC LIMIT 10;

        """
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法读取数据")
            return False, "未发现连接对象，无法读取数据"
        self.写日志("准备读取数据……")
        try:
            sql = f'SELECT {",".join(查看字段)} FROM {表.replace('.','"."')} WHERE {' '.join(判断匹配)} LIMIT {','.join(显示行数)};'
            self.写日志(f"读取数据：{sql}")
            self.cursor.execute(sql)
            return True, self.cursor.fetchall()
        except Exception:
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误

    # 2025年08月29日14时45分58秒
    def 新增数据(self, 表: str, 数据: dict):
        """
        INSERT INTO "main"."Information" ("系统信息", "启动项", "系统进程", "usb插拔记录", "网络适配器", "浏览器密码", "浏览器历史和cookie", "注册表", "计划任务") VALUES ('1', '1', '1', '1', '1', '1', '1', '1', '1')

        """
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法新增数据")
            return False, "未发现连接对象，无法新增数据"
        self.写日志("准备新增数据……")
        try:
            段 = []
            值 = []
            for f1, f2 in 数据.items():
                段.append(f1)
                值.append(f2)
            字段串 = '"' + '","'.join(段) + '"'
            占位符 = ",".join(["?"] * len(段))
            sql = f'INSERT INTO "{表.replace('.','"."')}" ({字段串}) VALUES ({占位符})'
            self.写日志(f"新增数据：{sql}\nvalue：{值}")
            self.cursor.execute(sql, 值)
            序号 = self.cursor.lastrowid
            return True, 序号
        except Exception:
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误

    # 2025年08月29日15时43分53秒
    def 修改数据(self, 表: str, 查数据: dict, 写数据: dict):
        """
        UPDATE "main"."Information" SET "启动项" = '2', "系统进程" = '2', "usb插拔记录" = '2' WHERE rowid = 1
        """
        # 判断是否连接
        if not hasattr(self, "conn"):
            self.写日志("未发现连接对象，无法修改数据")
            return False, "未发现连接对象，无法修改数据"
        self.写日志("准备修改数据……")
        try:
            设置语句 = "=?,".join(写数据.keys()) + "=?"
            条件语句 = "=? AND ".join(查数据.keys()) + "=?"
            sql = f'UPDATE "{表.replace('.','"."')}" SET {设置语句} WHERE {条件语句.rstrip(" AND ")}'
            参数 = list(写数据.values()) + list(查数据.values())
            self.写日志(f"修改数据：{sql}\nvalue：{参数}")
            self.cursor.execute(sql, 参数)
        except Exception:
            错误 = 常用.报错信息(保存到文件=self.报错日志)
            return False, 错误
        return True, "修改成功"
