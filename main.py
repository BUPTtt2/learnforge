import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.commander import commander
from utils.tools import format_learning_content

def main():
    print("=" * 50)
    print("LearnForge 智能学习助手")
    print("=" * 50)
    print()
    
    try:
        commander.load_state()
    except Exception as e:
        print(f"[警告] 加载状态失败：{e}")
    
    while True:
        print("\n请选择操作：")
        print("1. 开始学习")
        print("2. 查看学习进度")
        print("3. 查看知识图谱")
        print("4. 保存并退出")
        
        try:
            choice = input("\n请输入选项（1-4）：").strip()
        except EOFError:
            print("\n输入结束，程序退出。")
            break
        
        if choice == "1":
            knowledge_point = input("\n请输入想学习的内容：").strip()
            if not knowledge_point:
                print("内容不能为空！")
                continue
            
            mode = input("选择学习模式（1-简单了解，2-弄清楚）：").strip()
            learning_mode = "deep" if mode == "2" else "simple"
            
            learning_goal = input("请输入学习目标（如：面试、项目开发、考试等，按回车跳过）：").strip()
            
            print("\n正在分析知识点复杂度...")
            result = commander.process_learning_request(knowledge_point, learning_mode, learning_goal)
            
            print(f"\n类型：{'复杂知识点' if result['type'] == 'complex' else '简单知识点'}")
            print(f"学习模式：{'深度理解' if learning_mode == 'deep' else '简单了解'}")
            
            for i, chapter_result in enumerate(result['results'], 1):
                print(f"\n{'='*50}")
                print(f"第{i}章：{chapter_result['chapter']}")
                print("="*50)
                print(format_learning_content(chapter_result['content']))
                
                user_answer = input("\n请输入答案（A/B/C/D）或按回车跳过：").strip()
                if user_answer:
                    answer_result = commander.check_answer(
                        chapter_result['chapter'],
                        user_answer,
                        chapter_result['content']['exercise']['answer']
                    )
                    print(f"\n{answer_result['feedback']}")
                    print(f"掌握度：{answer_result['new_mastery_level']:.1%}")
            
            print("\n学习完成！")
        
        elif choice == "2":
            progress = commander.get_learning_progress()
            print("\n学习进度：")
            print(f"总知识点：{progress['total']}")
            print(f"已学习：{progress['learned']}")
            print(f"平均掌握度：{progress['average_mastery']:.1%}")
            print(f"完成进度：{progress['progress_rate']:.1%}")
        
        elif choice == "3":
            tree = commander.get_category_tree()
            print("\n知识图谱：")
            for category, data in tree.items():
                child_count = len(data.get("children", {}))
                print(f"  {category}：{child_count}个知识点")
        
        elif choice == "4":
            commander.save_state()
            print("\n已保存知识图谱，下次再见！")
            break
        
        else:
            print("\n无效选项，请重新选择！")


if __name__ == "__main__":
    main()
