import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class KnowledgeGraph:
    def __init__(self, persist_dir: str = "./memory_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        self.categories = [
            "数学", "计算机科学", "物理学", "化学", "生物学",
            "历史学", "文学", "经济学", "心理学", "哲学",
            "人工智能", "机器学习", "深度学习", "数据科学"
        ]
        
        self.knowledge_graph = {}
        self.relations = {}
        self.node_index = {}
        
        self._init_base_categories()
        self.load()
    
    def _init_base_categories(self):
        for category in self.categories:
            if category not in self.knowledge_graph:
                node_id = self._get_node_id(category)
                self.knowledge_graph[category] = {
                    "node_id": node_id,
                    "name": category,
                    "type": "category",
                    "children": {},
                    "properties": {
                        "status": "未学",
                        "mastery_level": 0.0,
                        "learning_mode": None,
                        "history": [],
                        "created_at": datetime.now().isoformat()
                    }
                }
                self.node_index[node_id] = {"category": category, "is_child": False}
    
    def _get_node_id(self, name: str) -> str:
        return name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    def _find_category(self, name: str) -> Optional[str]:
        for category in self.categories:
            if name.startswith(category) or category in name:
                return category
        return None
    
    def add_node(self, name: str, parent: str = None, properties: Dict = None) -> bool:
        if parent is None:
            parent = self._find_category(name)
        
        if parent is None:
            parent = "计算机科学"
        
        if parent not in self.knowledge_graph:
            self.knowledge_graph[parent] = {
                "node_id": self._get_node_id(parent),
                "name": parent,
                "type": "category",
                "children": {},
                "properties": {
                    "status": "未学",
                    "mastery_level": 0.0,
                    "learning_mode": None,
                    "history": [],
                    "created_at": datetime.now().isoformat()
                }
            }
        
        node_id = self._get_node_id(name)
        
        if "children" not in self.knowledge_graph[parent]:
            self.knowledge_graph[parent]["children"] = {}
        
        if node_id in self.knowledge_graph[parent]["children"]:
            self.update_node(name, properties or {})
            return True
        
        default_properties = {
            "status": "未学",
            "mastery_level": 0.0,
            "learning_mode": None,
            "history": [],
            "created_at": datetime.now().isoformat()
        }
        
        if properties:
            default_properties.update(properties)
            if "history" in properties:
                default_properties["history"] = properties["history"]
        
        self.knowledge_graph[parent]["children"][node_id] = {
            "node_id": node_id,
            "name": name,
            "type": "knowledge",
            "parent": parent,
            "properties": default_properties
        }
        
        self.node_index[node_id] = {"category": parent, "is_child": True}
        
        if "last_learned" in default_properties:
            default_properties["history"].append({
                "action": "learn",
                "timestamp": default_properties["last_learned"],
                "mode": default_properties.get("learning_mode")
            })
        
        return True
    
    def add_relation(self, source: str, target: str, relation_type: str = "related"):
        source_id = self._get_node_id(source)
        target_id = self._get_node_id(target)
        
        if source_id not in self.relations:
            self.relations[source_id] = []
        
        existing = [r for r in self.relations[source_id] 
                    if r["target"] == target_id and r["type"] == relation_type]
        
        if not existing:
            self.relations[source_id].append({
                "target": target_id,
                "type": relation_type,
                "created_at": datetime.now().isoformat()
            })
    
    def get_node(self, name: str) -> Optional[Dict]:
        node_id = self._get_node_id(name)
        
        index_entry = self.node_index.get(node_id)
        if index_entry:
            if index_entry["is_child"]:
                parent = index_entry["category"]
                if parent in self.knowledge_graph:
                    children = self.knowledge_graph[parent].get("children", {})
                    return children.get(node_id)
            else:
                return self.knowledge_graph.get(node_id)
        
        for category_data in self.knowledge_graph.values():
            if "children" in category_data:
                for child_id, child_data in category_data["children"].items():
                    if child_data.get("name") == name:
                        return child_data
        
        return None
    
    def update_node(self, name: str, properties: Dict) -> bool:
        node = self.get_node(name)
        if node:
            node["properties"].update(properties)
            if "last_learned" in properties:
                node["properties"].setdefault("history", []).append({
                    "action": "update",
                    "timestamp": properties["last_learned"],
                    "changes": list(properties.keys())
                })
            return True
        return False
    
    def search_nodes(self, query: str, limit: int = 5) -> List[Dict]:
        results = []
        query_lower = query.lower()
        
        for category, category_data in self.knowledge_graph.items():
            if query_lower in category.lower():
                results.append({
                    "name": category,
                    "type": "category",
                    "category": category,
                    "properties": category_data.get("properties", {})
                })
            
            if "children" in category_data:
                for node_id, node_data in category_data["children"].items():
                    node_name = node_data.get("name", "")
                    if query_lower in node_name.lower():
                        results.append({
                            "name": node_name,
                            "type": "knowledge",
                            "category": category,
                            "properties": node_data.get("properties", {})
                        })
        
        return sorted(results, key=lambda x: x["name"])[:limit]
    
    def get_related_nodes(self, name: str, relation_type: str = None) -> List[Dict]:
        node_id = self._get_node_id(name)
        related_ids = []
        
        if node_id in self.relations:
            for relation in self.relations[node_id]:
                if relation_type is None or relation["type"] == relation_type:
                    related_ids.append(relation["target"])
        
        results = []
        for related_id in related_ids:
            node = self._get_node_by_id(related_id)
            if node:
                results.append(node)
        
        return results
    
    def _get_node_by_id(self, node_id: str) -> Optional[Dict]:
        index_entry = self.node_index.get(node_id)
        if index_entry:
            if index_entry["is_child"]:
                parent = index_entry["category"]
                if parent in self.knowledge_graph:
                    children = self.knowledge_graph[parent].get("children", {})
                    return children.get(node_id)
            else:
                return self.knowledge_graph.get(node_id)
        return None
    
    def get_category_tree(self) -> Dict:
        return self.knowledge_graph
    
    def get_flat_nodes(self) -> List[Dict]:
        nodes = []
        for category, category_data in self.knowledge_graph.items():
            nodes.append({
                "name": category,
                "type": "category",
                **category_data.get("properties", {})
            })
            if "children" in category_data:
                for node_data in category_data["children"].values():
                    nodes.append({
                        "name": node_data.get("name", ""),
                        "type": "knowledge",
                        "category": category,
                        **node_data.get("properties", {})
                    })
        return nodes
    
    def update_mastery_level(self, name: str, level: float) -> bool:
        node = self.get_node(name)
        if node:
            old_level = node["properties"].get("mastery_level", 0.0)
            new_level = max(0.0, min(1.0, level))
            node["properties"]["mastery_level"] = new_level
            
            if new_level >= 0.8:
                node["properties"]["status"] = "已掌握"
            elif new_level > 0:
                node["properties"]["status"] = "学习中"
            else:
                node["properties"]["status"] = "未学"
            
            node["properties"].setdefault("history", []).append({
                "action": "mastery_update",
                "timestamp": datetime.now().isoformat(),
                "old_level": old_level,
                "new_level": new_level
            })
            
            return True
        return False
    
    def get_learning_progress(self) -> Dict[str, Any]:
        total = 0
        learned = 0
        mastered = 0
        mastery_sum = 0.0
        
        for category_data in self.knowledge_graph.values():
            if "children" in category_data:
                for node_data in category_data["children"].values():
                    total += 1
                    properties = node_data.get("properties", {})
                    status = properties.get("status", "未学")
                    if status != "未学":
                        learned += 1
                        mastery_sum += properties.get("mastery_level", 0.0)
                    if status == "已掌握":
                        mastered += 1
        
        return {
            "total": total,
            "learned": learned,
            "mastered": mastered,
            "average_mastery": mastery_sum / learned if learned > 0 else 0.0,
            "progress_rate": learned / total if total > 0 else 0.0,
            "mastery_rate": mastered / total if total > 0 else 0.0
        }
    
    def get_category_progress(self) -> Dict[str, Any]:
        result = {}
        for category, category_data in self.knowledge_graph.items():
            total = 0
            learned = 0
            mastery_sum = 0.0
            
            if "children" in category_data:
                for node_data in category_data["children"].values():
                    total += 1
                    properties = node_data.get("properties", {})
                    if properties.get("status") != "未学":
                        learned += 1
                        mastery_sum += properties.get("mastery_level", 0.0)
            
            result[category] = {
                "total": total,
                "learned": learned,
                "progress_rate": learned / total if total > 0 else 0.0,
                "average_mastery": mastery_sum / learned if learned > 0 else 0.0
            }
        
        return result
    
    def save(self) -> bool:
        data = {
            "knowledge_graph": self.knowledge_graph,
            "relations": self.relations,
            "node_index": self.node_index,
            "saved_at": datetime.now().isoformat()
        }
        
        save_file = self.persist_dir / "knowledge_graph.json"
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[错误] 保存知识图谱失败：{e}")
            return False
    
    def load(self) -> bool:
        save_file = self.persist_dir / "knowledge_graph.json"
        
        if not save_file.exists():
            return False
        
        try:
            with open(save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.knowledge_graph = data.get("knowledge_graph", {})
                self.relations = data.get("relations", {})
                self.node_index = data.get("node_index", {})
            return True
        except Exception as e:
            print(f"[错误] 加载知识图谱失败：{e}")
            return False
    
    def clear(self):
        self.knowledge_graph = {}
        self.relations = {}
        self.node_index = {}
        self._init_base_categories()
        self.save()
    
    def get_stats(self) -> Dict[str, Any]:
        total_categories = len(self.categories)
        total_nodes = sum(len(cat_data.get("children", {})) 
                         for cat_data in self.knowledge_graph.values())
        total_relations = sum(len(rels) for rels in self.relations.values())
        
        return {
            "categories": total_categories,
            "knowledge_nodes": total_nodes,
            "relations": total_relations
        }


knowledge_graph = KnowledgeGraph()
