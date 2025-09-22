from typing import Any, Generic, Optional, TypeAlias, TypeVar

from pydantic import BaseModel, Field

AllowedTypes: TypeAlias = str | list | int | dict

T = TypeVar('T')


class DefaultState(BaseModel, Generic[T]):
    """
    Дефолтный ответ вообще для всех существующих методов

    Attributes:
        result (bool): Общий результат выполнения действия
        status (str | bool): Короткое воплощение details
        details (str): Текстовое сообщение об ошибке
        data (Any): Любые данные, которые должны вернуться
    """

    result: Optional[bool] = Field(default=False)
    status: Optional[AllowedTypes] = Field(default='INIT')
    detail: Optional[AllowedTypes] = Field(default='')
    data: Optional[T] = None

    model_config = {
        "use_enum_values": True,
        "arbitrary_types_allowed": True,
    }

    # class Config:
    #     use_enum_values = True  # Для сериализации enum в строки
    #     arbitrary_types_allowed = True

    def __init__(self, init_data: Optional[dict] = None, **kwargs):
        """
        Поддерживает инициализацию:
        - Из словаря: DefaultState({'result': True, ...})
        - Из ключевых аргументов: DefaultState(result=True, ...)
        - Пустую инициализацию: DefaultState()
        """
        if init_data and isinstance(init_data, dict):
            processed_data = {
                'result': init_data.get('result', False),
                'status': init_data.get('status', 'INIT'),
                'detail': init_data.get('detail', ''),
                'data': init_data.get('data')
            }
            super().__init__(**processed_data, **kwargs)
        else:
            super().__init__(**kwargs)

    def __bool__(self) -> bool:
        """Позволяет использовать объект в булевом контексте (if/not)"""
        return self.result is True

    def update(
        self: 'DefaultState[T]',
        *,
        result: bool = False,
        status: Optional[AllowedTypes] = None,
        detail: Optional[AllowedTypes] = None,
        data: Optional[T] = None
    ) -> 'DefaultState[T]':
        """Обновляет данные стейта"""
        if result is not None:
            self.result = result
        if status is not None:
            self.status = status
        if detail is not None:
            self.detail = detail
        if data is not None:
            self.data = data
        return self

    def success(
        self: 'DefaultState[T]',
        *,
        status: Optional[AllowedTypes] = None,
        detail: Optional[AllowedTypes] = None,
        data: Optional[T] = None
    ) -> 'DefaultState[T]':
        """Обновляет данные стейта"""
        self.result = True
        if status is not None:
            self.status = status
        if detail is not None:
            self.detail = detail
        if data is not None:
            self.data = data
        return self
