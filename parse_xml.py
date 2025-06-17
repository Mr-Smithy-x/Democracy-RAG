import json

from bs4 import BeautifulSoup
from bs4.element import Tag
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

class QuotedBlock(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []
        self.subsections = []
        self.paragraphs = []
        self.subparagraphs = []
        self.clauses = []
        self.subparts = []
        self.after_quoted_block = None

    def add_subparts(self, subpart):
        self.subparts.extend(subpart)

    def add_sections(self, section):
        self.sections.extend(section)

    def add_subsections(self, subsection):
        self.subsections.extend(subsection)

    def add_paragraphs(self, paragraph):
        self.paragraphs.extend(paragraph)

    def add_subparagraphs(self, subparagraph):
        self.subparagraphs.extend(subparagraph)

    def add_clauses(self, clause):
        self.clauses.extend(clause)

    def set_after_quoted_block(self, param):
        self.after_quoted_block = param


class Subclause(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.quoted_blocks = []

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)


class Clause(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.quoted_blocks = []
        self.subclauses = []

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)

    def add_subclauses(self, subclauses: list[Subclause]):
        self.subclauses.extend(subclauses)

class Item(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId

class Subparagraph(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.clauses = []
        self.quoted_blocks = []

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)

    def add_clause(self, clauses: list[Clause]):
        self.clauses.extend(clauses)

class Paragraph(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.subparagraphs = []
        self.quoted_blocks = []

    def add_subparagraph(self, subparagraphs: list[Subparagraph]):
        self.subparagraphs.extend(subparagraphs)

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)

class Subsection(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.quoted_blocks = []
        self.paragraphs = []

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)

    def add_paragraphs(self, paragraphs: list[Paragraph]):
        self.paragraphs.extend(paragraphs)

class Section(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.subsections = []
        self.paragraphs = []
        self.quoted_blocks = []

    def add_subsection(self, subsections: list[Subsection]):
        self.subsections.extend(subsections)

    def add_paragraph(self, paragraphs: list[Paragraph]):
        self.paragraphs.extend(paragraphs)

    def add_quoted_block(self, quoted_blocks: list[QuotedBlock]):
        self.quoted_blocks.extend(quoted_blocks)

class Subpart(Node):
    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []

    def add_sections(self, sections: list[Section]):
        self.sections.extend(sections)

class Part(Node):

    def __init__(self, text, refId):
        super().__init__()
        self.text = text
        self.refId = refId
        self.sections = []
        self.subparts = []

    def add_sections(self, sections: list[Section]):
        self.sections.extend(sections)

    def add_section(self, section: Section):
        self.sections.append(section)

    def add_subparts(self, subparts: list[Subpart]):
        self.subparts.extend(subparts)

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
        return { 'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subtitles': obj.subtitles, 'sections': obj.sections}
    elif isinstance(obj, Subtitle):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return { 'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'sections': obj.sections, 'parts': obj.parts}
    elif isinstance(obj, Part):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'sections': obj.sections, 'subparts': obj.subparts}
    elif isinstance(obj, Section):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subsections': obj.subsections, 'paragraphs': obj.paragraphs, 'quoted_blocks': obj.quoted_blocks}
    elif isinstance(obj, Subsection):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'paragraphs': obj.paragraphs}
    elif isinstance(obj, Paragraph):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subparagraphs': obj.subparagraphs, 'quoted_blocks': obj.quoted_blocks}
    elif isinstance(obj, Subparagraph):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'clauses': obj.clauses, 'quoted_blocks': obj.quoted_blocks}
    elif isinstance(obj, Clause):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'quoted_blocks': obj.quoted_blocks, 'subclauses': obj.subclauses}
    elif isinstance(obj, Subclause):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'quoted_blocks': obj.quoted_blocks}
    elif isinstance(obj, Subpart):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'sections': obj.sections}
    elif isinstance(obj, QuotedBlock):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subparagraphs': obj.subparagraphs, 'paragraphs': obj.paragraphs, 'clauses': obj.clauses, 'sections': obj.sections, 'subsections': obj.subsections, 'after_quoted_blocks': obj.after_quoted_block}
    # You could add more isinstance checks for other custom classes here
    # For any other type it doesn't know, raise a TypeError as per default behavior
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def parse_toc(toc, soup):
    titles = []
    if toc:
        # print("\nFound using CSS selector:")
        # print(target_section)
        entries = toc.select('toc-entry')
        curr_title = None
        curr_subtitle = None
        current_part = None
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
                tag = entry.parent.parent.parent.parent.select_one(f"section:has(enum:-soup-contains(\"{enum_text}\"))")
                idref = tag.attrs['id'] if tag is not None else idref
            if level == 'title':
                curr_title = parse_title(tag)
                titles.append(curr_title)
                curr_subtitle = None
                current_part = None
            elif level == 'subtitle':
                if curr_title is not None:
                    curr_subtitle = parse_subtitle(tag)
                    if curr_subtitle is not None:
                        curr_title.add_subtitle(curr_subtitle)
                        if curr_subtitle is None:
                            print("WTF")
                        if curr_title is None:
                            print("WTF2")
                        curr_subtitle.set_parent(curr_title)
                else:
                    pass
                    # print(f"Warning: Subtitle '{text}' found without a parent title")
            elif level == 'part':
                if curr_subtitle is not None:
                    current_part = parse_part(tag)
                    if current_part is not None:
                        curr_subtitle.add_part(current_part)
                        current_part.set_parent(curr_subtitle)
                else:
                    pass
                    # print(f"Warning: Part '{text}' found without a parent subtitle")
            elif level == 'section':
                section = parse_section(tag)
                if section is None:
                    continue
                #if current_part is not None:
                #    current_part.add_section(section)
                #    section.set_parent(current_part)
                elif curr_subtitle is not None:
                    curr_subtitle.add_section(section)
                    section.set_parent(curr_subtitle)
                elif curr_title is not None:
                    # If no subtitle but we have a title, add directly to title
                    # print(f"Warning: Section '{text}' has no parent subtitle, adding to title")
                    curr_title.add_section(section)  # Assuming Title class can hold sections directly
                    section.set_parent(curr_title)
                else:
                    pass
                    # print(f"Warning: Section '{text}' found without a parent title or subtitle")
                if tag is not None:
                    # print(' '.join(tag.text.split()))
                    # print(tag.text)
                    # print('\n'.join(tag.text.rsplit('\n')))
                    pass  # break
    return titles

def parse_sections(entry):
    sections_list = []
    if entry is None:
        return sections_list
    sections = entry.find_all('section', recursive=False)
    for section in sections:
        section_obj = parse_section(section)
        if section_obj is not None:
            sections_list.append(section_obj)
    return sections_list

def parse_section(section):
    if section is None:
        return None
    header = section.find('header', recursive=False)
    enum = section.find('enum', recursive=False)
    text = section.find('text', recursive=False)
    section_obj = Section(' '.join(text.text.split()) if text is not None else None, section.attrs['id'])
    section_obj.header = header.text if header is not None else None
    section_obj.enum = enum.text if enum is not None else None
    section_obj.parent = section.parent
    section_obj.add_subsection(parse_subsections(section))
    section_obj.add_paragraph(parse_paragraphs(section))
    section_obj.add_quoted_block(parse_quoted_blocks(section))
    return section_obj

def parse_part(part):
    if part is None:
        return None
    header = part.find('header', recursive=False)
    enum = part.find('enum', recursive=False)
    text = part.find('text', recursive=False)
    part_obj = Part(' '.join(text.text.split()) if text is not None else None, part.attrs['id'])
    part_obj.add_subparts(parse_subparts(part))
    part_obj.add_sections(parse_sections(part))
    part_obj.header = header.text
    part_obj.enum = enum.text
    return part_obj

def parse_title(title):
    if title is None:
        return None
    header = title.find('header', recursive=False)
    enum = title.find('enum', recursive=False)
    text = title.find('text', recursive=False)
    title_obj = Title(' '.join(text.text.split()) if text is not None else None, title.attrs['id'])
    title_obj.header = header.text
    title_obj.enum = enum.text
    return title_obj

def parse_subtitle(subtitle):
    if subtitle is None:
        return None
    header = subtitle.find('header', recursive=False)
    enum = subtitle.find('enum', recursive=False)
    text = subtitle.find('text', recursive=False)
    subtitle_obj = Subtitle(' '.join(text.text.split()) if text is not None else None, subtitle.attrs['id'])
    subtitle_obj.header = header.text
    subtitle_obj.enum = enum.text
    return subtitle_obj


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
                header = subsection.select_one('header')
                enum = subsection.select_one('enum')
                subsection_obj = Subsection('\n'.join(lines), subsection.attrs['id'])
                subsection_obj.header = header.text if header is not None else None
                subsection_obj.enum = enum.text if enum is not None else None
                subsection_obj.parent = entry
                subsection_obj.add_quoted_block(parse_quoted_blocks(subsection))
                subsection_obj.add_paragraphs(parse_paragraphs(subsection))
                ss.append(subsection_obj)
            except Exception as e:
                print(f"Error parsing subsection: {e}")
    return ss

def parse_paragraphs(entry):
    pghs = []
    if entry is None:
        return pghs
    paragraphs = entry.find_all('paragraph', recursive=False)
    for paragraph in paragraphs:

        paragraph_text = paragraph.select_one('text')
        enum = paragraph.select_one('enum')
        header = paragraph.find('header', recursive=False)
        lines = [line.strip() for line in paragraph_text.text.splitlines()]

        paragraph_obj = Paragraph('\n'.join(lines), paragraph.attrs['id'])
        paragraph_obj.header = header.text if header is not None else None
        paragraph_obj.enum = enum.text if enum is not None else None
        paragraph_obj.parent = entry
        paragraph_obj.add_subparagraph(parse_subparagraphs(paragraph))
        paragraph_obj.add_quoted_block(parse_quoted_blocks(paragraph))
        pghs.append(paragraph_obj)
    return pghs

def parse_subparts(entry):
    sps = []
    if entry is None:
        return sps
    subparts = entry.find_all('subpart', recursive=False)
    for subpart in subparts:

        subpart_text = subpart.select_one('text')
        enum = subpart.select_one('enum')

        header = subpart.find('header', recursive=False)
        lines = [line.strip() for line in subpart_text.text.splitlines()]

        subpart_obj = Subpart('\n'.join(lines), subpart.attrs['id'])
        subpart_obj.header = header.text if header is not None else None
        subpart_obj.enum = enum.text if enum is not None else None
        subpart_obj.parent = entry
        subpart_obj.add_sections(parse_sections(subpart))
        sps.append(subpart_obj)
    return sps

def parse_subparagraphs(entry):
    pghs = []
    if entry is None:
        return pghs
    subparagraphs = entry.find_all('subparagraph', recursive=False)
    for subparagraph in subparagraphs:
        subparagraph_text = subparagraph.select_one('text')
        enum = subparagraph.select_one('enum')
        header = subparagraph.find('header', recursive=False)
        lines = [line.strip() for line in subparagraph_text.text.splitlines()]

        subparagraph_obj = Subparagraph('\n'.join(lines), subparagraph.attrs['id'])
        subparagraph_obj.header = header.text if header is not None else None
        subparagraph_obj.enum = enum.text if enum is not None else None
        subparagraph_obj.parent = entry
        subparagraph_obj.add_quoted_block(parse_quoted_blocks(subparagraph))
        subparagraph_obj.add_clause(parse_clauses(subparagraph))
        pghs.append(subparagraph_obj)
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
    with open(filename, 'r', encoding='utf-8') as file:
        # Example usage
        soup = BeautifulSoup(file, 'html.parser')

    def convert_quotes():
        # Parse the XML text

        # Find all quote tags
        quote_tags = soup.find_all('quote')

        # Replace each quote tag with quoted text
        for quote in quote_tags:
            # Get the text content
            text = quote.get_text(strip=True)
            # Replace the quote tag with quoted text
            quote.replace_with(f'"{text}"')

        # Get the modified text
        return soup.get_text(strip=True)


    result = convert_quotes()
    print(result)

    toc = soup.select_one('section:has(header:-soup-contains("Table of contents"))')
    findings = soup.select_one('section:has(header:-soup-contains("Findings"))')
    if toc:
        return parse_toc(toc, soup)
    elif findings:
        return parse_findings(soup)
    else:
        return []

def parse_quoted_blocks(entry):
    qbs = []
    if entry is None:
        return qbs
    quoted_blocks = entry.find_all('quoted-block', recursive=False)
    for quoted_block in quoted_blocks:
        aqb = quoted_block.find('after-quoted-block', recursive=False)

        lines = [line.strip() for line in quoted_block.text.splitlines()]
        full_text = '\n'.join(lines)

        block = QuotedBlock(full_text, quoted_block.attrs['id'])
        block.set_after_quoted_block(aqb.text if aqb is not None else None)
        block.add_sections(parse_sections(quoted_block))
        block.add_subsections(parse_subsections(quoted_block))
        block.add_paragraphs(parse_paragraphs(quoted_block))
        block.add_subparagraphs(parse_subparagraphs(quoted_block))
        block.add_clauses(parse_clauses(quoted_block))
        qbs.append(block)
    return qbs

def parse_clauses(entry):
    cl = []
    if entry is None:
        return cl
    clauses = entry.find_all('clause', recursive=False)
    for clause in clauses:

        clause_text = clause.select_one('text')
        enum = clause.select_one('enum')
        header = clause.find('header', recursive=False)
        clause_obj = Clause(clause_text.text if clause_text is not None else None, clause.attrs['id'])
        clause_obj.header = header.text if header is not None else None
        clause_obj.enum = enum.text if enum is not None else None
        clause.add_subclauses(parse_subclauses(clause))
        cl.append(clause_obj)
    return cl

def parse_subclauses(entry):
    scl = []
    if entry is None:
        return scl
    subclauses = entry.find_all('subclause', recursive=False)
    for subclause in subclauses:
        subclause_text = subclause.select_one('text')
        enum = subclause.select_one('enum')
        header = subclause.find('header', recursive=False)
        subclause_obj = Subclause(subclause_text.text if subclause_text is not None else None, subclause.attrs['id'])
        subclause_obj.header = header.text if header is not None else None
        subclause_obj.enum = enum.text if enum is not None else None
        scl.append(subclause_obj)
    return scl

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



