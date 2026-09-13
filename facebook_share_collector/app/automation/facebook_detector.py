import logging

logger = logging.getLogger(__name__)

class FacebookDetector:
    def __init__(self, expected_package="com.facebook.katana"):
        self.expected_package = expected_package
        
    def is_facebook_foreground(self, driver) -> bool:
        if not driver:
            return False
            
        try:
            current_pkg = driver.current_package
            if current_pkg == self.expected_package:
                return True
                
            # Allow fallback for basic facebook app etc if configured
            if "facebook" in current_pkg.lower():
                logger.warning(f"Foreground is {current_pkg}, which contains 'facebook' but is not exactly {self.expected_package}")
                return True
                
            logger.info(f"Current foreground app is {current_pkg}, expecting {self.expected_package}")
            return False
        except Exception as e:
            logger.error(f"Failed to detect foreground app: {e}")
            return False

    def get_current_activity(self, driver) -> str:
        if not driver:
            return ""
        try:
            return driver.current_activity
        except Exception:
            return ""
