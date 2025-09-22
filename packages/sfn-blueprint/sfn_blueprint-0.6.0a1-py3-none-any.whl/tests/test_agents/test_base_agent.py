import pytest
from unittest.mock import MagicMock
from sfn_blueprint import SFNAgent

# 1. Test that calling execute_task raises NotImplementedError
def test_sfnagent_raises_not_implemented_error():
    agent = SFNAgent(name="Test Agent", role="Tester")
    task = MagicMock()

    with pytest.raises(NotImplementedError, match="Subclasses must implement execute_task method"):
        agent.execute_task(task)

# 2. Test for a subclass of SFNAgent that implements execute_task
class MyAgent(SFNAgent):
    def execute_task(self, task):
        return {"result": "task executed"}

def test_myagent_executes_task():
    agent = MyAgent(name="My Agent", role="Executor")
    task = MagicMock()

    result = agent.execute_task(task)
    assert result == {"result": "task executed"}  # Ensure the method returns the expected result
