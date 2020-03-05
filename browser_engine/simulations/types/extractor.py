import yaml
from extraction_engine import ExtractionEngine
import uuid
import extraction_engine
import logging

logger = logging.getLogger(__name__)


class ScreenshotExtractor:

    def __init__(self, task=None, browser=None):
        self.task = task
        self.browser = browser

    @property
    def task_id(self):
        return self.task.get("task_id")

    def run(self):
        result_data = {
            "data": None,
            "task_type": self.task.get("task_type"),
            "is_task_success": False
        }
        try:
            result_data['data'] = self.browser.get_screenshot()
            result_data['is_task_success'] = True
        except Exception as e:
            print("task failed with error", e)
            result_data['error_message'] = str(e)
        return result_data



class HTMLExtractor:

    def __init__(self, task=None, browser=None):
        self.task = task
        self.browser = browser

    @property
    def task_id(self):
        return self.task.get("task_id")

    def run(self):
        result_data = {
            "data": None,
            "task_type": self.task.get("task_type"),
            "is_task_success": False
        }
        try:
            result_data['data'] = self.browser.page_source()
            result_data['is_task_success'] = True
        except Exception as e:
            print("task failed with error", e)
            result_data['error_message'] = str(e)
        return result_data


class JsonExtractorSimulation:
    """

    task = {
           "task_id": "step_1",
            "task_type": "json_extractor",
            "task_code": "- extractor_type: MetaTagExtractor
  extractor_id: meta_tags
- extractor_type: CustomContentExtractor
  extractor_id: content
  data_selectors:
  - selector_id: title
    selector: title
    selector_type: css
    selector_attribute: text
    data_type: RawField"
    }

    """

    def __init__(self, task=None, browser=None):
        self.task = task
        self.browser = browser

    @property
    def task_id(self):
        return self.task.get("task_id")

    def run(self):
        task_code = self.task.get("task_code")
        extraction_manifest = yaml.load(task_code, yaml.Loader)
        engine = ExtractionEngine(html=self.browser.page_source(), extraction_manifest=extraction_manifest)
        return engine.extract_data()


class TraversalExtractorSimulation:
    """

    task = {
       "task_id": "step_1",
        "task_type": "traversal_extractor",
        "task_code": "- traversal_id: default_traversal
  selector: "a"
  selector_type: css
  selector_attribute: href
  data_type: ListStringField
  max_requests: 500
  next_spider_id: default_spider"
    }

    """

    def __init__(self, task=None, browser=None):
        self.task = task
        self.browser = browser

    @property
    def task_id(self):
        return self.task.get("task_id")

    def run(self):
        task_code = self.task.get("task_code")
        traversal_extraction_manifest = yaml.load(task_code, yaml.Loader)
        traversal_manifests = []
        for traversal in traversal_extraction_manifest:
            traversal['selector_id'] = traversal['traversal_id']
            traversal_manifest = {
                "extractor_id": traversal['traversal_id'],
                "extractor_type": "CustomContentExtractor",
                "data_selectors": [
                    traversal
                ]
            }
            traversal_manifests.append(traversal_manifest)
        engine = ExtractionEngine(html=self.browser.page_source(), extraction_manifest=traversal_manifests)
        traversal_data_raw = engine.extract_data()

        traversal_data = {}
        if traversal_data_raw is not None:
            for k, v in traversal_data_raw.items():
                traversal_data.update(v)

        return traversal_data
