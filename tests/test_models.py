from src.models import model
import pytest

@pytest.mark.parametrize(
    "weight, hight, bias, expected",
    [
        (1,2,3,4),
        (-1,2,-3,4),
        (1,-2,3,-4),
        (0,0,0,0),
    ]
)

def test_model(weight, hight, bias, expected):
    assert model(weight, hight, bias) == expected