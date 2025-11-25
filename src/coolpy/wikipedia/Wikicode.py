import mwparserfromhell
from copy import deepcopy, copy


class Template(mwparserfromhell.nodes.Template):
    def __init__(self, template: mwparserfromhell.nodes.Template):
        super().__init__(template.name)
        self.params.extend(deepcopy(template.params))


    def get_parameter(self, name: str) -> "Wikicode":
        """Get a parameter by name.

        Args:
            name (str): The name of the parameter.

        Returns:
            Wikicode: The parameter's value as a Wikicode object.

        Raises:
            ValueError: If no parameter with the given name exists.
        """
        return Wikicode(self.get(name).value)


class Wikicode(mwparserfromhell.wikicode.Wikicode):
    def __init__(self, wikicode: mwparserfromhell.wikicode.Wikicode):
        self.nodes = deepcopy(wikicode.nodes)

    @staticmethod
    def parse(text: str) -> "Wikicode":
        """Parse a string into a Wikicode object.

        Args:
            text (str): The text to parse.

        Returns:
            Wikicode: The parsed Wikicode object.
        """
        return Wikicode(mwparserfromhell.parse(text))

    def get_templates(self, name: str, recursive=False) -> list[Template]:
        """Get all templates with a given case-insensitive name.

        Args:
            name (str): Template name (case-insensitive).

        Returns:
            list[mwparserfromhell.nodes.Template]: A list of templates, (can be empty).
        """
        return [Template(t) for t in self.filter_templates(recursive=recursive, matches=lambda myname: myname.name.strip().lower() == name.lower())]


    def get_template(self, name: str, recursive=False) -> Template:
        """Get the first template with a given case-insensitive name.

        Args:
            name (str): Template name (case-insensitive).

        Returns:
            mwparserfromhell.nodes.Template: The template.

        Raises:
            KeyError: If no template with the given name exists.
        """
        templates = self.get_templates(name, recursive=recursive)
        if len(templates) == 0:
            raise KeyError(f"Template '{name}' does not exist.")
        return templates[0]
