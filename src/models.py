from typing import Union


def model(
    weight: Union[int, float],
    hight: Union[int, float],
    val: Union[int, float]
    ) -> Union[int, float]:
    return weight * hight + val