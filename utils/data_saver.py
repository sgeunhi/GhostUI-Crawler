import os
import json
import shutil
from xml.etree import ElementTree

class DataSaver:
    def __init__(self, base_dir="dataset"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.current_index_dir = None

    def get_action_dir(self, app_name, action):
        """현재 액션(action)에 대한 폴더 경로를 반환"""
        return os.path.join(self.base_dir, app_name, action)
    
    def get_next_index_dir(self, app_name, action):
        """새로운 index 디렉토리를 생성하고 경로 저장"""
        action_dir = self.get_action_dir(app_name, action)
        os.makedirs(action_dir, exist_ok=True)

        existing_indices = [
            int(folder) for folder in os.listdir(action_dir) if folder.isdigit()
        ]
        
        next_index = (max(existing_indices) + 1) if existing_indices else 0
        self.current_index_dir = os.path.join(action_dir, str(next_index))
        os.makedirs(self.current_index_dir, exist_ok=True)
        
        return self.current_index_dir

    # 0부터 시작하는 index를 action 하위 폴더로 생성
    def get_save_path(self, stage, extension):
        """현재 index 디렉토리에 저장할 파일 경로 반환"""
        if not self.current_index_dir:
            raise ValueError("prepare_new_index_dir()를 먼저 호출해야 합니다.")
        
        return os.path.join(self.current_index_dir, f"{stage}.{extension}")

    # 스크린샷 저장
    def save_screenshot(self, driver, app_name, action, stage):
        """스크린샷 저장"""
        if stage == "before":
            self.get_next_index_dir(app_name, action)

        path = self.get_save_path(stage, "png")
        driver.get_screenshot_as_file(path)
        print(f"📸 스크린샷 저장됨: {path}")
        return path

    # view hierarchy -> xml 파일로 저장
    def save_view_hierarchy(self, driver, app_name, action, stage):
        path = self.get_save_path(stage, "xml")
        xml_data = driver.page_source
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml_data)
        print(f"📂 View Hierarchy 저장됨: {path}")
        return path

    # simplified view hierarchy -> json 파일로 저장
    def save_simplified_view_hierarchy(self, driver, app_name, action, stage):
        path = self.get_save_path(stage, "json")
        xml_data = driver.page_source
        root = ElementTree.fromstring(xml_data)

        elements = []
        for node in root.iter():
            # print(node.tag, node.attrib, node.text)
            element = node.attrib
            
            elements.append(element)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(elements, f, indent=4)
        print(f"📂 Simplified View Hierarchy 저장됨: {path}")
        
        return path

    # action_data -> json 파일로 저장
    def save_action_data(self, app_name, action, element_id, bounds):
        path = self.get_save_path("action", "json")
        metadata = {
            "action": action,
            "element_id": element_id,
            "bounds": bounds,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        print(f"📜 액션 데이터 저장됨: {path}")
        return path

    def delete_data(self, app_name, action):
        """현재 작업 중인 디렉토리 삭제"""
        if self.current_index_dir and os.path.exists(self.current_index_dir):
            shutil.rmtree(self.current_index_dir)
            print(f"🗑️ 변화 없음 -> 폴더 삭제: {self.current_index_dir}")
            self.current_index_dir = None
        else:
            print("⚠️ 삭제할 폴더가 없습니다.")
        