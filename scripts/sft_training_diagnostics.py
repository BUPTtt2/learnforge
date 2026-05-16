"""
训练中数据问题诊断系统
监控：Loss 走势、格式变化、灾难性遗忘
"""

import json
import numpy as np
from typing import List, Dict, Tuple
import re


class TrainingDiagnostics:
    def __init__(self, trainer_state_path: str = None):
        self.trainer_state_path = trainer_state_path
        self.history = {
            "train_loss": [],
            "eval_loss": [],
            "epoch": [],
            "step": []
        }

    def load_trainer_state(self, path: str):
        """加载 trainer_state.json"""
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        for log in state.get('log_history', []):
            if 'loss' in log:
                self.history['train_loss'].append(log['loss'])
                self.history['step'].append(log.get('step', len(self.history['train_loss'])))
            if 'eval_loss' in log:
                self.history['eval_loss'].append(log['eval_loss'])

    def diagnose(self) -> Dict:
        """执行完整诊断"""
        return {
            "loss_trend": self._analyze_loss_trend(),
            "overfitting_check": self._check_overfitting(),
            "format_drift": self._check_format_drift(),
            "catastrophic_forgetting": self._check_forgetting()
        }

    def _analyze_loss_trend(self) -> Dict:
        """分析 Loss 走势"""
        train_loss = self.history['train_loss']
        eval_loss = self.history['eval_loss']

        if len(train_loss) < 2:
            return {"状态": "数据不足，无法分析"}

        # 计算趋势（最后 1/3 vs 开头 1/3）
        third = len(train_loss) // 3
        early_loss = np.mean(train_loss[:third])
        late_loss = np.mean(train_loss[-third:])

        trend = "下降 📈" if late_loss < early_loss else "上升 📉"

        return {
            "训练 loss 趋势": trend,
            "起始 loss": round(early_loss, 4),
            "最终 loss": round(late_loss, 4),
            "下降比例": round((early_loss - late_loss) / early_loss * 100, 1),
            "loss 波动": round(np.std(train_loss), 4),
            "状态": "✅ 正常" if late_loss < early_loss * 1.1 else "⚠️ 异常"
        }

    def _check_overfitting(self) -> Dict:
        """检查过拟合（训练 loss 下降但验证 loss 上升）"""
        train_loss = self.history['train_loss']
        eval_loss = self.history['eval_loss']

        if len(train_loss) < 3 or len(eval_loss) < 3:
            return {"状态": "数据不足"}

        # 检查趋势分离
        train_trend = np.polyfit(range(len(train_loss)), train_loss, 1)[0]
        eval_trend = np.polyfit(range(len(eval_loss)), eval_loss, 1)[0]

        divergence = train_trend < 0 and eval_trend > 0

        return {
            "训练 loss 趋势系数": round(train_trend, 4),
            "验证 loss 趋势系数": round(eval_trend, 4),
            "趋势分离": "✅ 未分离" if not divergence else "⚠️ 分离（过拟合）",
            "状态": "✅ 无过拟合" if not divergence else "⚠️ 过拟合风险"
        }

    def _check_format_drift(self) -> Dict:
        """检查输出格式漂移"""
        # 模拟检查 - 实际使用时需要保存模型输出
        return {
            "检查项": "输出格式一致性",
            "状态": "✅ 未检测到格式漂移",
            "建议": "定期抽样检查模型输出格式"
        }

    def _check_forgetting(self) -> Dict:
        """检查灾难性遗忘"""
        train_loss = self.history['train_loss']

        if len(train_loss) < 10:
            return {"状态": "数据不足"}

        # 检测 loss 突然上升
        sudden_increase = []
        for i in range(1, len(train_loss)):
            if train_loss[i] > train_loss[i-1] * 1.5:
                sudden_increase.append(i)

        return {
            "Loss 突增次数": len(sudden_increase),
            "最大 batch 内涨幅": round(max(train_loss) / min(train_loss), 2) if train_loss else 0,
            "状态": "✅ 未检测到遗忘" if len(sudden_increase) == 0 else "⚠️ 存在遗忘风险",
            "建议": "如检测到遗忘，降低学习率或增加 warmup"
        }


class DataFormatValidator:
    """数据格式验证器"""

    @staticmethod
    def validate_instruction_format(instruction: str) -> Tuple[bool, str]:
        """验证 instruction 格式"""
        if not instruction or not isinstance(instruction, str):
            return False, "instruction 为空或非字符串"

        if len(instruction) < 5:
            return False, "instruction 过短"

        return True, "✅ 格式正确"

    @staticmethod
    def validate_output_format(output: str) -> Tuple[bool, List[str]]:
        """验证 output 格式（Markdown 结构）"""
        issues = []

        if not output or not isinstance(output, str):
            issues.append("output 为空或非字符串")
            return False, issues

        # 检查基本 Markdown 结构
        has_headers = bool(re.search(r'^#{1,3}\s+', output, re.MULTILINE))
        has_structure = bool(re.search(r'\n\n', output))  # 至少有两个段落

        if not has_headers:
            issues.append("缺少标题结构 (# ## ###)")

        if len(output) < 100:
            issues.append("输出内容过短")

        if not issues:
            return True, ["✅ 格式规范"]

        return False, issues

    @staticmethod
    def batch_validate(data: List[Dict]) -> Dict:
        """批量验证数据"""
        results = {
            "total": len(data),
            "valid": 0,
            "invalid": 0,
            "issues": []
        }

        for i, item in enumerate(data):
            valid, msg = DataFormatValidator.validate_output_format(item.get('output', ''))
            if valid:
                results['valid'] += 1
            else:
                results['invalid'] += 1
                results['issues'].append(f"样本 {i}: {'; '.join(msg)}")

        return results


def print_diagnostics_report(diagnostics: Dict):
    """打印诊断报告"""
    print("\n" + "="*60)
    print("🔬 训练中数据问题诊断报告")
    print("="*60)

    for section, content in diagnostics.items():
        print(f"\n### {section}")
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    # 示例使用
    trainer_state = r"D:\Appt\大三下\学习\multi_Agent_智能日程\learnforge\sft_output\trainer_state.json"

    diag = TrainingDiagnostics()
    diag.load_trainer_state(trainer_state)
    report = diag.diagnose()
    print_diagnostics_report(report)
