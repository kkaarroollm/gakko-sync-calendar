from unittest.mock import MagicMock, patch

from pydantic import HttpUrl

from src.core import CommandContext, GakkoConfig


def test_context_creates_driver_from_config_when_none():
    mock_driver = MagicMock()
    config = GakkoConfig(base_url=HttpUrl("https://test.local"))

    with patch("src.core.command_context._create_driver_from_config", return_value=mock_driver) as mock_factory:
        ctx = CommandContext(config=config)

    mock_factory.assert_called_once_with(config)
    assert ctx.driver is mock_driver


def test_context_uses_provided_driver():
    mock_driver = MagicMock()
    ctx = CommandContext(driver=mock_driver)
    assert ctx.driver is mock_driver


def test_current_url_delegates_to_driver():
    mock_driver = MagicMock()
    mock_driver.current_url = "https://example.com/page"
    ctx = CommandContext(driver=mock_driver)
    assert ctx.current_url == "https://example.com/page"


def test_page_source_delegates_to_driver():
    mock_driver = MagicMock()
    mock_driver.page_source = "<html>test</html>"
    ctx = CommandContext(driver=mock_driver)
    assert ctx.page_source == "<html>test</html>"


def test_quit_calls_driver_quit():
    mock_driver = MagicMock()
    ctx = CommandContext(driver=mock_driver)
    ctx.quit()
    mock_driver.quit.assert_called_once()


def test_quit_when_driver_is_none():
    mock_driver = MagicMock()
    ctx = CommandContext(driver=mock_driver)
    ctx.driver = None
    ctx.quit()


def test_create_driver_from_config_headless():
    config = GakkoConfig(
        base_url=HttpUrl("https://test.local"),
        chrome_headless=True,
        selenium_implicit_wait=5,
        selenium_page_load_timeout=15,
    )

    with patch("src.core.command_context.Chrome") as mock_chrome_cls:
        mock_driver_instance = MagicMock()
        mock_chrome_cls.return_value = mock_driver_instance

        from src.core.command_context import _create_driver_from_config

        driver = _create_driver_from_config(config)

    mock_chrome_cls.assert_called_once()
    mock_driver_instance.implicitly_wait.assert_called_once_with(5)
    mock_driver_instance.set_page_load_timeout.assert_called_once_with(15)
    assert driver is mock_driver_instance


def test_create_driver_from_config_with_binary_path():
    config = GakkoConfig(
        base_url=HttpUrl("https://test.local"),
        chrome_binary_path="/usr/bin/chromium",
    )

    with patch("src.core.command_context.Chrome") as mock_chrome_cls:
        mock_chrome_cls.return_value = MagicMock()

        from src.core.command_context import _create_driver_from_config

        _create_driver_from_config(config)

    options = mock_chrome_cls.call_args[1]["options"]
    assert options.binary_location == "/usr/bin/chromium"


def test_create_driver_from_config_with_driver_path():
    config = GakkoConfig(
        base_url=HttpUrl("https://test.local"),
        chrome_binary_path="/usr/bin/chromium",
        chrome_driver_path="/usr/bin/chromedriver",
    )

    with patch("src.core.command_context.Chrome") as mock_chrome_cls:
        mock_chrome_cls.return_value = MagicMock()

        from src.core.command_context import _create_driver_from_config

        _create_driver_from_config(config)

    service = mock_chrome_cls.call_args[1]["service"]
    assert service.path == "/usr/bin/chromedriver"
