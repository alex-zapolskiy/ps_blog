from ps_blog import settings


CACHE_TIMEOUTS = getattr(settings, 'NOTES_CACHE_TIMEOUT', {})
SECTIONS_CACHE = CACHE_TIMEOUTS.get('sections', 3600)
CHAPTERS_CACHE = CACHE_TIMEOUTS.get('chapters', 3600)
CHAPTERS_TEXT_CACHE = CACHE_TIMEOUTS.get('chapter_text', 86400)