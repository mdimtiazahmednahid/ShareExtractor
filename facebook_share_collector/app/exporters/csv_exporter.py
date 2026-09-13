import csv
import logging
import os
from typing import List
from app.models.share_profile import ShareProfile

logger = logging.getLogger(__name__)

class CSVExporter:
    @staticmethod
    def export(profiles: List[ShareProfile], output_path: str):
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # UTF-8 with BOM for Excel compatibility
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'Name', 'Profile URL', 'Share URL', 'Confidence', 
                    'Source', 'First Seen', 'Last Seen', 'Session ID'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for profile in profiles:
                    writer.writerow({
                        'Name': profile.name,
                        'Profile URL': profile.profile_url or "",
                        'Share URL': profile.share_url or "",
                        'Confidence': f"{profile.confidence:.2f}",
                        'Source': profile.source,
                        'First Seen': profile.first_seen_at,
                        'Last Seen': profile.last_seen_at,
                        'Session ID': profile.session_id
                    })
            logger.info(f"Successfully exported {len(profiles)} profiles to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export CSV to {output_path}: {e}")
            return False
