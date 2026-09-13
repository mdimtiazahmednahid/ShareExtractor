import logging
import time
from PySide6.QtCore import QThread, Signal
from app.models.collection_session import CollectionSession
from app.automation.appium_manager import AppiumManager
from app.automation.facebook_detector import FacebookDetector
from app.automation.share_list_detector import ShareListDetector
from app.automation.profile_extractor import ProfileExtractor
from app.automation.scroll_controller import ScrollController
from app.automation.ui_inspector import UIInspector
from app.utils.deduplicator import Deduplicator

logger = logging.getLogger(__name__)

class CollectorEngine(QThread):
    # Signals for GUI updates
    status_updated = Signal(str)
    profile_found = Signal(object)
    stats_updated = Signal(int, int, int) # total_profiles, total_scrolls, new_this_pass
    finished_collection = Signal()
    error_occurred = Signal(str)
    auto_save_requested = Signal()

    def __init__(self, appium_manager: AppiumManager, session: CollectionSession, config: dict):
        super().__init__()
        self.appium = appium_manager
        self.session = session
        self.config = config
        
        self.is_running = False
        self.is_paused = False
        
        self.deduplicator = Deduplicator()
        
        self.fb_detector = FacebookDetector(self.config.get("facebook.package", "com.facebook.katana"))
        self.share_detector = ShareListDetector()
        
        min_conf = self.config.get("extraction.minimum_confidence", 0.6)
        self.extractor = ProfileExtractor(min_confidence=min_conf)
        
        self.auto_retry = False
        self.auto_save = False
        self.profiles_since_last_save = 0

    def run(self):
        self.is_running = True
        self.status_updated.emit("COLLECTING")
        
        driver = self.appium.get_driver()
        if not driver:
            self.error_occurred.emit("Appium driver not available.")
            self.stop()
            return
            
        scroll_controller = ScrollController(driver)
        
        max_scrolls = self.config.get("collector.max_scrolls", 500)
        max_no_new_results = self.config.get("collector.max_no_new_results", 5)
        
        scrolls = 0
        empty_passes = 0
        
        last_xml_source = ""
        
        while self.is_running and scrolls < max_scrolls:
            if self.is_paused:
                self.status_updated.emit("PAUSED")
                time.sleep(1)
                continue
                
            self.status_updated.emit("COLLECTING")
            
            # 1. Verify Facebook foreground
            if not self.fb_detector.is_facebook_foreground(driver):
                self.error_occurred.emit("Facebook is not in the foreground.")
                self.stop()
                break
                
            # 2. Get Source
            xml_source = UIInspector.get_page_source(driver)
            if xml_source == last_xml_source:
                logger.info("Page source has not changed after scroll.")
                empty_passes += 1
                if empty_passes >= max_no_new_results:
                    if self.auto_retry:
                        logger.info("End of list reached, waiting 5s for lazy load (Auto-Retry)...")
                        self.status_updated.emit("WAITING 5s (LAZY LOAD)")
                        time.sleep(5)
                        empty_passes = 0
                        self.status_updated.emit("COLLECTING")
                    else:
                        logger.info("End of list reached (source stable).")
                        break
            
            # 3. Verify it's a share list
            # We might want to only strictly check this on the first pass, 
            # as headers scroll out of view. We'll check it, but not fail immediately.
            
            # 4. Extract
            new_this_pass = 0
            if xml_source != last_xml_source:
                candidates = self.extractor.extract(xml_source, self.session.id)
                
                for candidate in candidates:
                    # Deduplication bypassed by user request to collect raw responses
                    self.profile_found.emit(candidate)
                    self.session.total_profiles += 1
                    new_this_pass += 1
                    
                    if self.auto_save:
                        self.profiles_since_last_save += 1
                        if self.profiles_since_last_save >= 50:
                            self.auto_save_requested.emit()
                            self.profiles_since_last_save = 0
                
                # Only reset it if the screen did change.
                empty_passes = 0
                
            self.stats_updated.emit(self.session.total_profiles, scrolls, new_this_pass)
            last_xml_source = xml_source
            
            if empty_passes >= max_no_new_results:
                logger.info("End of list reached (no new results).")
                break
                
            # 5. Scroll
            self.status_updated.emit("SCROLLING")
            if not scroll_controller.scroll_forward():
                logger.error("Failed to scroll.")
                break
                
            scrolls += 1
            self.session.total_scrolls = scrolls
            
        self.stop()
        self.status_updated.emit("COMPLETED")
        self.finished_collection.emit()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_running = False
        self.is_paused = False
