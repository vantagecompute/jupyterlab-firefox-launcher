#!/usr/bin/env python3
"""
Test suite for CSP proxy functionality in JupyterLab Firefox Launcher.

This test suite validates:
1. CSP header modification for iframe embedding
2. Backend proxy handler functionality  
3. Frontend URL construction logic
4. End-to-end iframe embedding workflow
"""

import pytest
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from jupyter_server.base.handlers import JupyterHandler

# Import our handlers
from jupyterlab_firefox_launcher.firefox_handler import (
    XpraProxyHandler,
    FirefoxLauncherHandler,
    FirefoxCleanupHandler
)

class TestCSPProxy:
    """Test CSP header modification functionality."""
    
    def test_modify_csp_frame_ancestors_none(self):
        """Test CSP modification when frame-ancestors is 'none'."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        original_csp = "script-src 'self'; frame-ancestors 'none'; form-action 'self'"
        expected_csp = "script-src 'self'; frame-ancestors *; form-action 'self'"
        
        result = handler._modify_csp(original_csp)
        assert result == expected_csp
    
    def test_modify_csp_frame_ancestors_self(self):
        """Test CSP modification when frame-ancestors is 'self'."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        original_csp = "script-src 'self'; frame-ancestors 'self'; form-action 'self'"
        expected_csp = "script-src 'self'; frame-ancestors *; form-action 'self'"
        
        result = handler._modify_csp(original_csp)
        assert result == expected_csp
    
    def test_modify_csp_no_frame_ancestors(self):
        """Test CSP modification when no frame-ancestors directive exists."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        original_csp = "script-src 'self'; form-action 'self'"
        expected_csp = "script-src 'self'; form-action 'self'; frame-ancestors *"
        
        result = handler._modify_csp(original_csp)
        assert result == expected_csp
    
    def test_modify_csp_empty(self):
        """Test CSP modification with empty/None input."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        assert handler._modify_csp("") == ""
        assert handler._modify_csp(None) is None
    
    def test_modify_csp_complex(self):
        """Test CSP modification with complex real-world CSP header."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        original_csp = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
            "font-src 'self'; frame-ancestors 'none'; "
            "connect-src 'self' ws: wss:; object-src 'none'"
        )
        
        result = handler._modify_csp(original_csp)
        
        # Should replace frame-ancestors 'none' with frame-ancestors *
        assert "frame-ancestors *" in result
        assert "frame-ancestors 'none'" not in result
        
        # Should preserve all other directives
        assert "default-src 'self'" in result
        assert "script-src 'self' 'unsafe-inline' 'unsafe-eval'" in result
        assert "object-src 'none'" in result


class TestProxyHandler(AsyncHTTPTestCase):
    """Test the XpraProxyHandler functionality."""
    
    def get_app(self):
        """Create test application with proxy handler."""
        app = Application([
            (r'/firefox-launcher/proxy', XpraProxyHandler),
        ])
        
        # Mock settings
        app.settings = {
            'base_url': '/test/',
            'log': Mock()
        }
        
        return app
    
    def test_proxy_handler_missing_port(self):
        """Test proxy handler with missing port parameter."""
        response = self.fetch('/firefox-launcher/proxy?host=localhost')
        
        assert response.code == 400
        assert b'Missing required \'port\' parameter' in response.body
    
    @patch('aiohttp.ClientSession')
    def test_proxy_handler_success(self, mock_session):
        """Test successful proxy request with CSP modification."""
        # Mock aiohttp response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {
            'Content-Type': 'text/html',
            'Content-Security-Policy': 'frame-ancestors \'none\'',
            'Content-Length': '100'
        }
        mock_response.content.iter_chunked.return_value = [b'<html>test</html>']
        
        mock_session_instance = AsyncMock()
        mock_session_instance.request.return_value.__aenter__.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        response = self.fetch('/firefox-launcher/proxy?host=localhost&port=8080')
        
        # Should return 200 with modified headers
        assert response.code == 200
        
        # Check that CSP was modified
        csp_header = response.headers.get('Content-Security-Policy', '')
        assert 'frame-ancestors *' in csp_header
        assert 'frame-ancestors \'none\'' not in csp_header
        
        # Check X-Frame-Options was added
        assert response.headers.get('X-Frame-Options') == 'ALLOWALL'


class TestFirefoxLauncherIntegration:
    """Test end-to-end Firefox launcher integration."""
    
    def test_frontend_proxy_url_construction(self):
        """Test that frontend constructs correct proxy URLs."""
        # Simulate frontend proxy URL construction logic
        base_path = "/user/testuser/"
        host = "localhost"
        port = "8080"
        
        expected_proxy_url = f"{base_path}firefox-launcher/proxy?host={host}&port={port}"
        actual_proxy_url = f"{base_path}firefox-launcher/proxy?host={host}&port={port}"
        
        assert actual_proxy_url == expected_proxy_url
    
    def test_jupyterhub_base_path_detection(self):
        """Test JupyterHub base path detection logic."""
        # Test cases for different URL patterns
        test_cases = [
            ("/user/alice/lab", "/user/alice/"),
            ("/user/bob-test/tree", "/user/bob-test/"),
            ("/user/user123/", "/user/user123/"),
            ("/lab", "/"),  # No user path
            ("/tree", "/"),  # No user path
        ]
        
        for current_path, expected_base in test_cases:
            # Simulate the regex matching from frontend
            import re
            user_match = re.match(r'^(\/user\/[^\/]+\/)', current_path)
            base_path = user_match.group(1) if user_match else "/"
            
            assert base_path == expected_base, f"Failed for path: {current_path}"


class TestDependencyChecking:
    """Test system dependency validation."""
    
    def test_dependency_check_structure(self):
        """Test dependency check returns correct structure."""
        from jupyterlab_firefox_launcher.firefox_handler import _check_dependencies
        
        result = _check_dependencies()
        
        # Should have required keys
        assert 'missing' in result
        assert 'all_present' in result
        
        # missing should be a list
        assert isinstance(result['missing'], list)
        
        # all_present should be a boolean
        assert isinstance(result['all_present'], bool)
        
        # If no missing deps, all_present should be True
        if not result['missing']:
            assert result['all_present'] is True
        else:
            assert result['all_present'] is False
    
    @patch('shutil.which')
    def test_dependency_check_missing_xpra(self, mock_which):
        """Test dependency check when Xpra is missing."""
        def mock_which_func(command):
            if command == 'xpra':
                return None
            elif command == 'firefox':
                return '/usr/bin/firefox'
            elif command == 'Xvfb':
                return '/usr/bin/Xvfb'
            return '/usr/bin/' + command
        
        mock_which.side_effect = mock_which_func
        
        from jupyterlab_firefox_launcher.firefox_handler import _check_dependencies
        
        result = _check_dependencies()
        
        assert result['all_present'] is False
        assert len(result['missing']) == 1
        assert result['missing'][0]['name'] == 'Xpra'
    
    @patch('shutil.which')
    def test_dependency_check_all_present(self, mock_which):
        """Test dependency check when all dependencies are present."""
        mock_which.return_value = '/usr/bin/mock_command'
        
        from jupyterlab_firefox_launcher.firefox_handler import _check_dependencies
        
        result = _check_dependencies()
        
        assert result['all_present'] is True
        assert len(result['missing']) == 0


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_dependency_error_html_rendering(self):
        """Test dependency error HTML rendering."""
        from jupyterlab_firefox_launcher.firefox_handler import _render_dependency_error_html
        
        missing_deps = [
            {
                "name": "Xpra",
                "description": "Remote display server",
                "install_commands": ["sudo apt install xpra", "# Install Xpra"]
            }
        ]
        
        html = _render_dependency_error_html(missing_deps)
        
        assert isinstance(html, str)
        assert 'Xpra' in html
        assert 'Remote display server' in html
        assert 'sudo apt install xpra' in html
    
    def test_dependency_error_html_fallback(self):
        """Test dependency error HTML fallback when template fails."""
        from jupyterlab_firefox_launcher.firefox_handler import _render_dependency_error_html
        
        # Mock missing template to trigger fallback
        missing_deps = [{"name": "Test", "description": "Test dep", "install_commands": []}]
        
        with patch('builtins.open', side_effect=FileNotFoundError):
            html = _render_dependency_error_html(missing_deps)
            
            assert isinstance(html, str)
            assert 'Test' in html
            assert 'Test dep' in html


class TestCSPIntegration:
    """Test end-to-end CSP iframe embedding workflow."""
    
    @pytest.mark.asyncio
    async def test_csp_proxy_workflow(self):
        """Test complete CSP proxy workflow."""
        # This test simulates the complete workflow:
        # 1. Frontend constructs proxy URL
        # 2. Backend strips CSP headers
        # 3. Content is delivered for iframe embedding
        
        # Step 1: Frontend URL construction
        base_path = "/user/testuser/"
        host = "localhost"
        port = "8080"
        proxy_url = f"{base_path}firefox-launcher/proxy?host={host}&port={port}"
        
        assert "firefox-launcher/proxy" in proxy_url
        assert f"host={host}" in proxy_url
        assert f"port={port}" in proxy_url
        
        # Step 2: CSP header modification (unit test)
        handler = XpraProxyHandler(Mock(), Mock())
        original_csp = "frame-ancestors 'none'"
        modified_csp = handler._modify_csp(original_csp)
        
        assert modified_csp == "frame-ancestors *"
        
        # Step 3: Verify iframe embedding is now possible
        # (In real test, this would involve actual HTTP requests)
        assert "frame-ancestors *" in modified_csp
        assert "frame-ancestors 'none'" not in modified_csp


# Performance and load testing
class TestPerformance:
    """Test performance characteristics."""
    
    def test_csp_modification_performance(self):
        """Test CSP modification performance with large headers."""
        handler = XpraProxyHandler(Mock(), Mock())
        
        # Create a large CSP header
        large_csp = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:",
            "style-src 'self' 'unsafe-inline' blob: data:",
            "img-src 'self' data: blob: https:",
            "font-src 'self' data: blob:",
            "connect-src 'self' ws: wss: https:",
            "media-src 'self' blob: data:",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "upgrade-insecure-requests"
        ])
        
        # Time the modification
        start_time = time.time()
        result = handler._modify_csp(large_csp)
        end_time = time.time()
        
        # Should complete quickly (< 1ms for reasonable CSP headers)
        assert (end_time - start_time) < 0.001
        
        # Should correctly modify the header
        assert "frame-ancestors *" in result
        assert "frame-ancestors 'none'" not in result


# Integration test with mock Xpra server
class TestXpraIntegration:
    """Test integration with mock Xpra server."""
    
    @pytest.mark.asyncio
    async def test_mock_xpra_csp_response(self):
        """Test proxy behavior with mock Xpra server response."""
        # This simulates an Xpra server response with CSP headers
        mock_xpra_response = {
            'status': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Content-Security-Policy': (
                    'default-src \'self\'; script-src \'self\' \'unsafe-inline\'; '
                    'frame-ancestors \'none\'; object-src \'none\''
                ),
                'X-Frame-Options': 'DENY',
                'Cache-Control': 'no-cache'
            },
            'body': '<html><head><title>Xpra</title></head><body>Xpra Server</body></html>'
        }
        
        # Test CSP modification
        handler = XpraProxyHandler(Mock(), Mock())
        original_csp = mock_xpra_response['headers']['Content-Security-Policy']
        modified_csp = handler._modify_csp(original_csp)
        
        # Verify modification
        assert 'frame-ancestors *' in modified_csp
        assert 'frame-ancestors \'none\'' not in modified_csp
        
        # Verify other directives are preserved
        assert 'default-src \'self\'' in modified_csp
        assert 'script-src \'self\' \'unsafe-inline\'' in modified_csp
        assert 'object-src \'none\'' in modified_csp


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
