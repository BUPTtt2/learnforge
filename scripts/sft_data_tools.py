import json
import os
import argparse
from typing import List, Dict, Any
from datetime import datetime


class DataConverter:
    """数据格式转换器 - 转换为各种训练框架格式"""

    @staticmethod
    def to_huggingface_chat(data: Dict) -> Dict:
        """转换为 HuggingFace chat 格式"""
        return {
            "messages": data["messages"],
            "metadata": data.get("metadata", {})
        }

    @staticmethod
    def to_llama_factory(data: Dict) -> Dict:
        """转换为 LLaMA Factory 格式"""
        messages = data["messages"]

        conversation = []
        for msg in messages:
            role = msg["role"]
            if role == "system":
                conversation.append({"role": "system", "content": msg["content"]})
            elif role == "user":
                conversation.append({"role": "user", "content": msg["content"]})
            elif role == "assistant":
                conversation.append({"role": "assistant", "content": msg["content"]})

        return {
            "conversation": conversation
        }

    @staticmethod
    def to_pretrain(data: Dict) -> str:
        """转换为预训练文本格式"""
        messages = data["messages"]

        texts = []
        for msg in messages:
            if msg["role"] == "user":
                texts.append(f"<|user|>\n{msg['content']}")
            elif msg["role"] == "assistant":
                texts.append(f"<|assistant|>\n{msg['content']}")

        return "\n\n".join(texts)

    @staticmethod
    def convert_file(input_path: str, output_path: str, format: str = "huggingface"):
        """转换文件格式"""

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        converter_map = {
            "huggingface": DataConverter.to_huggingface_chat,
            "llama_factory": DataConverter.to_llama_factory,
            "pretrain": DataConverter.to_pretrain
        }

        converter = converter_map.get(format, DataConverter.to_huggingface_chat)

        if format == "pretrain":
            results = [converter(item) for item in data]
            output_text = "\n".join(results)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
        else:
            results = [converter(item) for item in data]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"[Convert] 转换完成: {input_path} -> {output_path} ({format})")


class DatasetSplitter:
    """数据集划分工具"""

    @staticmethod
    def split(input_path: str, output_dir: str,
              train_ratio: float = 0.8,
              val_ratio: float = 0.1,
              test_ratio: float = 0.1,
              seed: int = 42):
        """划分训练集/验证集/测试集"""

        import random
        random.seed(seed)

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        random.shuffle(data)

        total = len(data)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        train_data = data[:train_end]
        val_data = data[train_end:val_end]
        test_data = data[val_end:]

        os.makedirs(output_dir, exist_ok=True)

        splits = {
            "train": train_data,
            "val": val_data,
            "test": test_data
        }

        for split_name, split_data in splits.items():
            output_path = os.path.join(output_dir, f"{split_name}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(split_data, f, ensure_ascii=False, indent=2)

            print(f"[Split] {split_name}: {len(split_data)} 条 -> {output_path}")

        stats = {
            "total": total,
            "train": len(train_data),
            "val": len(val_data),
            "test": len(test_data),
            "ratios": {
                "train": len(train_data) / total,
                "val": len(val_data) / total,
                "test": len(test_data) / total
            }
        }

        stats_path = os.path.join(output_dir, "split_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print(f"\n[Split] 划分完成!")
        print(f"  训练集: {stats['train']} ({stats['ratios']['train']:.1%})")
        print(f"  验证集: {stats['val']} ({stats['ratios']['val']:.1%})")
        print(f"  测试集: {stats['test']} ({stats['ratios']['test']:.1%})")


class DatasetMerger:
    """数据集合并工具"""

    @staticmethod
    def merge(input_paths: List[str], output_path: str):
        """合并多个数据集"""

        merged = []

        for path in input_paths:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                merged.extend(data)
                print(f"[Merge] {path}: +{len(data)} 条")
            else:
                merged.append(data)
                print(f"[Merge] {path}: +1 条")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

        print(f"\n[Merge] 合并完成: {len(merged)} 条 -> {output_path}")


class DataAugmenter:
    """数据增强工具"""

    @staticmethod
    def add_variants(data: Dict, num_variants: int = 2) -> List[Dict]:
        """为单条数据生成多个变体"""

        base_message = data["messages"][1]["content"]
        metadata = data.get("metadata", {})

        variants = []

        question_templates = [
            f"请讲解一下{base_message.replace('请用', '').replace('讲解', '')}",
            f"能否详细介绍{base_message.split('主题：')[1].split('\\n')[0] if '主题：' in base_message else ''}？",
            base_message,
            f"我需要学习{base_message.split('学习目标：')[1] if '学习目标：' in base_message else ''}，请讲解{base_message.split('子主题：')[1].split('\\n')[0] if '子主题：' in base_message else ''}",
        ]

        import random
        random.seed(42)

        selected_templates = random.sample(question_templates, min(num_variants, len(question_templates)))

        for i, template in enumerate(selected_templates):
            variant_data = {
                "messages": [
                    data["messages"][0].copy(),
                    {"role": "user", "content": template},
                    data["messages"][2].copy()
                ],
                "metadata": {
                    **metadata,
                    "variant_id": i
                }
            }
            variants.append(variant_data)

        return variants


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SFT 数据处理工具")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    convert_parser = subparsers.add_parser("convert", help="转换数据格式")
    convert_parser.add_argument("--input", "-i", required=True, help="输入文件")
    convert_parser.add_argument("--output", "-o", required=True, help="输出文件")
    convert_parser.add_argument("--format", "-f", default="huggingface",
                                choices=["huggingface", "llama_factory", "pretrain"],
                                help="输出格式")

    split_parser = subparsers.add_parser("split", help="划分数据集")
    split_parser.add_argument("--input", "-i", required=True, help="输入文件")
    split_parser.add_argument("--output", "-o", required=True, help="输出目录")
    split_parser.add_argument("--train", "-t", type=float, default=0.8, help="训练集比例")
    split_parser.add_argument("--val", "-v", type=float, default=0.1, help="验证集比例")
    split_parser.add_argument("--test", "-e", type=float, default=0.1, help="测试集比例")
    split_parser.add_argument("--seed", "-s", type=int, default=42, help="随机种子")

    merge_parser = subparsers.add_parser("merge", help="合并数据集")
    merge_parser.add_argument("--inputs", "-i", nargs="+", required=True, help="输入文件列表")
    merge_parser.add_argument("--output", "-o", required=True, help="输出文件")

    args = parser.parse_args()

    if args.command == "convert":
        DataConverter.convert_file(args.input, args.output, args.format)

    elif args.command == "split":
        DatasetSplitter.split(args.input, args.output, args.train, args.val, args.test, args.seed)

    elif args.command == "merge":
        DatasetMerger.merge(args.inputs, args.output)

    else:
        parser.print_help()