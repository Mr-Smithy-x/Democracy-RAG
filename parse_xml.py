import json

from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import re

def extract_section_identifier(text):
    # Regex pattern:
    # (Sec\.\s+\d+) - Captures "Sec." followed by one or more spaces, then one or more digits.
    #                 This is group 1.
    # \.\s+         - Matches the dot and space(s) immediately following the section number.
    # (.+)          - Captures the rest of the string. This is group 2.
    #pattern = r"^(Sec\.\s+\d+)\.\s+(.+)$"
    #pattern = r"^Sec\.\s+(\d+)\.\s+(.+)$"
    pattern = r"^Sec\.\s+(\d+)\.\s+(.+)$"

    match = re.match(pattern, text)

    if match:
        section_identifier = match.group(1)
        remaining_text = match.group(2)
        #print(f"Section Identifier: '{section_identifier}'")
        #print(f"Remaining Text: '{remaining_text}'")
        return section_identifier, remaining_text
    else:
        #print("No match found.")
        return None, None



class Node:

    def __init__(self):
        self.parent = None
        self.header = None
        self.enum = None

    def set_parent(self, parent):
        self.parent = parent

    def get_parent(self):
        return self.parent

class Subparagraph(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId

class Paragraph(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.subparagraphs = []

    def add_subparagraph(self, subparagraphs: list[Subparagraph]):
        self.subparagraphs.extend(subparagraphs)

class Subsection(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId

class Section(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.subsections = []
        self.paragraphs = []

    def add_subsection(self, subsections: list[Subsection]):
        self.subsections.extend(subsections)

    def add_paragraph(self, paragraphs: list[Paragraph]):
        self.paragraphs.extend(paragraphs)

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
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subsections': obj.subsections, 'paragraphs': obj.paragraphs}
    elif isinstance(obj, Subsection):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum}
    elif isinstance(obj, Paragraph):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subparagraphs': obj.subparagraphs}
    elif isinstance(obj, Subparagraph):
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
        for entry in entries:
            lines = [line.strip() for line in entry.text.splitlines()]
            full_text = '\n'.join(lines)

            idref = entry.attrs['idref'] if entry.has_attr('idref') else None
            level = entry.attrs['level']
            header_text = None
            enum_text = None
            if idref is not None:
                tag = entry.select_one(f"{level}#{idref}")
                if tag is not None:
                    header = tag.select_one('header')
                    enum = tag.select_one('enum')
                    header_text = ' '.join(header.text.split())
                    enum_text = ' '.join(enum.text.split())
                else:
                    tag = entry.parent.parent.parent.parent.select_one(f"{level}#{idref}")
                    if tag is None:
                        tag = soup.select_one(f"{level}#{idref}")
                    header = tag.select_one('header')
                    enum = tag.select_one('enum')
                    header_text = ' '.join(header.text.split())
                    enum_text = ' '.join(enum.text.split())
            else:
                tag = None
                (enum, header) = extract_section_identifier(' '.join(full_text.split()))
                header_text = header
                enum_text = enum
                tag = entry.parent.parent.parent.parent.select_one(f"section:has(enum:contains(\"{enum_text}\"))")
                idref = tag.attrs['id'] if tag is not None else idref

            if level == 'title':
                text = tag.find('text', recursive=False) if tag is not None else None
                currTitle = Title(' '.join(text.text.split()) if text is not None else None, idref)
                currTitle.header = header_text
                currTitle.enum = enum_text
                titles.append(currTitle)
                currSubtitle = None
                currPart = None
            elif level == 'subtitle':
                if currTitle is not None:
                    text = tag.find('text', recursive=False) if tag is not None else None
                    currSubtitle = Subtitle(' '.join(text.text.split()) if text is not None else None, idref)
                    currSubtitle.header = header_text
                    currSubtitle.enum = enum_text
                    currTitle.add_subtitle(currSubtitle)
                    currSubtitle.set_parent(currTitle)
                else:
                    pass
                    # print(f"Warning: Subtitle '{text}' found without a parent title")
            elif level == 'part':
                if currSubtitle is not None:
                    text = tag.find('text', recursive=False)
                    currPart = Part(' '.join(text.text.split()) if text is not None else None, idref)
                    currPart.header = header_text
                    currPart.enum = enum_text
                    currSubtitle.add_part(currPart)
                    currPart.set_parent(currSubtitle)
                else:
                    pass
                    # print(f"Warning: Part '{text}' found without a parent subtitle")
            elif level == 'section':
                text = tag.find('text', recursive=False) if tag is not None else None
                newSection = Section(' '.join(text.text.split()) if text is not None else full_text, idref)
                newSection.header = header_text
                newSection.enum = enum_text
                newSection.add_subsection(parse_subsections(tag))
                newSection.add_paragraph(parse_paragraphs(tag))
                if currPart is not None:
                    currPart.add_section(newSection)
                    newSection.set_parent(currPart)
                elif currSubtitle is not None:
                    currSubtitle.add_section(newSection)
                    newSection.set_parent(currSubtitle)
                elif currTitle is not None:
                    # If no subtitle but we have a title, add directly to title
                    # print(f"Warning: Section '{text}' has no parent subtitle, adding to title")
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

def parse_subsections(entry):
    ss = []
    if entry is None:
        return ss
    subsections = entry.find_all('subsection', recursive=False)
    for subsection in subsections:
        toc = subsection.select_one('quoted-block > toc')
        if toc:
            ss.append(parse_toc(toc, entry))
        else:
            try:

                lines = [line.strip() for line in subsection.text.splitlines()]

                subsec = Subsection('\n'.join(lines), subsection.attrs['id'])
                header = subsection.select_one('header')
                enum = subsection.select_one('enum')
                subsec.header = header.text if header is not None else None
                subsec.enum = enum.text if enum is not None else None
                subsection.parent = entry
                ss.append(subsec)
            except Exception as e:
                print(f"Error parsing subsection: {e}")
    return ss


def parse_paragraphs(entry):
    pghs = []
    if entry is None:
        return pghs
    paragraphs = entry.find_all('paragraph', recursive=False)
    for subsection in paragraphs:

        paragraph_text = subsection.select_one('text')
        enum = subsection.select_one('enum')
        lines = [line.strip() for line in paragraph_text.text.splitlines()]

        paragraph = Paragraph('\n'.join(lines), subsection.attrs['id'])
        paragraph.header = paragraph_text.text if paragraph_text is not None else None
        paragraph.enum = enum.text if enum is not None else None
        paragraph.parent = entry
        paragraph.add_subparagraph(parse_subparagraphs(subsection))
        pghs.append(paragraph)
    return pghs

def parse_subparagraphs(entry):
    pghs = []
    if entry is None:
        return pghs
    subsections = entry.find_all('subparagraph', recursive=False)
    for subsection in subsections:
        paragraph_text = subsection.select_one('text')
        enum = subsection.select_one('enum')
        lines = [line.strip() for line in paragraph_text.text.splitlines()]

        paragraph = Subparagraph('\n'.join(lines), subsection.attrs['id'])
        paragraph.header = paragraph_text.text if paragraph_text is not None else None
        paragraph.enum = enum.text if enum is not None else None
        paragraph.parent = entry
        pghs.append(paragraph)
    return pghs


def parse_findings(soup):
    titles = []
    # print("\nFound using CSS selector:")
    # print(target_section)
    entries = soup.select('legis-body > section')
    currTitle = None
    currSubtitle = None
    currPart = None
    for entry in entries:
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

            newSection.add_subsection(parse_subsections(entry))

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
    elif findings:
        return parse_findings(soup)
    else:
        return []



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

titles = parse_document('xml/BILLS-119hr1eh.xml')
#titles = parse_document('xml/BILLS-119hr2385ih.xml')
print(len(titles))
jsonText = json.dumps(titles, default=custom_encoder, indent=4)
print(jsonText)


file_name = "BILLS-119hr1eh.json"

try:
    # Using 'with' ensures the file is properly closed even if errors occur
    with open(file_name, 'w') as file_object:
        file_object.write(jsonText)
    print(f"Successfully wrote to '{file_name}'")
except IOError:
    print(f"An error occurred while trying to write to '{file_name}'")

#soup.find_all()
# Find and print all tags
#for tag in soup.find_all("section.header"):
#    for child in tag.children:
#        print(child.find_all_next('subtitle'))
#    break



