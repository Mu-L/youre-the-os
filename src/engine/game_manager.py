import asyncio
from typing import Union

import pygame

from engine.game_event import GameEvent
from engine.game_event_type import GameEventType
from engine.scene import Scene
from engine.scene_manager import SceneManager
from engine.window_config import WindowConfig


_LEFT_MOUSE_BUTTON = 1

class GameManager():
    window_config: WindowConfig
    fps = 60

    @property
    def startup_scene(self):
        return self._startup_scene

    @startup_scene.setter
    def startup_scene(self, value : Union[Scene, str]):
        if isinstance(value, str) and self._scene_manager.get_scene(value) is None:
            scene = self._scene_manager.get_scene(value)
            if scene is None:
                raise ValueError(f'Scene not found: {value}')
        else:
            scene = value
        self._startup_scene = scene

    def __init__(self):
        self._current_scene = None
        self._scenes = None
        self._screen = None
        self._scene_manager = SceneManager()
        self._startup_scene = None

        self._mouse_down = False
        self._shift_down = False

    @property
    def current_scene(self):
        return self._current_scene

    def _init_pygame(self):
        pygame.init()
        pygame.font.init()

    def _init_screen(self):
        if self.window_config is None:
            raise ValueError('Property `window_config` needs to be set.')
        self._screen = pygame.display.set_mode(self.window_config.size)
        icon = pygame.image.load(self.window_config.icon_path)
        pygame.display.set_caption(self.window_config.title)
        pygame.display.set_icon(icon)
        self._scene_manager.screen = self._screen

    def register_scene(self, scene: Scene):
        self._scene_manager.register_scene(scene)

    def _get_events(self):
        events = []
        mouse_event_added = False
        mouse_motion_event = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(GameEvent(GameEventType.QUIT, {}))
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key).endswith('shift'):
                    self._shift_down = True
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key).endswith('shift'):
                    self._shift_down = False
                events.append(
                    GameEvent(
                        GameEventType.KEY_UP, {
                            'key': pygame.key.name(
                                event.key), 'shift': self._shift_down}))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == _LEFT_MOUSE_BUTTON:
                self._mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == _LEFT_MOUSE_BUTTON:
                self._mouse_down = False
                if mouse_event_added and mouse_motion_event:
                    events.remove(mouse_motion_event)
                    mouse_event_added = False
                    mouse_motion_event = None
                if not mouse_event_added:
                    events.append(
                        GameEvent(
                            GameEventType.MOUSE_LEFT_CLICK, {
                                'position': event.pos, 'shift': self._shift_down }))
                    mouse_event_added = True
            elif event.type == pygame.MOUSEMOTION and not mouse_event_added:
                game_event = GameEvent(GameEventType.MOUSE_MOTION,
                                  {'position': event.pos,
                                   'left_button_down': self._mouse_down,
                                   'shift': self._shift_down})
                events.append(game_event)
                mouse_event_added = True
                mouse_motion_event = game_event
        return events

    async def _main_loop(self, ignore_events=False):
        clock = pygame.time.Clock()

        while True:
            events = self._get_events()
            for event in events:
                if event.type == GameEventType.QUIT:
                    return

            if ignore_events:
                events = []

            scene = self._scene_manager.current_scene

            scene.update(self._scene_manager.current_scene.current_time, events)
            if scene != self._scene_manager.current_scene:
                scene = self._scene_manager.current_scene
                self._scene_manager.current_scene.update(
                    self._scene_manager.current_scene.current_time, []
                )

            scene.render()

            clock.tick(self.fps)

            await asyncio.sleep(0)

    async def play(self, ignore_events=False):
        self._init_pygame()
        self._init_screen()
        if self.startup_scene is None:
            raise ValueError('Property `startup_scene` needs to be set.')
        self._scene_manager.start_scene(self.startup_scene)
        await self._main_loop(ignore_events)
