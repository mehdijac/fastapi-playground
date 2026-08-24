import os


def pytest_configure(config):
    os.environ["NEWS_AGENT_ENABLE_OBSERVABILITY"] = "false"
