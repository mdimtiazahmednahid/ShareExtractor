import logging
from typing import List
from app.models.share_profile import ShareProfile
from app.automation.ui_inspector import UIInspector
from app.utils.text_normalizer import normalize_text

logger = logging.getLogger(__name__)

class ProfileExtractor:
    def __init__(self, min_confidence=0.60):
        self.min_confidence = min_confidence

    def extract(self, xml_source: str, session_id: str) -> List[ShareProfile]:
        profiles = []
        if not xml_source:
            return profiles
            
        nodes = UIInspector.parse_xml_to_nodes(xml_source)
        
        # A simple layered heuristic approach for extracting profiles.
        # Facebook UI is dynamic. A common pattern is:
        # - Clickable nodes containing profile names.
        # - Often inside a RecyclerView.
        # - Content-desc may contain name or action.
        
        for node in nodes:
            text = node.get("text", "")
            content_desc = node.get("content-desc", "")
            clickable = node.get("clickable")
            
            # Skip obvious UI elements
            ignore_list = ["share", "like", "comment", "follow", "invite", "see more", "back", "close", "search", "menu", "profile photo"]
            if text.lower() in ignore_list or content_desc.lower() in ignore_list:
                continue
                
            candidate_name = text if text else content_desc
            if not candidate_name:
                continue
                
            # Score this candidate
            score = 0.0
            
            # Is it clickable? (Profiles in lists usually are)
            if clickable:
                score += 0.3
                
            # Does it look like a real name? (No numbers, not too long, not too short)
            if len(candidate_name) > 2 and len(candidate_name) < 40 and not any(char.isdigit() for char in candidate_name):
                score += 0.4
                
            # Check content-desc for hidden URLs if any (Facebook sometimes embeds them)
            # In official FB App this is rare, but we check.
            url = None
            if "facebook.com/" in content_desc.lower():
                url = content_desc
                score += 0.5
                
            confidence = min(score, 1.0)
            if confidence >= self.min_confidence:
                profiles.append(ShareProfile(
                    name=normalize_text(candidate_name),
                    profile_url=url, # if exposed
                    share_url=None, # not typically exposed in the list UI directly
                    confidence=confidence,
                    source="facebook_android_ui",
                    session_id=session_id
                ))
                
        logger.debug(f"Extracted {len(profiles)} candidates from source.")
        return profiles
