import pytest

from singleton_base import SingletonWrap


def test_singleton_wrapper_basic():
    class MyClass:
        def __init__(self, value: int) -> None:
            self.value = value

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass, 42)

    instance1: MyClass = singleton.get()
    instance2: MyClass = singleton.get()

    assert instance1 is instance2
    assert instance1.value == 42
    assert singleton.has_instance()

    singleton.reset_instance()
    print(singleton.has_instance())

    assert not singleton.has_instance()

    instance3: MyClass = singleton.get()
    assert instance3 is not instance1
    assert instance3.value == 42


def test_singleton_wrapper_with_kwargs():
    class MyClass:
        def __init__(self, value: int, name: str = "default") -> None:
            self.value = value
            self.name = name

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass, 100, name="test")

    instance1: MyClass = singleton.get()
    instance2: MyClass = singleton.get()

    assert instance1 is instance2
    assert instance1.value == 100
    assert instance1.name == "test"
    assert singleton.has_instance()


def test_singleton_wrapper_exception_handling():
    class MyClass:
        def __init__(self, value: int) -> None:
            if value < 0:
                raise ValueError("Value must be non-negative")
            self.value = value

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass, -1)

    with pytest.raises(RuntimeError) as exc_info:
        singleton.get()
    assert "Failed to create singleton instance" in str(exc_info.value)

    assert not singleton.has_instance()

    singleton = SingletonWrap(MyClass, 10)
    instance = singleton.get()
    assert instance.value == 10
    assert singleton.has_instance()


def test_singleton_wrapper_thread_safety():
    import threading  # noqa: PLC0415

    class MyClass:
        def __init__(self, value: int) -> None:
            self.value = value

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass, 50)
    instances = []

    def access_singleton() -> None:
        instance = singleton.get()
        instances.append(instance)

    threads = [threading.Thread(target=access_singleton) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    first_instance = instances[0]
    for instance in instances:
        assert instance is first_instance
    assert singleton.has_instance()


def test_singleton_wrapper_no_args():
    class MyClass:
        def __init__(self) -> None:
            self.value = 99

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass)

    instance1: MyClass = singleton.get()
    instance2: MyClass = singleton.get()
    assert instance1 is instance2
    assert instance1.value == 99
    assert singleton.has_instance()
    singleton.reset_instance()
    assert not singleton.has_instance()
    instance3: MyClass = singleton.get()
    assert instance3 is not instance1
    assert instance3.value == 99
    assert singleton.has_instance()


def test_singleton_wrapper_multiple_resets():
    class MyClass:
        def __init__(self, value: int) -> None:
            self.value = value

    singleton: SingletonWrap[MyClass] = SingletonWrap(MyClass, 10)

    instance1: MyClass = singleton.get()
    assert instance1.value == 10
    assert singleton.has_instance()

    singleton.reset_instance()
    assert not singleton.has_instance()

    instance2: MyClass = singleton.get()
    assert instance2 is not instance1
    assert instance2.value == 10
    assert singleton.has_instance()

    singleton.reset_instance()
    assert not singleton.has_instance()

    instance3: MyClass = singleton.get()
    assert instance3 is not instance2
    assert instance3.value == 10
    assert singleton.has_instance()
