import json
import os
import sys

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 修改工作目录
os.chdir(script_dir)

# 将目录添加到系统路径（可选）
sys.path.insert(0, script_dir)

# 定义JSON文件路径
file_path = './tcl_device_KFR-72F_YP1Ca+F1.json'

try:
    # 打开并读取JSON文件
    with open(file_path, 'r', encoding='utf-8') as file:
        # 解析JSON数据
        rn_panel_config = json.load(file)

    data = rn_panel_config["data"]["pages"]["home"]
    attr_name = dict()

    for item in data:
        attr_name[item["identifier"]]=item["title"]

    # 打印整个数据结构
    print("成功读取JSON数据：")
    print(json.dumps(attr_name, indent=4, ensure_ascii=False))  # 美化输出

    # 示例：访问数据（假设JSON是对象类型）
    # if isinstance(data, dict):
        # print("\n访问特定数据：")
        # 根据实际结构访问数据，例如：
        # if 'name' in data:
        #     print(f"名称: {data['name']}")
        # if 'age' in data:
        #     print(f"年龄: {data['age']}")

except FileNotFoundError:
    print(f"错误：文件 {file_path} 不存在")
except json.JSONDecodeError:
    print("错误：文件内容不是有效的JSON格式")
except Exception as e:
    print(f"发生未知错误: {str(e)}")