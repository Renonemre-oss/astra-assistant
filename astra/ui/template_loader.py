#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - HTML Template Loader
Utility to load and cache HTML templates for the UI.
"""

import logging
from pathlib import Path
from typing import Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    Loads and caches HTML templates for the ASTRA UI.
    
    Features:
    - Automatic caching
    - Template validation
    - Fallback templates
    - Error handling
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template loader.
        
        Args:
            templates_dir: Directory containing templates (auto-detected if None)
        """
        if templates_dir is None:
            # Auto-detect templates directory
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = templates_dir
        self._cache: Dict[str, str] = {}
        
        # Ensure templates directory exists
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Template loader initialized: {self.templates_dir}")
    
    def load_template(self, template_name: str, use_cache: bool = True) -> str:
        """
        Load an HTML template.
        
        Args:
            template_name: Name of the template file (e.g., "background.html")
            use_cache: Whether to use cached version if available
            
        Returns:
            Template content as string
            
        Raises:
            FileNotFoundError: If template not found and no fallback available
        """
        # Check cache first
        if use_cache and template_name in self._cache:
            logger.debug(f"Loading template from cache: {template_name}")
            return self._cache[template_name]
        
        # Build template path
        template_path = self.templates_dir / template_name
        
        try:
            # Load template
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache it
            self._cache[template_name] = content
            logger.info(f"✅ Template loaded: {template_name}")
            
            return content
        
        except FileNotFoundError:
            logger.error(f"❌ Template not found: {template_path}")
            
            # Try to return fallback
            fallback = self._get_fallback_template(template_name)
            if fallback:
                logger.warning(f"⚠️ Using fallback template for: {template_name}")
                return fallback
            
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        except Exception as e:
            logger.error(f"❌ Error loading template {template_name}: {e}")
            raise
    
    def _get_fallback_template(self, template_name: str) -> Optional[str]:
        """
        Get fallback template content.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Fallback template content or None
        """
        # Fallback for background.html
        if template_name == "background.html":
            return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
</head>
<body></body>
</html>
"""
        
        return None
    
    def reload_template(self, template_name: str) -> str:
        """
        Force reload a template (bypass cache).
        
        Args:
            template_name: Name of the template
            
        Returns:
            Fresh template content
        """
        # Clear from cache
        if template_name in self._cache:
            del self._cache[template_name]
        
        # Reload
        return self.load_template(template_name, use_cache=False)
    
    def clear_cache(self):
        """Clear all cached templates."""
        self._cache.clear()
        logger.info("🗑️ Template cache cleared")
    
    def list_templates(self) -> list:
        """
        List all available templates.
        
        Returns:
            List of template filenames
        """
        try:
            templates = list(self.templates_dir.glob("*.html"))
            return [t.name for t in templates]
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []


# Global template loader instance
_template_loader: Optional[TemplateLoader] = None


def get_template_loader() -> TemplateLoader:
    """
    Get global template loader instance (singleton).
    
    Returns:
        TemplateLoader instance
    """
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader


def load_html_template(template_name: str) -> str:
    """
    Convenience function to load a template.
    
    Args:
        template_name: Name of the template file
        
    Returns:
        Template content
    """
    return get_template_loader().load_template(template_name)


# Commonly used templates as functions
def get_background_html() -> str:
    """
    Get the animated background HTML.
    
    Returns:
        Background HTML content
    """
    return load_html_template("background.html")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get loader
    loader = get_template_loader()
    
    # List available templates
    print("📄 Available templates:")
    for template in loader.list_templates():
        print(f"  - {template}")
    
    # Load background template
    try:
        background = get_background_html()
        print(f"\n✅ Background template loaded ({len(background)} characters)")
        print(f"First 100 chars: {background[:100]}...")
    except FileNotFoundError:
        print("\n⚠️ Background template not found, using fallback")
        # Fallback will be used automatically
    
    # Test cache
    print("\n🔄 Testing cache...")
    import time
    
    start = time.time()
    loader.load_template("background.html", use_cache=False)
    no_cache_time = time.time() - start
    
    start = time.time()
    loader.load_template("background.html", use_cache=True)
    cache_time = time.time() - start
    
    print(f"Without cache: {no_cache_time*1000:.2f}ms")
    print(f"With cache: {cache_time*1000:.2f}ms")
    print(f"Speedup: {no_cache_time/cache_time:.1f}x faster")
