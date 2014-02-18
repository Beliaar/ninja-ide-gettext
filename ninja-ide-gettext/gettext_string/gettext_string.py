# -*- coding: UTF-8 -*-
import ast

from ninja_ide.core import plugin
from ninja_ide.core import plugin_services


class GettextString(plugin.Plugin):
    def initialize(self):
        # Init your plugin
        #For IDE
        if False:
            self.editor_s = plugin_services.MainService()
        self.editor_s = self.locator.get_service('editor')
        self.editor_s.currentTabChanged.connect(self.cb_tab_changed)
        self.gettext_types = (ast.Call, ast.Assign)
        self.ignored_methods = []
        self.cb_tab_changed(None)

    def finish(self):
        # Shutdown your plugin
        pass

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        pass

    def cb_tab_changed(self, filename):
        source = self.editor_s.get_text().encode("utf-8")
        #For IDE
        tree = ast.parse(source)
        messages = self.recursive_check(tree)
        print messages

    def recursive_check(self, cur_node, node_list=None, cur_lineno=0):
        """Recursively check for Str objects that are not inside a
        gettext function or an ignored function/method

        Args:

            cur_node: The current node to check

            node_list: A list of nodes up to the current_node

            cur_lineno: The current linenumber

        Returns: A list of lines with strings that are not passed to gettext or
        ignored functions/methods.
        """
        messages = []
        node_list = node_list or list()
        if hasattr(cur_node, "lineno"):
            cur_lineno = cur_node.lineno
        if isinstance(cur_node, ast.Str):
            for node in node_list:
                if isinstance(node, self.gettext_types):
                    messages.append((cur_lineno, cur_node.s))
                    break
        elif isinstance(cur_node, (list, tuple)):
            for node in cur_node:
                messages.extend(self.recursive_check(node,
                                                     node_list,
                                                     cur_lineno))
        if isinstance(cur_node, ast.Call):
            assert isinstance(cur_node, ast.Call)
            func = cur_node.func
            if isinstance(func, ast.Attribute):
                func_name = func.attr
            elif isinstance(func, ast.Name):
                func_name = func.id
            else:
                raise RuntimeError("%s type not handled" % (str(type(func))))
            if (func_name.endswith("gettext") or
                func_name in self.ignored_methods or
                func_name is "_"):
                return messages
        if hasattr(cur_node, "_fields"):
            node_list.append(cur_node)
            for field in cur_node._fields:
                node = getattr(cur_node, field)
                messages.extend(self.recursive_check(node,
                                                     node_list,
                                                     cur_lineno))
            node_list.pop()
        return messages
