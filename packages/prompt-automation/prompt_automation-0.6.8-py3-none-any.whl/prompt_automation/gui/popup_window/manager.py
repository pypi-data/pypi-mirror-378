"""Popup window lifecycle management for digit shortcuts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ...errorlog import get_logger
from ..single_window.frames import collect, review
from ..selector.view.exclusions import edit_exclusions as exclusions_dialog
from ...services import exclusions as exclusions_service


_log = get_logger(__name__)


@dataclass
class PopupDimensions:
    width: int
    height: int
    x: int
    y: int


class PopupGeometry:
    """Calculate responsive popup window sizes."""

    def __init__(self, baseline_ratio: float = 0.6, min_width: int = 720, min_height: int = 540):
        self.baseline_ratio = baseline_ratio
        self.min_width = min_width
        self.min_height = min_height

    def calculate(self, screen_width: int, screen_height: int) -> PopupDimensions:
        width = max(int(screen_width * self.baseline_ratio), self.min_width)
        height = max(int(screen_height * self.baseline_ratio), self.min_height)
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 3, 0)
        return PopupDimensions(width=width, height=height, x=x, y=y)


class PopupManager:
    """Spawn and track popup windows with a headless-friendly API."""

    _SENTINEL = object()

    def __init__(self, tk_module: Optional[Any] = None, owner: Optional[Any] = None) -> None:
        self.geometry = PopupGeometry()
        self._windows: List[_BasePopup] = []
        self._default_owner = owner
        if tk_module is not None:
            tk = tk_module
        else:
            try:
                import tkinter as tk  # type: ignore
            except Exception:  # pragma: no cover - optional GUI
                tk = None  # type: ignore[assignment]
        self._tk = tk

    @property
    def active_count(self) -> int:
        return len(self._windows)

    def open_template(self, template: Dict[str, Any], *, owner: Any = _SENTINEL) -> Any:
        if self._tk is None:
            view = _StubPopup(self, template)
            self._windows.append(view)
            return view

        tk = self._tk
        assert tk is not None
        target_owner = self._default_owner if owner is self._SENTINEL else owner
        try:
            if target_owner is None:
                window = tk.Tk()
            else:
                window = tk.Toplevel(target_owner)
        except Exception:
            # Fallback to headless stub when display is unavailable
            self._tk = None
            view = _StubPopup(self, template)
            self._windows.append(view)
            return view

        try:
            popup = _TkPopup(self, tk, window, template, owner=target_owner)
        except Exception as exc:  # pragma: no cover - defensive
            try:
                window.destroy()
            except Exception:
                pass
            self._tk = None
            try:
                _log.error("popup.spawn_failed error=%s", exc)
            except Exception:
                pass
            view = _StubPopup(self, template)
            self._windows.append(view)
            return view

        self._windows.append(popup)
        return popup

    def register_close(self, popup: "_BasePopup") -> None:
        if popup in self._windows:
            self._windows.remove(popup)

    def close_all(self) -> None:
        for popup in list(self._windows):
            popup.close()
        self._windows.clear()


class _BasePopup:
    def __init__(self, manager: PopupManager, template: Dict[str, Any]):
        self._manager = manager
        self.template = template

    def close(self) -> None:  # pragma: no cover - subclasses override
        raise NotImplementedError


class _StubPopup(_BasePopup):
    def close(self) -> None:
        self._manager.register_close(self)


class _TkPopup(_BasePopup):  # pragma: no cover - GUI runtime
    def __init__(self, manager: PopupManager, tk_mod: Any, window: Any, template: Dict[str, Any], owner: Any):
        super().__init__(manager, template)
        self._tk = tk_mod
        self.root = window
        self._owner = owner
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.final_text: Optional[str] = None
        self.variables: Optional[Dict[str, Any]] = None
        self._stage: Optional[str] = None
        self._reminders_expanded: Optional[bool] = None
        self._closed = False
        self._grabbed = False
        self._configure_window()
        self._show_collect()

    # --- Stage orchestration -------------------------------------------------
    def _configure_window(self) -> None:
        try:
            title = self.template.get("title") or "Prompt"
            self.root.title(title)
        except Exception:
            pass
        try:
            screen_w = self.root.winfo_screenwidth()
            screen_h = self.root.winfo_screenheight()
            geom = self._manager.geometry.calculate(screen_w, screen_h)
            self.root.geometry(f"{geom.width}x{geom.height}+{geom.x}+{geom.y}")
            self.root.minsize(self._manager.geometry.min_width, self._manager.geometry.min_height)
        except Exception:
            pass
        try:
            if self._owner is not None and hasattr(self.root, "transient"):
                self.root.transient(self._owner)
        except Exception:
            pass
        for attr, args in (
            ("lift", ()),
            ("focus_force", ()),
        ):
            try:
                getattr(self.root, attr)(*args)
            except Exception:
                pass
        self._enforce_modal_focus()

    def _clear_content(self) -> None:
        children = []
        try:
            children = list(getattr(self.root, "children", {}).values())
        except Exception:
            try:
                children = list(self.root.winfo_children())
            except Exception:
                children = []
        for child in children:
            try:
                child.destroy()
            except Exception:
                pass

    def _unbind_stage_shortcuts(self) -> None:
        for seq in (
            "<Control-Return>",
            "<Control-KP_Enter>",
            "<KP_Enter>",
            "<Escape>",
            "<Control-Shift-c>",
        ):
            try:
                self.root.unbind(seq)
            except Exception:
                pass

    def _show_collect(self) -> None:
        self._unbind_stage_shortcuts()
        self._clear_content()
        self._stage = "collect"
        try:
            collect.build(self, self.template)
        except Exception as exc:
            try:
                _log.error("popup.collect_failed error=%s", exc)
            except Exception:
                pass
            self.close()
            return
        self._enforce_modal_focus()
        self._focus_first_entry_async()

    def advance_to_review(self, variables: Dict[str, Any]) -> None:
        if variables is None:
            self.cancel()
            return
        self.variables = variables
        self._unbind_stage_shortcuts()
        self._clear_content()
        self._stage = "review"
        try:
            review.build(self, self.template, variables)
        except Exception as exc:
            try:
                _log.error("popup.review_failed error=%s", exc)
            except Exception:
                pass
            self.close()
            return
        self._enforce_modal_focus()
        self._focus_first_entry_async()

    def back_to_select(self) -> None:
        self.cancel()

    def edit_exclusions(self, template_id: int) -> None:
        try:
            try:
                exclusions_dialog(self.root, exclusions_service, template_id)
            except TypeError:
                exclusions_dialog(self.root, exclusions_service)  # type: ignore[misc]
        except Exception as exc:
            try:
                _log.error("popup.exclusions_failed error=%s", exc)
            except Exception:
                pass

    def finish(self, final_text: str) -> None:
        self.final_text = final_text
        self.close()

    def cancel(self) -> None:
        self.final_text = None
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._unbind_stage_shortcuts()
        except Exception:
            pass
        if self._grabbed:
            try:
                self.root.grab_release()
            except Exception:
                pass
        self._drop_topmost()
        try:
            self.root.destroy()
        except Exception:
            pass
        self._manager.register_close(self)

    def _enforce_modal_focus(self) -> None:
        try:
            self.root.focus_force()
        except Exception:
            pass
        try:
            if hasattr(self.root, "attributes"):
                self.root.attributes('-topmost', True)
                self.root.after(200, lambda: self._drop_topmost())
        except Exception:
            pass
        if self._owner is not None:
            try:
                if hasattr(self.root, "grab_set"):
                    self.root.grab_set()
                    self._grabbed = True
            except Exception:
                self._grabbed = False
        else:
            self._grabbed = False

    def _drop_topmost(self) -> None:
        if self._closed:
            return
        try:
            if hasattr(self.root, "attributes"):
                self.root.attributes('-topmost', False)
        except Exception:
            pass

    def _focus_first_entry_async(self) -> None:
        def _attempt() -> None:
            if self._closed:
                return
            if not self._focus_first_entry():
                try:
                    self.root.after(50, _attempt)
                except Exception:
                    pass

        try:
            self.root.after(10, _attempt)
        except Exception:
            _attempt()

    def _focus_first_entry(self) -> bool:
        widgets: list[Any] = []
        try:
            widgets = list(getattr(self.root, "children", {}).values())
        except Exception:
            try:
                widgets = list(self.root.winfo_children())
            except Exception:
                widgets = []

        def _focus_in(widget: Any) -> bool:
            try:
                klass = getattr(widget, "winfo_class", lambda: "")()
                if klass in {"Entry", "Text"} and hasattr(widget, "focus_set"):
                    if hasattr(widget, "see"):
                        try:
                            widget.see("end")
                        except Exception:
                            pass
                    if hasattr(widget, "schedule_focus"):
                        try:
                            widget.schedule_focus(widget.focus_set)
                            return True
                        except Exception:
                            pass
                    widget.focus_set()
                    return True
            except Exception:
                return False
            return False

        for widget in reversed(widgets):
            if _focus_in(widget):
                return True
            try:
                children = list(getattr(widget, "children", {}).values())
            except Exception:
                try:
                    children = list(widget.winfo_children())
                except Exception:
                    children = []
            for child in reversed(children):
                if _focus_in(child):
                    return True
        return False


__all__ = ["PopupManager", "PopupGeometry", "PopupDimensions"]
