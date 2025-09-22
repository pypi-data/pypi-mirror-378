#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.24 23:00:00                  #
# ================================================== #

import re

from PySide6.QtCore import Qt, QObject, Signal, Slot, QEvent
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu

from pygpt_net.item.ctx import CtxMeta
from pygpt_net.core.text.web_finder import WebFinder
from pygpt_net.utils import trans


class HtmlOutput(QWebEngineView):
    def __init__(self, window=None):
        """
        HTML output (Webkit)

        :param window: main window
        """
        super(HtmlOutput, self).__init__(window)
        self.window = window
        self.finder = WebFinder(window, self)
        self.loadFinished.connect(self.on_page_loaded)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.signals = WebEngineSignals()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.plain = ""
        self.html_content = ""
        self.meta = None
        self.tab = None
        self.installEventFilter(self)

    def on_delete(self):
        """Clean up on delete"""
        if self.finder:
            self.finder.disconnect()  # disconnect finder
            self.finder = None  # delete finder

        self.tab = None  # clear tab reference

        # delete page
        page = self.page()
        if page:
            if hasattr(page, 'bridge'):
                page.bridge.deleteLater()
            if hasattr(page, 'channel'):
                page.channel.deleteLater()
            if hasattr(page, 'signals') and page.signals:
                page.signals.deleteLater()
            page.deleteLater()  # delete page

        # disconnect signals
        self.loadFinished.disconnect(self.on_page_loaded)
        self.customContextMenuRequested.disconnect(self.on_context_menu)
        self.signals.save_as.disconnect()
        self.signals.audio_read.disconnect()

        self.deleteLater()  # delete widget

    def set_tab(self, tab):
        """
        Set tab

        :param tab: Tab
        """
        self.tab = tab

    def set_meta(self, meta: CtxMeta):
        """
        Assign ctx meta

        :param meta: context meta
        """
        self.meta = meta

    def set_plaintext(self, text: str):
        """
        Set plain text

        :param text: text
        """
        self.plain = text

    def set_html_content(self, html: str):
        """
        Set HTML content

        :param html: HTML content
        """
        self.html_content = html

        # set page HTML
        self.setHtml(html, baseUrl="file://")

    def get_html_content(self) -> str:
        """
        Get HTML content

        :return: HTML content
        """
        return self.html_content

    def on_context_menu(self, position):
        """
        Context menu event

        :param position: position
        """
        menu = QMenu(self)
        selected_text = ""
        is_selection = self.page().hasSelection()
        if is_selection:
            selected_text = self.get_selected_text()

        if is_selection:
            # copy
            action = QAction(QIcon(":/icons/copy.svg"), trans('action.copy'), self)
            action.triggered.connect(self.copy_selected_text)
            menu.addAction(action)

            # audio read
            action = QAction(QIcon(":/icons/volume.svg"), trans('text.context_menu.audio.read'), self)
            action.triggered.connect(
                lambda: self.signals.audio_read.emit(selected_text)
            )
            menu.addAction(action)

            # copy to
            copy_to_menu = self.window.ui.context_menu.get_copy_to_menu(menu, selected_text)
            menu.addMenu(copy_to_menu)

            # save as (selected)
            action = QAction(QIcon(":/icons/save.svg"), trans('action.save_selection_as'), self)
            action.triggered.connect(
                lambda: self.signals.save_as.emit(selected_text, 'txt')
            )
            menu.addAction(action)
        else:
            # select all
            action = QAction(QIcon(":/icons/copy.svg"), trans('action.select_all'), self)
            action.triggered.connect(self.select_all_text)
            menu.addAction(action)

            # save as (all) - plain
            action = QAction(QIcon(":/icons/save.svg"), trans('action.save_as') + " (text)", self)
            action.triggered.connect(
                lambda: self.signals.save_as.emit(re.sub(r'\n{2,}', '\n\n', self.plain), 'txt')
            )
            menu.addAction(action)

            # save as (all) - html
            action = QAction(QIcon(":/icons/save.svg"), trans('action.save_as') + " (html)", self)
            action.triggered.connect(
                lambda: self.signals.save_as.emit(re.sub(r'\n{2,}', '\n\n', self.html_content), 'html')
            )
            menu.addAction(action)

        action = QAction(QIcon(":/icons/search.svg"), trans('text.context_menu.find'), self)
        action.triggered.connect(self.find_open)
        # action.setShortcut(QKeySequence("Ctrl+F"))
        menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def update_zoom(self):
        """Update zoom from config"""
        if self.window.core.config.has("zoom"):
            self.page().setZoomFactor(self.window.core.config.get("zoom"))

    def get_zoom_value(self) -> float:
        """
        Get zoom value

        :return: zoom value
        """
        return self.page().zoomFactor()

    def reset_current_content(self):
        """Reset current content"""
        self.plain = ""
        self.html_content = ""

    def update_current_content(self):
        """Update current content"""
        self.page().runJavaScript("document.getElementById('container').outerHTML", 0, self.set_plaintext)
        self.page().runJavaScript("document.documentElement.innerHTML", 0, self.set_html_content)

    def on_page_loaded(self, success):
        """
        On page loaded

        :param success: True if loaded successfully
        """
        pass

    def get_selected_text(self) -> str:
        """
        Get selected text

        :return: selected text
        """
        return self.page().selectedText()

    def copy_selected_text(self):
        """Copy selected text"""
        self.page().triggerAction(QWebEnginePage.Copy)

    def select_all_text(self):
        """Select all text"""
        self.page().triggerAction(QWebEnginePage.SelectAll)

    def unselect_text(self):
        """Unselect text"""
        self.page().triggerAction(QWebEnginePage.Unselect)

    def find_open(self):
        """Open find dialog"""
        self.window.controller.finder.open(self.finder)

    def on_update(self):
        """On content update"""
        self.finder.clear()  # clear finder

    def focusInEvent(self, e):
        """
        Focus in event

        :param e: focus event
        """
        super(HtmlOutput, self).focusInEvent(e)
        self.window.controller.finder.focus_in(self.finder)

    def eventFilter(self, source, event):
        """
        Focus event filter

        :param source: source
        :param event: event
        """
        if (event.type() == QEvent.ChildAdded and
                source is self and
                event.child().isWidgetType()):
            self._glwidget = event.child()
            self._glwidget.installEventFilter(self)
        elif (event.type() == event.Type.MouseButtonPress):
            if self.tab:
                col_idx = self.tab.column_idx
                self.window.controller.ui.tabs.on_column_focus(col_idx)
        elif event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_F and (event.modifiers() & Qt.ControlModifier):
                self.find_open()
        return super().eventFilter(source, event)


class CustomWebEnginePage(QWebEnginePage):
    """Custom WebEnginePage to handle web events"""
    def __init__(self, window, parent):
        super(CustomWebEnginePage, self).__init__(window)
        self.window = window
        self.parent = parent
        self.signals = WebEnginePageSignals()
        self.findTextFinished.connect(self.on_find_finished)
        self.zoomFactorChanged.connect(self.on_view_changed)
        self.selectionChanged.connect(self.on_selection_changed)
        self.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessFileUrls, True
        )
        self.settings().setAttribute(
            QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
        )
        self.settings().setFontFamily(QWebEngineSettings.StandardFont, 'Lato')
        self.settings().setFontFamily(QWebEngineSettings.FixedFont, 'Monaspace Neon')
        self.settings().setFontFamily(QWebEngineSettings.SerifFont, 'Monaspace Neon')
        if self.window.core.config.has("zoom"):
            self.setZoomFactor(self.window.core.config.get("zoom"))

        # bridge Python <> JavaScript
        self.bridge = Bridge(self.window)
        self.channel = QWebChannel(self)
        self.channel.registerObject("bridge", self.bridge)
        self.setWebChannel(self.channel)

    def on_find_finished(self, result):
        """
        On find text finished

        :param result: Find result
        """
        current = int(result.activeMatch())
        num = int(result.numberOfMatches())
        self.parent.finder.current_match_index = current
        self.parent.finder.matches = num
        self.parent.finder.on_find_finished()

    def on_view_changed(self):
        """On view changed"""
        zoom = self.zoomFactor()
        self.window.core.config.set("zoom", zoom)
        option = self.window.controller.settings.editor.get_option('zoom')
        option['value'] = zoom
        self.window.controller.config.apply(
            parent_id='config',
            key='zoom',
            option=option,
        )

    def on_selection_changed(self):
        """On selection changed"""
        pass

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        """
        On navigation (link click) event

        :param url: URL
        :param _type: Navigation type
        :param isMainFrame: True if main frame
        """
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            self.window.core.filesystem.url.handle(url)
            return False
        return super().acceptNavigationRequest(url,  _type, isMainFrame)

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        """
        On JavaScript console message

        :param level: log level
        :param message: message
        :param line_number: line number
        :param source_id: source ID
        """
        self.signals.js_message.emit(line_number, message, source_id)  # handled in debug controller


class Bridge(QObject):
    """Bridge between Python and JavaScript"""
    def __init__(self, window):
        super(Bridge, self).__init__(window)
        self.window = window

    @Slot(str)
    def copy_text(self, text: str):
        """
        Copy text from web to clipboard

        :param text: text
        """
        self.window.controller.ctx.extra.copy_code_text(text)

    @Slot(str)
    def preview_text(self, text: str):
        """
        Preview code

        :param text: text
        """
        self.window.controller.ctx.extra.preview_code_text(text)

    @Slot(int)
    def update_scroll_position(self, pos: int):
        """
        Update scroll position from web view

        :param pos: scroll position
        """
        self.window.controller.chat.render.scroll = pos


class WebEngineSignals(QObject):
    save_as = Signal(str, str)
    audio_read = Signal(str)


class WebEnginePageSignals(QObject):
    js_message = Signal(int, str, str)  # on Javascript message