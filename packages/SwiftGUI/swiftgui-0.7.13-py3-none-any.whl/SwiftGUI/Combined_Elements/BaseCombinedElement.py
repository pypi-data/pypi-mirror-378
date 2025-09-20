from collections.abc import Iterable, Callable
from typing import Any

from SwiftGUI import BaseElement, SubLayout
from SwiftGUI.ElementFlags import ElementFlag
from SwiftGUI.Widget_Elements.Frame import Frame
from SwiftGUI.Windows import ValueDict

class BaseCombinedElement(BaseElement):
    """
    Derive from this class to create an element consisting of multiple inner elements.
    """
    def __init__(
            self,
            frame,
            key: Any = None,
            key_function: Callable | Iterable[Callable] = None,
            apply_parent_background_color: bool = True,
            disable_key_collection: bool = False,
    ):
        """

        :param frame: Pass a Frame containing all the elements you'd like to have inside this element
        :param key: Pass a key to register it in main window
        :param apply_parent_background_color: True, if the background_color of the parent container should also apply to this frame
        :param disable_key_collection: True, if keys should be passed up to the main event loop instead of .event_loop
        """
        super().__init__()

        if disable_key_collection:
            self._sg_widget = frame
        else:
            self._sg_widget = SubLayout(frame, self._event_loop)

        self.key = key
        self._key_function = key_function

        self._throw_event: Callable = lambda :None

        if apply_parent_background_color:
            self.add_flags(ElementFlag.APPLY_PARENT_BACKGROUND_COLOR)

    def _event_loop(self, e: Any, v: ValueDict):
        """
        All key-events will call this method.
        You can use it exactly like your normal event-loop.

        :param e: Contains the element-key
        :param v: Contains all values
        :return:
        """
        ...

    def throw_event(self):
        """
        Throw the default event to the window
        :return:
        """
        self._throw_event()

    def _personal_init(self):
        self._sg_widget._init(self, self.window)
        self._throw_event = self.window.get_event_function(me= self, key= self.key, key_function= self._key_function)

    def _update_special_key(self,key:str,new_val:Any) -> bool|None:
        """
        Inherit (use) this method to pick out "special" keys to update.
        Keys are passed one-by-one.

        When calling .update, this method gets called first.
        If it returns anything truethy, execution of .update ends for this key.

        Otherwise, ._update_default_keys gets called for the key.

        Just copy the whole method and add more cases.

        :param key:
        :param new_val:
        :return:
        """
        match key:
            case "background_color":
                self._sg_widget._update_initial(background_color=new_val)
            case _:
                # The key wasn't found in any other case
                return super()._update_special_key(key, new_val)    # Look in the parent-class

        # The key was found in match-case
        return True

    @property
    def w(self):
        if isinstance(self._sg_widget, Frame):
            raise AttributeError("You tried to get .w from a combined element that does not have a sub-layout.\nUse ._sg_widget instead.")

        return self._sg_widget

    def _get_value(self) -> Any:
        if isinstance(self._sg_widget, Frame):
            return None

        return self._sg_widget.value


