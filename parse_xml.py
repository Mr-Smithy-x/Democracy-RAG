import json

from bs4 import BeautifulSoup

from bs4 import XMLParsedAsHTMLWarning
import warnings

class Node:

    def __init__(self):
        self.parent = None
        self.header = None
        self.enum = None

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

class Section(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId

class Part(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []

    def add_section(self, section: Section):
        self.sections.append(section)

class Subtitle(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []
        self.parts = []

    def add_part(self, part: Part):
        self.parts.append(part)

    def add_section(self, section: Section):
        self.sections.append(section)

class Title(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []
        self.subtitles = []

    def add_subtitle(self, subtitle: Subtitle):
        self.subtitles.append(subtitle)

    def add_section(self, section: Section):
        self.sections.append(section)

def custom_encoder(obj):
    if isinstance(obj, Title):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return { 'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'subtitles': obj.subtitles, 'sections': obj.sections, 'header': obj.header, 'enum': obj.enum}
    elif isinstance(obj, Subtitle):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return { 'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'sections': obj.sections, 'parts': obj.parts, 'header': obj.header, 'enum': obj.enum}
    elif isinstance(obj, Part):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'sections': obj.sections, 'header': obj.header, 'enum': obj.enum}
    elif isinstance(obj, Section):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum}
    # You could add more isinstance checks for other custom classes here
    # For any other type it doesn't know, raise a TypeError as per default behavior
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def parse_toc(toc, soup):
    titles = []
    if toc:
        # print("\nFound using CSS selector:")
        # print(target_section)
        entries = toc.select('toc-entry')
        currTitle = None
        currSubtitle = None
        currPart = None
        for entry in entries[2:]:
            text = ' '.join(entry.text.split())
            idref = entry.attrs['idref']
            level = entry.attrs['level']
            tag = soup.select_one(f"{level}#{idref}")
            header = tag.select_one('header')
            enum = tag.select_one('enum')
            header_text = ' '.join(header.text.split())
            enum_text = ' '.join(enum.text.split())
            if level == 'title':
                currTitle = Title(text, idref)
                currTitle.header = header_text
                currTitle.enum = enum_text
                titles.append(currTitle)
                currSubtitle = None
                currPart = None

            elif level == 'subtitle':
                if currTitle is not None:
                    currSubtitle = Subtitle(text, idref)
                    currSubtitle.header = header_text
                    currSubtitle.enum = enum_text
                    currTitle.add_subtitle(currSubtitle)
                    currSubtitle.set_parent(currTitle)
                else:
                    pass
                    # print(f"Warning: Subtitle '{text}' found without a parent title")
            elif level == 'part':
                if currSubtitle is not None:
                    currPart = Part(text, idref)
                    currPart.header = header_text
                    currPart.enum = enum_text
                    currSubtitle.add_part(currPart)
                    currPart.set_parent(currSubtitle)
                else:
                    pass
                    # print(f"Warning: Part '{text}' found without a parent subtitle")
            elif level == 'section':
                if currPart is not None:
                    newSection = Section(text, idref)
                    newSection.header = header_text
                    newSection.enum = enum_text
                    currPart.add_section(newSection)
                    newSection.set_parent(currPart)
                elif currSubtitle is not None:
                    newSection = Section(text, idref)
                    newSection.header = header_text
                    newSection.enum = enum_text
                    currSubtitle.add_section(newSection)
                    newSection.set_parent(currSubtitle)
                elif currTitle is not None:
                    # If no subtitle but we have a title, add directly to title
                    # print(f"Warning: Section '{text}' has no parent subtitle, adding to title")
                    newSection = Section(text, idref)
                    newSection.header = header_text
                    newSection.enum = enum_text
                    currTitle.add_section(newSection)  # Assuming Title class can hold sections directly
                    newSection.set_parent(currTitle)
                else:
                    pass
                    # print(f"Warning: Section '{text}' found without a parent title or subtitle")

                if tag is not None:
                    # print(' '.join(tag.text.split()))
                    # print(tag.text)
                    # print('\n'.join(tag.text.rsplit('\n')))
                    pass  # break
    return titles

def parse_findings(soup):
    titles = []
    # print("\nFound using CSS selector:")
    # print(target_section)
    body = soup.select_one('legis-body')
    entries = body.children
    currTitle = None
    currSubtitle = None
    currPart = None
    for entry in entries:

        print(entry)
        text = ' '.join(entry.text.split())
        idref = entry.attrs['id']
        section_type = entry.name #entry.attrs['section-type'] if entry.has_attr('section-type') else None
        header = entry.select_one('header')
        enum = entry.select_one('enum')
        header_text = ' '.join(header.text.split())
        enum_text = ' '.join(enum.text.split())
        if section_type == 'title':
            currTitle = Title(text, idref)
            currTitle.header = header_text
            currTitle.enum = enum_text
            #titles.append(currTitle)
            currSubtitle = None
            currPart = None

        elif section_type == 'subtitle':
            if currTitle is not None:
                currSubtitle = Subtitle(text, idref)
                currSubtitle.header = header_text
                currSubtitle.enum = enum_text
                currTitle.add_subtitle(currSubtitle)
                currSubtitle.set_parent(currTitle)
            else:
                pass
                # print(f"Warning: Subtitle '{text}' found without a parent title")
        elif section_type == 'part':
            if currSubtitle is not None:
                currPart = Part(text, idref)
                currPart.header = header_text
                currPart.enum = enum_text
                currSubtitle.add_part(currPart)
                currPart.set_parent(currSubtitle)
            else:
                pass
                # print(f"Warning: Part '{text}' found without a parent subtitle")
        elif section_type == 'section':
            # If no subtitle but we have a title, add directly to title
            # print(f"Warning: Section '{text}' has no parent subtitle, adding to title")
            newSection = Section(text, idref)
            newSection.header = header_text
            newSection.enum = enum_text
            titles.append(newSection)  # Assuming Title class can hold sections directly

            # print(f"Warning: Section '{text}' found without a parent title or subtitle")

            #if tag is not None:
                # print(' '.join(tag.text.split()))
                # print(tag.text)
                # print('\n'.join(tag.text.rsplit('\n')))
                #pass  # break
    return titles


def parse_document(filename: str):
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

    # Open the XML file and parse it with BeautifulSoup
    with open(filename, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    toc = soup.select_one('section:has(header:contains("Table of contents"))')
    findings = soup.select_one('section:has(header:contains("Findings"))')
    if toc:
        return parse_toc(toc, soup)
    else:
        return parse_findings(soup)



def debug_print(titles: list[Title]):
    print(f"This bill has {len(titles)} titles")
    for title_idx, title in enumerate(titles):
        print(f"Title {title_idx + 1}: \"{title.text}\" has {len(title.subtitles)} subtitles and {len(title.sections)} direct sections")
        for sub_idx, subtitle in enumerate(title.subtitles):
            print(f"\tSubtitle {title_idx + 1}.{sub_idx + 1}: \"{subtitle.text}\" has {len(subtitle.sections)} sections")
            for sec_idx, section in enumerate(subtitle.sections):
                # pass # No need to print every section text for verification of counts
                print(f"\t\tSection {title_idx + 1}.{sub_idx + 1}.{sec_idx + 1}: {section.text}")

            print(f"\tSubtitle {title_idx + 1}.{sub_idx + 1}: \"{subtitle.text}\" has {len(subtitle.parts)} parts")
            for part_idx, part in enumerate(subtitle.parts):
                # pass # No need to print every section text for verification of counts
                print(f"\t\tParts {title_idx + 1}.{sub_idx + 1}.{part_idx + 1}: \"{part.text}\" has {len(part.sections)} sections")
                print(f"\t\tParts {title_idx + 1}.{sub_idx + 1}.{part_idx + 1}: {part.text}")
                for sec_idx, section in enumerate(part.sections):
                    # pass # No need to print every section text for verification of counts
                    print(f"\t\t\tParts Section {title_idx + 1}.{sub_idx + 1}.{part_idx + 1}.{sec_idx + 1}: {section.text}")

        # If you also want to print sections directly under a title:
        for sec_idx, section in enumerate(title.sections):
            print(f"\tDirect Section {title_idx + 1}.{sec_idx + 1} (under \"{section.parent.text}\"): {section.text}")
        print("=" * 100)

#titles = parse_document('xml/BILLS-119hr1eh.xml')
titles = parse_document('xml/BILLS-119hr2385ih.xml')
print(len(titles))
print(json.dumps(titles, default=custom_encoder, indent=4))
#soup.find_all()
# Find and print all tags
#for tag in soup.find_all("section.header"):
#    for child in tag.children:
#        print(child.find_all_next('subtitle'))
#    break



