"""
SFT 数据生成和训练完整流程
========================

使用方法:
  # 1. 生成数据
  python run_sft.py generate

  # 2. 检查质量
  python run_sft.py check

  # 3. 划分数据集
  python run_sft.py split

  # 4. 一键完成全部流程
  python run_sft.py all

"""

import os
import sys
import json
import subprocess
from datetime import datetime


SFT_DATA_DIR = "./sft_data"
RAW_DATA_PATH = f"{SFT_DATA_DIR}/raw_generated.json"
TRAIN_DATA_PATH = f"{SFT_DATA_DIR}/train.json"
VAL_DATA_PATH = f"{SFT_DATA_DIR}/val.json"
TEST_DATA_PATH = f"{SFT_DATA_DIR}/test.json"


def run_command(cmd: list, description: str):
    """执行命令"""
    print(f"\n{'='*60}")
    print(f"[{description}]")
    print(f"命令: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, shell=True)

    if result.returncode != 0:
        print(f"[Error] {description} 失败!")
        return False

    print(f"[Success] {description} 完成!")
    return True


def step_generate():
    """步骤1: 生成 SFT 数据"""
    print("\n" + "="*60)
    print("步骤 1: 生成 SFT 数据")
    print("="*60)

    cmd = [
        "python", "scripts/generate_sft_data.py",
        "-o", RAW_DATA_PATH,
        "-c", "30",
        "-d", "1.0"
    ]

    if not run_command(cmd, "生成 SFT 数据"):
        return False

    return True


def step_check():
    """步骤2: 检查数据质量"""
    print("\n" + "="*60)
    print("步骤 2: 检查数据质量")
    print("="*60)

    if not os.path.exists(RAW_DATA_PATH):
        print(f"[Error] 数据文件不存在: {RAW_DATA_PATH}")
        return False

    cmd = [
        "python", "scripts/generate_sft_data.py",
        "--check",
        "-o", RAW_DATA_PATH
    ]

    result = subprocess.run(cmd, shell=True)

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"\n当前数据集: {len(data)} 条数据")

    valid = input("数据质量是否可接受? (y/n): ").strip().lower()
    return valid == 'y'


def step_split():
    """步骤3: 划分数据集"""
    print("\n" + "="*60)
    print("步骤 3: 划分数据集")
    print("="*60)

    if not os.path.exists(RAW_DATA_PATH):
        print(f"[Error] 数据文件不存在: {RAW_DATA_PATH}")
        return False

    cmd = [
        "python", "scripts/sft_data_tools.py",
        "split",
        "-i", RAW_DATA_PATH,
        "-o", SFT_DATA_DIR,
        "-t", "0.8",
        "-v", "0.1",
        "-e", "0.1"
    ]

    return run_command(cmd, "划分数据集")


def step_export():
    """步骤4: 导出 Ollama 格式"""
    print("\n" + "="*60)
    print("步骤 4: 导出 Ollama 格式")
    print("="*60)

    cmd = [
        "python", "scripts/sft_train.py",
        "export",
        "-d", TRAIN_DATA_PATH,
        "-o", f"{SFT_DATA_DIR}/ollama_format.json"
    ]

    return run_command(cmd, "导出 Ollama 格式")


def step_train():
    """步骤5: 训练模型 (可选)"""
    print("\n" + "="*60)
    print("步骤 5: 训练模型")
    print("="*60)

    print("注意: 本地训练需要 GPU 和足够显存")
    print(f"训练数据: {TRAIN_DATA_PATH}")

    confirm = input("是否继续训练? (y/n): ").strip().lower()

    if confirm != 'y':
        print("跳过训练步骤")
        return True

    cmd = [
        "python", "scripts/sft_train.py",
        "train",
        "-d", TRAIN_DATA_PATH,
        "-o", "./sft_output",
        "-e", "3"
    ]

    return run_command(cmd, "训练模型")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用命令:")
        print("  generate - 仅生成数据")
        print("  check    - 检查数据质量")
        print("  split    - 划分数据集")
        print("  export   - 导出 Ollama 格式")
        print("  train    - 训练模型")
        print("  all      - 执行全部流程")
        sys.exit(1)

    command = sys.argv[1].lower()

    os.makedirs(SFT_DATA_DIR, exist_ok=True)

    if command == "generate":
        step_generate()

    elif command == "check":
        if not os.path.exists(RAW_DATA_PATH):
            print(f"[Error] 请先生成数据: python run_sft.py generate")
            sys.exit(1)
        step_check()

    elif command == "split":
        if not os.path.exists(RAW_DATA_PATH):
            print(f"[Error] 请先生成数据: python run_sft.py generate")
            sys.exit(1)
        step_split()

    elif command == "export":
        if not os.path.exists(TRAIN_DATA_PATH):
            print(f"[Error] 请先划分数据: python run_sft.py split")
            sys.exit(1)
        step_export()

    elif command == "train":
        if not os.path.exists(TRAIN_DATA_PATH):
            print(f"[Error] 请先划分数据: python run_sft.py split")
            sys.exit(1)
        step_train()

    elif command == "all":
        print("\n" + "="*60)
        print("SFT 完整流程")
        print("="*60)

        if not step_generate():
            sys.exit(1)

        if not step_check():
            print("数据质量不达标，请调整后重试")
            sys.exit(1)

        if not step_split():
            sys.exit(1)

        if not step_export():
            sys.exit(1)

        print("\n" + "="*60)
        print("全部流程完成!")
        print("="*60)
        print(f"\n生成的数据:")
        print(f"  原始数据: {RAW_DATA_PATH}")
        print(f"  训练集:   {TRAIN_DATA_PATH}")
        print(f"  验证集:   {VAL_DATA_PATH}")
        print(f"  测试集:   {TEST_DATA_PATH}")
        print(f"  Ollama:   {SFT_DATA_DIR}/ollama_format.json")

    else:
        print(f"[Error] 未知命令: {command}")
        print("使用 'python run_sft.py' 查看帮助")


if __name__ == "__main__":
    main()