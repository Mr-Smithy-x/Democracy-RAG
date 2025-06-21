import json
import os
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from parser.models import Node


class NodeObject:
    def __init__(self, id, header, enum, name):
        super().__init__()
        self.id = id
        if name is not None:
            self.title = f'{name} {enum} {header}'
        else:
            self.title = f'{enum}: {header}'
        self.header = header
        self.enum = enum
        self.children = []
        self.icon = 'Scale'
        self.color = 'from-blue-600 to-blue-700'
        self.description = 'This is a title node'
        self.details = 'This is a title node'

    def add_child(self, child):
        self.children.append(child)

    def add_children(self, child: list):
        self.children.extend(child)

class TableOfContents:

    def __init__(self, filename=None):
        self.filename = filename
        self.soup = None
        self.titles = dict()
        self.init()

    def set_filename(self, filename):
        self.filename = filename
        self.soup = None
        self.titles = dict()
        self.init()

    def init(self):
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        # Open the XML file and parse it with BeautifulSoup
        with open(self.filename, 'r', encoding='utf-8') as file:
            # Example usage
            self.soup = BeautifulSoup(file, 'html.parser')

        def convert_quotes():
            # Parse the XML text

            # Find all quote tags
            quote_tags = self.soup.find_all('quote')

            # Replace each quote tag with quoted text
            for quote in quote_tags:
                # Get the text content
                text = quote.get_text(strip=True)
                # Replace the quote tag with quoted text
                quote.replace_with(f'"{text}"')

            # Get the modified text
            return self.soup.get_text(strip=True)

        result = convert_quotes()

    def _parse_section(self, section):
        section_id = section.attrs['id']
        section_header = ' '.join(section.find('header', recursive=False).text.split())
        section_enum = ' '.join(section.find('enum', recursive=False).text.split())
        section_text = ' '.join(section.find('text', recursive=False).text.split() if section.find('text', recursive=False) is not None else ''.split())
        section_obj = NodeObject(section_id, section_header, section_enum, section.name.capitalize())
        section_obj.details = section.text
        section_obj.description = section_text
        return section_obj

    def _parse_part(self, part):
        part_id = part.attrs['id']
        part_header = ' '.join(part.find('header', recursive=False).text.split())
        part_enum = ' '.join(part.find('enum', recursive=False).text.split())
        part_text = ' '.join(part.find('text', recursive=False).text.split() if part.find('text', recursive=False) is not None else ''.split())
        part_obj = NodeObject(part_id, part_header, part_enum, part.name.capitalize())
        part_obj.details = part.text
        part_obj.description = part_text
        return part_obj

    def _parse_subtitle(self, subtitle):
        subtitle_id = subtitle.attrs['id']
        subtitle_header = ' '.join(subtitle.find('header', recursive=False).text.split())
        subtitle_enum = ' '.join(subtitle.find('enum', recursive=False).text.split())
        subtitle_text = ' '.join(subtitle.find('text', recursive=False).text.split() if subtitle.find('text', recursive=False) is not None else ''.split())
        subtitle_obj = NodeObject(subtitle_id, subtitle_header, subtitle_enum, subtitle.name.capitalize())
        subtitle_obj.details = subtitle.text
        subtitle_obj.description = subtitle_text
        return subtitle_obj

    def _parse_title(self, title):
        id = title.attrs['id']
        enum = ' '.join(title.find('enum', recursive=False).text.split())
        header = ' '.join(title.find('header', recursive=False).text.split())
        text = ' '.join(title.find('text', recursive=False).text.split() if title.find('text', recursive=False) is not None else ''.split())

        title_obj = NodeObject(id, header, enum, title.name.capitalize())
        title_obj.description = text
        return title_obj

    def parse(self):
        official_title =  ' '.join(self.soup.select_one('form > official-title').text.split())
        bill_title = ' '.join(self.soup.select_one('dublinCore > dc\\:title').text.split())
        root = NodeObject('root', bill_title, '1', None)
        root.description = bill_title
        root.details = official_title
        titles = self.soup.select('legis-body > section > toc > toc-entry[level="title"]')
        for title_xml in titles:
            title = self.soup.select_one(f"title[id='{title_xml.attrs['idref']}']")
            subtitles = title.find_all("subtitle", recursive=False)
            sections = title.find_all("section", recursive=False)
            title_obj = self._parse_title(title)
            if len(sections) == 0:
                for subtitle in subtitles:
                    subtitle_obj = self._parse_subtitle(subtitle)
                    title_obj.add_child(subtitle_obj.id)
                    sections = subtitle.find_all("section", recursive=False)
                    parts = subtitle.find_all("part", recursive=False)
                    for section in sections:
                        section_obj = self._parse_section(section)
                        subtitle_obj.add_child(section_obj.id)
                        self.titles[section_obj.id] = section_obj
                    for part in parts:
                        part_obj = self._parse_part(part)
                        subtitle_obj.add_child(part_obj.id)
                        self.titles[part_obj.id] = part_obj
                    self.titles[subtitle_obj.id] = subtitle_obj
            else:
                for section in sections:
                    section_obj = self._parse_section(section)
                    title_obj.add_child(section_obj.id)
                    self.titles[section_obj.id] = section_obj
            root.add_child(title_obj.id)
            self.titles[title_obj.id] = title_obj
        self.titles[root.id] = root


def custom_encoder(obj):
    if isinstance(obj, NodeObject):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return { 'id': obj.id, 'title': obj.title, 'header': obj.header, 'enum': obj.enum, 'children': obj.children , 'icon': obj.icon, 'color': obj.color, 'description': obj.description, 'details': obj.details}
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def main():
    bill = "BILLS-119hr1eh"
    filename = f"xml/{bill}.xml"
    toc = TableOfContents(filename)
    toc.parse()

    jsonText = json.dumps(toc.titles, default=custom_encoder, indent=2)

    os.mkdir("json") if not os.path.exists("json") else None

    with open(f"json/{bill}.json", "w") as outfile:
        outfile.write(jsonText)



main()
