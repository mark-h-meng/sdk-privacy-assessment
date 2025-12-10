import os
import json

# 输入和输出目录
input_dir = "."          # 当前文件夹，如需指定别的目录可改成绝对路径或相对路径
output_dir = "output"    # 输出目录名称

# 如果输出目录不存在，则创建
os.makedirs(output_dir, exist_ok=True)

def update_trace_depth(obj, new_value=30):
    """
    递归遍历 JSON 对象，把所有键为 'traceDepth' 的值改为 new_value。
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "traceDepth":
                obj[key] = new_value
            else:
                update_trace_depth(value, new_value)
    elif isinstance(obj, list):
        for item in obj:
            update_trace_depth(item, new_value)

# 遍历输入目录下的所有 .json 文件
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".json"):
        continue  # 跳过非 json 文件

    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取 {input_path} 失败，跳过。错误：{e}")
        continue

    # 修改 traceDepth
    update_trace_depth(data, new_value=30)

    # 保存到 output 目录下
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已处理并保存：{output_path}")
    except Exception as e:
        print(f"写入 {output_path} 失败。错误：{e}")