"""评估记录查看工具"""

import json
import os
from typing import Dict, List

script_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(os.path.dirname(script_dir), "evaluation_logs")
log_file = os.path.join(log_dir, "evaluation_history.json")

def load_history() -> List[Dict]:
    """加载历史记录"""
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def format_bytes(size_bytes: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def main():
    history = load_history()
    
    if not history:
        print("❌ 暂无评估记录")
        return
    
    # 显示基本信息
    file_size = os.path.getsize(log_file)
    print("\n" + "="*70)
    print("📋 SFT 数据评估记录查看器")
    print("="*70)
    print(f"\n📍 记录文件: {log_file}")
    print(f"📊 记录数量: {len(history)} 次评估")
    print(f"📁 文件大小: {format_bytes(file_size)}")
    
    # 显示历史列表
    print("\n" + "="*70)
    print("📜 评估历史列表")
    print("="*70)
    print(f"\n{'索引':<6} {'时间':<26} {'数据集':<25} {'数据量':<8} {'质量分':<10}")
    print("-"*70)
    
    for idx, record in enumerate(history):
        time_str = record['timestamp'][:19].replace('T', ' ')
        data_name = record['data_name'][:25]
        data_count = record['report'].get('数据概览', {}).get('总数据量', 'N/A')
        quality_score = record['report'].get('内容质量', {}).get('平均质量分', 'N/A')
        
        print(f"{idx+1:<6} {time_str:<26} {data_name:<25} {str(data_count):<8} {str(quality_score):<10}")
    
    # 查看详细信息
    print("\n" + "="*70)
    print("🔍 操作选项")
    print("="*70)
    print("\n1. 查看某次评估详情")
    print("2. 比较两次评估")
    print("3. 查看全部记录")
    print("4. 导出为CSV")
    print("0. 退出")
    
    while True:
        choice = input("\n请输入选项 (0-4): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
            
        elif choice == '1':
            idx_input = input("请输入评估索引 (1-{}): ".format(len(history))).strip()
            try:
                idx = int(idx_input) - 1
                if 0 <= idx < len(history):
                    record = history[idx]
                    print("\n" + "="*70)
                    print(f"📋 评估 #{idx+1} 详情")
                    print("="*70)
                    print(f"\n📅 时间: {record['timestamp']}")
                    print(f"📁 数据集: {record['data_name']}")
                    
                    print("\n📊 报告内容:")
                    for section, content in record['report'].items():
                        print(f"\n--- {section} ---")
                        if isinstance(content, dict):
                            for key, value in content.items():
                                print(f"  {key}: {value}")
                        else:
                            print(f"  {content}")
                else:
                    print("❌ 索引无效")
            except ValueError:
                print("❌ 请输入数字")
                
        elif choice == '2':
            idx1 = input("请输入第一次评估索引 (1-{}): ".format(len(history))).strip()
            idx2 = input("请输入第二次评估索引 (1-{}): ".format(len(history))).strip()
            
            try:
                idx1 = int(idx1) - 1
                idx2 = int(idx2) - 1
                
                if 0 <= idx1 < len(history) and 0 <= idx2 < len(history):
                    r1, r2 = history[idx1], history[idx2]
                    
                    print("\n" + "="*70)
                    print(f"📈 比较评估 #{idx1+1} vs #{idx2+1}")
                    print("="*70)
                    
                    print(f"\n评估 1: {r1['data_name']} ({r1['timestamp'][:19]})")
                    print(f"评估 2: {r2['data_name']} ({r2['timestamp'][:19]})")
                    
                    print("\n📊 关键指标对比:")
                    metrics = [
                        ("数据概览", "总数据量"),
                        ("内容质量", "平均质量分"),
                        ("内容质量", "高分样本数 (>60)"),
                        ("多样性分析", "主题覆盖数"),
                    ]
                    
                    for section, metric in metrics:
                        v1 = r1['report'].get(section, {}).get(metric, 'N/A')
                        v2 = r2['report'].get(section, {}).get(metric, 'N/A')
                        
                        if v1 != 'N/A' and v2 != 'N/A':
                            diff = v2 - v1
                            pct = (diff / v1 * 100) if v1 != 0 else 0
                            print(f"  {metric}: {v1} → {v2} ({diff:+.1f}, {pct:+.1f}%)")
                        else:
                            print(f"  {metric}: {v1} → {v2}")
                else:
                    print("❌ 索引无效")
            except ValueError:
                print("❌ 请输入数字")
                
        elif choice == '3':
            print("\n" + "="*70)
            print("📜 全部记录详情")
            print("="*70)
            
            for idx, record in enumerate(history):
                print(f"\n--- 评估 #{idx+1} ---")
                print(f"时间: {record['timestamp']}")
                print(f"数据集: {record['data_name']}")
                
                overview = record['report'].get('数据概览', {})
                quality = record['report'].get('内容质量', {})
                diversity = record['report'].get('多样性分析', {})
                
                print(f"数据量: {overview.get('总数据量', 'N/A')}")
                print(f"质量分: {quality.get('平均质量分', 'N/A')}")
                print(f"主题数: {diversity.get('主题覆盖数', 'N/A')}")
                
        elif choice == '4':
            import csv
            
            csv_path = os.path.join(log_dir, "evaluation_summary.csv")
            
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                
                # 表头
                writer.writerow(['索引', '时间', '数据集', '数据量', '平均质量分', '高分样本数', '主题覆盖数'])
                
                for idx, record in enumerate(history):
                    overview = record['report'].get('数据概览', {})
                    quality = record['report'].get('内容质量', {})
                    diversity = record['report'].get('多样性分析', {})
                    
                    writer.writerow([
                        idx + 1,
                        record['timestamp'],
                        record['data_name'],
                        overview.get('总数据量', ''),
                        quality.get('平均质量分', ''),
                        quality.get('高分样本数 (>60)', ''),
                        diversity.get('主题覆盖数', '')
                    ])
                    
            print(f"\n✅ CSV已导出: {csv_path}")
            
        else:
            print("❌ 无效选项")

if __name__ == "__main__":
    main()
