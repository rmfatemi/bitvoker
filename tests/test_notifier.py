"""Unit tests for notifier.py module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bitvoker.notifier import Notifier


@pytest.fixture
def sample_destinations():
    """Return sample destination configurations."""
    return [
        {
            "name": "Test1",
            "url": "apprise://test1",
            "enabled": True
        },
        {
            "name": "Test2",
            "url": "apprise://test2",
            "enabled": True
        },
        {
            "name": "Disabled",
            "url": "apprise://disabled",
            "enabled": False
        }
    ]


class TestNotifier:
    """Test cases for Notifier class."""

    def test_init_empty(self):
        """Test Notifier initialization with no destinations."""
        notifier = Notifier()
        assert notifier.destinations_config == []
        assert notifier.apprise is not None

    def test_init_with_destinations(self, sample_destinations):
        """Test Notifier initialization with destinations."""
        with patch('apprise.Apprise') as mock_apprise:
            mock_instance = Mock()
            mock_apprise.return_value = mock_instance
            notifier = Notifier(sample_destinations)
            assert notifier.destinations_config == sample_destinations
            # Should add only enabled destinations
            assert mock_instance.add.call_count == 2

    def test_setup_destinations_disabled(self, sample_destinations):
        """Test that disabled destinations are not added."""
        with patch('apprise.Apprise') as mock_apprise:
            mock_instance = Mock()
            mock_apprise.return_value = mock_instance
            notifier = Notifier(sample_destinations)
            
            # Should only add Test1 and Test2 (not Disabled)
            assert mock_instance.add.call_count == 2
            calls = mock_instance.add.call_args_list
            tags = [call[1]['tag'] for call in calls]
            assert 'Test1' in tags
            assert 'Test2' in tags
            assert 'Disabled' not in tags

    def test_update_destinations(self, sample_destinations):
        """Test updating destinations."""
        with patch('apprise.Apprise') as mock_apprise:
            mock_instance = Mock()
            mock_apprise.return_value = mock_instance
            
            notifier = Notifier()
            assert mock_instance.add.call_count == 0
            
            notifier.update_destinations(sample_destinations)
            # Should add 2 enabled destinations
            assert mock_instance.add.call_count == 2

    @patch('apprise.Apprise')
    def test_send_message_no_servers(self, mock_apprise):
        """Test sending message with no configured servers."""
        mock_instance = Mock()
        mock_instance.servers = []
        mock_apprise.return_value = mock_instance
        
        notifier = Notifier()
        # Should not raise an exception
        notifier.send_message("Test message")

    @patch('apprise.Apprise')
    def test_send_message_success(self, mock_apprise):
        """Test sending message successfully."""
        mock_server = Mock()
        mock_server.tags = {'Test1'}
        mock_server.url = Mock(return_value="apprise://test1")
        mock_server.service_name = "Test1"
        mock_server.body_maxlen = 1000
        
        mock_instance = Mock()
        mock_instance.servers = [mock_server]
        mock_instance.add = Mock()
        mock_apprise.return_value = mock_instance
        
        notifier = Notifier([{"name": "Test1", "url": "apprise://test1", "enabled": True}])
        
        # Mock the temporary apprise instances created in send_message
        with patch('apprise.Apprise') as mock_temp_apprise:
            mock_temp_instance = Mock()
            mock_temp_instance.add = Mock()
            mock_temp_instance.notify = Mock(return_value=True)
            mock_temp_apprise.return_value = mock_temp_instance
            
            notifier.send_message("Test message", "Test Title")
            
            # Should have called notify
            assert mock_temp_instance.notify.call_count >= 1

    @patch('apprise.Apprise')
    def test_send_message_with_destination_names(self, mock_apprise):
        """Test sending message to specific destinations."""
        mock_server1 = Mock()
        mock_server1.tags = {'Test1'}
        mock_server1.url = Mock(return_value="apprise://test1")
        mock_server1.service_name = "Test1"
        
        mock_server2 = Mock()
        mock_server2.tags = {'Test2'}
        mock_server2.url = Mock(return_value="apprise://test2")
        mock_server2.service_name = "Test2"
        
        mock_instance = Mock()
        mock_instance.servers = [mock_server1, mock_server2]
        mock_apprise.return_value = mock_instance
        
        notifier = Notifier()
        notifier.apprise.servers = [mock_server1, mock_server2]
        
        # Should only send to Test1
        with patch('apprise.Apprise') as mock_temp:
            mock_temp_instance = Mock()
            mock_temp_instance.notify.return_value = True
            mock_temp.return_value = mock_temp_instance
            
            notifier.send_message("Test message", destination_names=["Test1"])

    @patch('apprise.Apprise')
    def test_send_message_chunking(self, mock_apprise):
        """Test sending message with chunking for length limits."""
        mock_server = Mock()
        mock_server.tags = {'Test1'}
        mock_server.url = Mock(return_value="apprise://test1")
        mock_server.service_name = "Test1"
        mock_server.body_maxlen = 150  # Set limit that allows chunking but not too small
        
        mock_instance = Mock()
        mock_instance.servers = [mock_server]
        mock_instance.add = Mock()
        mock_apprise.return_value = mock_instance
        
        long_message = "A" * 300  # Long message that needs chunking
        
        notifier = Notifier([{"name": "Test1", "url": "apprise://test1", "enabled": True}])
        
        # Mock the temporary apprise instances created in send_message
        with patch('apprise.Apprise') as mock_temp_apprise:
            mock_temp_instance = Mock()
            mock_temp_instance.add = Mock()
            mock_temp_instance.notify = Mock(return_value=True)
            mock_temp_apprise.return_value = mock_temp_instance
            
            notifier.send_message(long_message, "Test Title")
            
            # Should have called notify multiple times for chunks
            assert mock_temp_instance.notify.call_count > 1

    @patch('apprise.Apprise')
    def test_send_message_no_matching_tags(self, mock_apprise):
        """Test sending message when no servers match the specified tags."""
        mock_server = Mock()
        mock_server.tags = {'Test1'}
        
        mock_instance = Mock()
        mock_instance.servers = [mock_server]
        mock_apprise.return_value = mock_instance
        
        notifier = Notifier()
        notifier.apprise.servers = [mock_server]
        
        # Should not raise an exception
        notifier.send_message("Test message", destination_names=["NonExistent"])

    @patch('apprise.Apprise')
    def test_send_message_exception_handling(self, mock_apprise):
        """Test that exceptions during sending are handled gracefully."""
        mock_server = Mock()
        mock_server.tags = {'Test1'}
        mock_server.url = Mock(side_effect=Exception("Test error"))
        mock_server.service_name = "Test1"
        
        mock_instance = Mock()
        mock_instance.servers = [mock_server]
        mock_apprise.return_value = mock_instance
        
        notifier = Notifier()
        notifier.apprise.servers = [mock_server]
        
        # Should not raise an exception
        notifier.send_message("Test message")
