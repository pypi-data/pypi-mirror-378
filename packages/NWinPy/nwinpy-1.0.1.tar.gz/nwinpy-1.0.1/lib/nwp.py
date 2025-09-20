# 导入必须库
import os

# 函数
def copy(str: str):
    os.system(f"echo {str}| clip") # 复制内容


copy("www")