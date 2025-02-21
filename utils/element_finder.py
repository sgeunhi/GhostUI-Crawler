from xml.etree import ElementTree
from typing import Dict

class ElementFinder:
    def __init__(self, driver):
        self.driver = driver
        self.xml_source = None
        self.root = None

    # View Hierachy를 가져와서 view_hierarchy.xml 파일로 저장
    def get_view_hierarchy(self) -> str:
        self.xml_source = self.driver.page_source
        with open("view_hierarchy.xml", "w", encoding="utf-8") as f:
            f.write(self.xml_source)

        self.root = ElementTree.fromstring(self.xml_source)
        return self.xml_source

    def _ensure_hierarchy_loaded(self) -> None:
        if self.root is None:
            self.get_view_hierarchy()

    # Gesture에 따라 interactive element 찾기
    # tap, double_tap의 경우 clickable="true"
    def find_tappable_elements(self) -> list[ElementTree.Element]:
        self._ensure_hierarchy_loaded()

        return [
            node for node in self.root.iter()
            if node.attrib.get("clickable") == "true"
        ]
    
    # long_press의 경우 "clickable"""="true" and "long_clickable""="true"
    def find_long_pressable_elements(self) -> list[ElementTree.Element]:
        self._ensure_hierarchy_loaded()

        return [
            node for node in self.root.iter()
            if node.attrib.get("clickable") == "true" and 
            node.attrib.get("long_clickable") == "true"
        ]
    
    # swipe의 경우 scrollable="true"
    def find_swipeable_elements(self) -> list[ElementTree.Element]:
        self._ensure_hierarchy_loaded()

        return [
            node for node in self.root.iter()
            if node.attrib.get("scrollable") == "true"
        ]
    
    # pinch_zoom의 경우 zoomable="true"
    def find_pinch_zoomable_elements(self) -> list[ElementTree.Element]:
        self._ensure_hierarchy_loaded()
        
        pinch_zoom_view_classes = {
            "android.webkit.WebView",
            "android.widget.ImageView",
            "com.google.android.gms.maps.MapView",
            "android.view.ViewGroup"  # 커스텀 구현이 있을 수 있는 ViewGroup
        }

        return [
            node for node in self.root.iter()
            if node.attrib.get("scalable") == "true" or
               node.attrib.get("class") in pinch_zoom_view_classes
        ]

    def get_element_info(self, element: ElementTree.Element) -> Dict[str, str]:
        return {
            "class": element.attrib.get("class", ""),
            "resource-id": element.attrib.get("resource-id", ""),
            "content-desc": element.attrib.get("content-desc", ""),
            "bounds": element.attrib.get("bounds", ""),
            "clickable": element.attrib.get("clickable", "false"),
            "long-clickable": element.attrib.get("long-clickable", "false"),
            "scrollable": element.attrib.get("scrollable", "false"),
            "scalable": element.attrib.get("scalable", "false")
        }
    
