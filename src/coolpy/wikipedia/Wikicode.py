import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode as _Wikicode
from mwparserfromhell.nodes import Node as _Node


class Template:
    _template: mwparserfromhell.nodes.Template

    def __init__(self, template: mwparserfromhell.nodes.Template):
        self._template = template

    def __repr__(self) -> str:
        return repr(self._template)
    
    def __str__(self) -> str:
        return str(self._template)
    
    def get_item(self, *names: str, path_so_far: str='') -> "Wikicode | Template":
        """Drill down into a Template object following a path of node types.

        Args:
            names (str): The name of the item(s) to find.
        """

        if len(names) == 0:
            return self
        
        param_name = names[0].strip()
        try:
            param = self._template.get(param_name)
        except ValueError:
            raise KeyError(f"Path '{path_so_far}{param_name}' does not exist.")
        
        return Wikicode(param.value).get_item(*names[1:], path_so_far=f"{path_so_far}{param_name}.")


class Wikicode:
    _wikicode: _Wikicode

    def __init__(self, wikicode: _Wikicode | None=None, text: str | None=None):
        if wikicode is not None:
            self._wikicode = wikicode
        elif text is not None:
            self._wikicode = mwparserfromhell.parse(text)
        else:
            raise ValueError("Either wikicode or text must be provided")

    def get_templates(self, name: str) -> list[Template]:
        """Get all templates with a given case-insensitive name.

        Args:
            name (str): Template name (case-insensitive).

        Returns:
            list[mwparserfromhell.nodes.Template]: A list of templates, (can be empty).
        """
        return [Template(t) for t in self._wikicode.filter_templates(recursive=False, matches=lambda myname: myname.name.strip().lower() == name.lower())]


    def get_item(self, *names: str, path_so_far: str='') -> "Wikicode | Template":
        """Drill down into a Wikicode object following a path of node types.

        Args:
            names (str): The name of the item(s) to find.
        """

        if len(names) == 0:
            return self
        
        template_name = names[0]
        templates = self.get_templates(template_name)
        if len(templates) == 0:
            raise KeyError(f"Path '{path_so_far}{template_name} does not exist.")
        return templates[0].get_item(*names[1:], path_so_far=f"{path_so_far}{template_name}.")

    def __repr__(self) -> str:
        return repr(self._wikicode)
    
    def __str__(self) -> str:
        return str(self._wikicode)
