import enum
from functools import lru_cache
from typing import Optional

from fred.dao.comp.interface import ComponentInterface
from fred.dao.comp._queue import FredQueue
from fred.dao.comp._keyval import FredKeyVal


class _PreconfCatalogMixin:
    """A mixin class to allow enum members to be called directly to create instances
    of preconfigured components.
    This mixin is used in conjunction with the `preconf` class method of the `CompCatalog`
    enum to create a new enum with preconfigured components for a specific service."""

    def __call__(self, *args, **kwargs) -> ComponentInterface:
        """Create an instance of the preconfigured component. This method
        allows the enum member to be called directly to instantiate the component
        with any additional arguments.
        Args:
            *args: Positional arguments to pass to the component constructor.
            **kwargs: Keyword arguments to pass to the component constructor.
        Returns:
            ComponentInterface: An instance of the preconfigured component.
        """
        return self.value(*args, **kwargs)


class CompCatalog(enum.Enum):
    """An enumeration of available component types.
    Each enum member corresponds to a specific component class that implements
    the `ComponentInterface`. This enum provides a way to reference and create
    instances of different component types in a standardized manner.
    """
    QUEUE = FredQueue
    KEYVAL = FredKeyVal

    @classmethod
    def from_classname(cls, classname: str) -> "CompCatalog":
        """Get enum member by component class name.
        Args:
            classname (str): The class name of the component.
        Returns:
            CompCatalog: The corresponding enum member.
        Raises:
            ValueError: If no matching component is found.
        """
        for item in cls:
            if item.value.__name__ == classname:
                return item
        raise ValueError(f"No component found for classname: {classname}")

    @classmethod
    @lru_cache(maxsize=None)  # TODO: Consider cache invalidation strategy if needed
    def preconf(cls, srv_name: str, **kwargs) -> enum.Enum:
        """Create a new Enum with preconfigured components for a specific service name.
        Args:
            srv_name (str): The service name to preconfigure the components with.
            **kwargs: Additional keyword arguments to pass to the component constructors.
        Returns:
            enum.Enum: A new Enum class with preconfigured components.
        """
        return enum.Enum(
            f"{srv_name.title()}{cls.__name__}",
            {item.name: item.value.mount(srv_name=srv_name, **kwargs) for item in cls},
            type=_PreconfCatalogMixin,
        )

    def component_cls(self) -> type[ComponentInterface]:
        """Returns the class of the component associated with the enum member.
        Returns:
            type[ComponentInterface]: The class of the component.
        """
        return self.value

    def auto(self, srv_name: Optional[str] = None, **kwargs) -> ComponentInterface:
        """Automatically creates an instance of the component, mounting it to a service.
        This method is a convenience wrapper that first mounts the component to a service
        and then creates an instance of the component.
        Args:
            srv_name (Optional[str]): The name of the service to mount. Defaults to None.
            **kwargs: Additional keyword arguments for both mounting the service and
                      creating the component instance. If there are specific arguments
                      for the service, they should be passed under the key `srv_kwargs`
                      as a dictionary.
        Returns:
            ComponentInterface: An instance of the component.
        """
        return self.value.auto(srv_name=srv_name, **kwargs)
