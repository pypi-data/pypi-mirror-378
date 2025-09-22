import pytest
from sfn_blueprint import RetryLimitExceededError

# Test function for RetryLimitExceededError
def test_retry_limit_exceeded_error():
    # Define the expected error message
    error_message = "Retry limit exceeded"

    # Use pytest.raises to test if the exception is raised
    with pytest.raises(RetryLimitExceededError) as exc_info:
        # Simulate a scenario where the exception is raised
        raise RetryLimitExceededError(error_message)

    # Check if the raised exception contains the correct message
    assert str(exc_info.value) == error_message