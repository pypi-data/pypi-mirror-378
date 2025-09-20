# shadowstep/element/dom.py
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, cast

from selenium.common import (
    InvalidSessionIdException,
    NoSuchDriverException,
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.types import WaitExcTypes
from selenium.webdriver.support import expected_conditions as expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from shadowstep.decorators.decorators import log_debug
from shadowstep.element.utilities import ElementUtilities
from shadowstep.exceptions.shadowstep_exceptions import (
    ShadowstepElementException,
    ShadowstepResolvingLocatorError,
)
from shadowstep.locator.types.shadowstep_dict import ShadowstepDictAttribute

if TYPE_CHECKING:
    from shadowstep.element.element import Element
    from shadowstep.locator import LocatorConverter, UiSelector
    from shadowstep.shadowstep import Shadowstep


class ElementDOM:
    def __init__(self, element: Element):
        self.logger = logging.getLogger(__name__)
        self.element: Element = element
        self.shadowstep: Shadowstep = element.shadowstep
        self.converter: LocatorConverter = element.converter
        self.utilities: ElementUtilities = element.utilities

    @log_debug()
    def get_element(self,
                    locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    timeout: int = 30,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> Element:
        from shadowstep.element.element import Element
        resolved_locator = None
        if isinstance(locator, Element):
            locator = locator.locator

        parent_locator = self.utilities.remove_null_value(self.element.locator)
        child_locator = self.utilities.remove_null_value(locator)

        if not parent_locator:
            raise ShadowstepResolvingLocatorError("Failed to resolve parent locator")
        if not child_locator:
            raise ShadowstepResolvingLocatorError("Failed to resolve child locator")

        if isinstance(parent_locator, tuple):
            child_locator = self.converter.to_xpath(child_locator)
            inner_path = child_locator[1].lstrip("/")  # Remove accidental `/` in front

            # Guaranteed nesting: parent//child
            if not inner_path.startswith("//"):
                inner_path = f"//{inner_path}"

            resolved_locator = ("xpath", f"{parent_locator[1]}{inner_path}")
        elif isinstance(parent_locator, dict):
            child_locator = self.converter.to_dict(child_locator)
            resolved_child_locator = {ShadowstepDictAttribute.CHILD_SELECTOR.value: child_locator}
            parent_locator.update(resolved_child_locator)
            resolved_locator = parent_locator

        elif isinstance(parent_locator, UiSelector):
            child_locator = self.converter.to_uiselector(child_locator)
            resolved_locator = parent_locator.childSelector(UiSelector.from_string(child_locator))

        if resolved_locator is None:
            raise ShadowstepResolvingLocatorError("Failed to resolve locator")

        return Element(locator=resolved_locator,
                       shadowstep=self.shadowstep,
                       timeout=timeout,
                       poll_frequency=poll_frequency,
                       ignored_exceptions=ignored_exceptions)

    @log_debug()
    def get_elements(  # noqa: C901
            self,
            locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            timeout: float = 30,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None
    ) -> list[Element]:
        from shadowstep.element.element import Element

        if isinstance(locator, Element):
            locator = locator.locator

        base_xpath = self.utilities.get_xpath()
        if not base_xpath:
            raise ShadowstepElementException("Unable to resolve shadowstep xpath")

        locator = self.utilities.remove_null_value(locator)
        locator = self.converter.to_xpath(locator)

        start_time = time.time()
        while time.time() - start_time < self.element.timeout:
            try:
                self.element.get_driver()
                wait = WebDriverWait(
                    driver=self.element.driver,
                    timeout=timeout,
                    poll_frequency=poll_frequency,
                    ignored_exceptions=ignored_exceptions,
                )
                wait.until(expected_conditions.presence_of_element_located(locator))
                attributes_list = self.utilities.extract_el_attrs_from_source(xpath_expr=locator[1],
                                                                              page_source=self.shadowstep.driver.page_source)
                elements = []
                for attributes in attributes_list:
                    element = Element(
                        locator=cast(dict[str, Any], attributes),
                        shadowstep=self.shadowstep,
                        timeout=timeout,
                        poll_frequency=poll_frequency,
                        ignored_exceptions=ignored_exceptions
                    )
                    elements.append(element)
                return elements
            except (NoSuchDriverException, InvalidSessionIdException) as error:
                self.element.handle_driver_error(error)
            except StaleElementReferenceException as error:
                self.logger.debug(error)
                self.logger.warning("StaleElementReferenceException \n Re-acquire element")
                self.element.native = None
                self.element.get_native()
                continue
            except WebDriverException as error:
                err_msg = str(error).lower()
                if "instrumentation process is not running" in err_msg or "socket hang up" in err_msg:
                    self.element.handle_driver_error(error)
                    continue
                raise error
        return []

    @log_debug()
    def get_parent(self,
                   timeout: float = 30.0,
                   poll_frequency: float = 0.5,
                   ignored_exceptions: WaitExcTypes | None = None) -> Element:
        from shadowstep.element.element import Element
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        xpath = self.converter.to_xpath(clean_locator)
        xpath = (xpath[0], xpath[1] + "/..")
        return Element(locator=xpath,
                       shadowstep=self.shadowstep,
                       timeout=timeout,
                       poll_frequency=poll_frequency,
                       ignored_exceptions=ignored_exceptions)

    @log_debug()
    def get_parents(self,
                    timeout: float = 30.0,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        xpath = self.converter.to_xpath(clean_locator)
        xpath = (xpath[0], xpath[1] + "/ancestor::*")
        parents = self.get_elements(xpath, timeout, poll_frequency, ignored_exceptions)
        if parents and parents[0].locator.get("class") == "hierarchy":  # type: ignore
            parents.pop(0)
        return parents

    @log_debug()
    def get_sibling(self,
                    locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    timeout: float = 30.0,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> Element:
        from shadowstep.element.element import Element
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        base_xpath = self.converter.to_xpath(clean_locator)[1]
        sibling_locator = self.utilities.remove_null_value(locator)
        sibling_xpath = self.converter.to_xpath(sibling_locator)
        sibling_path = sibling_xpath[1].lstrip("/")
        xpath = f"{base_xpath}/following-sibling::{sibling_path}[1]"
        return Element(
            locator=("xpath", xpath),
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @log_debug()
    def get_siblings(self,
                     locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                     timeout: float = 30.0,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        clean_locator = self.utilities.remove_null_value(self.element.locator)
        base_xpath = self.converter.to_xpath(clean_locator)[1]
        sibling_locator = self.utilities.remove_null_value(locator)
        sibling_xpath = self.converter.to_xpath(sibling_locator)
        sibling_path = sibling_xpath[1].lstrip("/")
        xpath = f"{base_xpath}/following-sibling::{sibling_path}"
        return self.get_elements(("xpath", xpath), timeout, poll_frequency, ignored_exceptions)

    @log_debug()
    def get_cousin(
            self,
            cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
            depth_to_parent: int = 1,
            timeout: float = 30.0,
            poll_frequency: float = 0.5,
            ignored_exceptions: WaitExcTypes | None = None) -> Element:
        from shadowstep.element.element import Element
        depth_to_parent += 1
        clean_base_locator = self.utilities.remove_null_value(self.element.locator)
        current_xpath = self.converter.to_xpath(clean_base_locator)[1]
        up_xpath = "/".join([".."] * depth_to_parent)
        base_xpath = f"{current_xpath}/{up_xpath}" if up_xpath else current_xpath

        clean_cousin_locator = self.utilities.remove_null_value(cousin_locator)
        cousin_xpath = self.converter.to_xpath(clean_cousin_locator)[1]

        full_xpath = f"{base_xpath}{cousin_xpath}"
        return Element(
            locator=("xpath", full_xpath),
            shadowstep=self.shadowstep,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    @log_debug()
    def get_cousins(self,
                    cousin_locator: tuple[str, str] | dict[str, Any] | Element | UiSelector,
                    depth_to_parent: int = 1,
                    timeout: float = 30.0,
                    poll_frequency: float = 0.5,
                    ignored_exceptions: WaitExcTypes | None = None) -> list[Element]:
        depth_to_parent += 1
        clean_base_locator = self.utilities.remove_null_value(self.element.locator)
        current_xpath = self.converter.to_xpath(clean_base_locator)[1]
        up_xpath = "/".join([".."] * depth_to_parent)
        base_xpath = f"{current_xpath}/{up_xpath}" if up_xpath else current_xpath

        clean_cousin_locator = self.utilities.remove_null_value(cousin_locator)
        cousin_xpath = self.converter.to_xpath(clean_cousin_locator)[1]

        full_xpath = f"{base_xpath}{cousin_xpath}"
        return self.get_elements(("xpath", full_xpath), timeout, poll_frequency, ignored_exceptions)
