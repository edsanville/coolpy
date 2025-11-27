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
            Wikicode: The parameter's value as a Wikicode object, or None if the parameter does not exist.
        """
        try:
            return Wikicode(self.get(name).value)
        except ValueError:
            return None


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
            Template: The template, or None if it does not exist.
        """
        templates = self.get_templates(name, recursive=recursive)
        if len(templates) == 0:
            return None
        return templates[0]


    def get_text(self) -> str:
        """Get the text representation of the Wikicode.

        Returns:
            str: The text representation, replacing <br> tags with newlines and removing other markup.
        """
        # Replace all <br> / <br /> tags with newlines
        for tag in self.ifilter_tags(matches=lambda n: n.tag.lower() == "br"):
            self.replace(tag, "\n")
        return self.strip_code()

