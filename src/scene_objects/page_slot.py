from engine.scene_object import SceneObject
from scene_objects.views.page_slot_view import PageSlotView


class PageSlot(SceneObject):
    def __init__(self):
        self._page = None

        super().__init__(PageSlotView())

    @property
    def has_page(self):
        return self._page is not None

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, page):
        self._page = page

    def update(self, current_time, events):
        pass
