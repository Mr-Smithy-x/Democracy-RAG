import re
import warnings

from bs4 import XMLParsedAsHTMLWarning, BeautifulSoup

from parser import Section, Subsection, SubItem, Item, Subpart, Part, Subtitle, Title, QuotedBlock, Subclause, Clause, Subparagraph, \
    Paragraph


class USDocumentParser:

    soup: BeautifulSoup = None

    def __init__(self, filename):
        self.filename = filename
        self.soup = None
        self.init()

    def set_filename(self, filename):
        self.filename = filename
        self.soup = None
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

    def parse_sections(self, entry):
        sections_list = []
        if entry is None:
            return sections_list
        sections = entry.find_all('section', recursive=False)
        for section in sections:
            section_obj = self.parse_section(section)
            if section_obj is not None:
                sections_list.append(section_obj)
        return sections_list

    def parse_parts(self, entry):
        parts_list = []
        if entry is None:
            return parts_list
        parts = entry.find_all('part', recursive=False)
        for part in parts:
            part_obj = self.parse_part(part)
            if part_obj is not None:
                parts_list.append(part_obj)
        return parts_list

    def parse_subtitles(self, entry):
        subtitles_list = []
        if entry is None:
            return subtitles_list
        subtitles = entry.find_all('subtitle', recursive=False)
        for subtitle in subtitles:
            subtitle_obj = self.parse_subtitle(subtitle)
            if subtitle_obj is not None:
                subtitles_list.append(subtitle_obj)
        return subtitles_list

    def parse_section(self, section):
        if section is None:
            return None
        header = section.find('header', recursive=False)
        enum = section.find('enum', recursive=False)
        text = section.find('text', recursive=False)
        section_obj = Section(' '.join(text.text.split()) if text is not None else None, section.attrs['id'])
        section_obj.header = header.text if header is not None else None
        section_obj.enum = enum.text if enum is not None else None
        section_obj.parent = section.parent
        section_obj.add_subsection(self.parse_subsections(section))
        section_obj.add_paragraph(self.parse_paragraphs(section))
        section_obj.add_quoted_block(self.parse_quoted_blocks(section))
        return section_obj

    def parse_part(self, part):
        if part is None:
            return None
        header = part.find('header', recursive=False)
        enum = part.find('enum', recursive=False)
        text = part.find('text', recursive=False)
        part_obj = Part(' '.join(text.text.split()) if text is not None else None, part.attrs['id'])
        part_obj.add_subparts(self.parse_subparts(part))
        part_obj.add_sections(self.parse_sections(part))
        part_obj.header = header.text
        part_obj.enum = enum.text
        return part_obj

    def parse_title(self, title):
        if title is None:
            return None
        header = title.find('header', recursive=False)
        enum = title.find('enum', recursive=False)
        text = title.find('text', recursive=False)
        title_obj = Title(' '.join(text.text.split()) if text is not None else None, title.attrs['id'])
        title_obj.header = header.text
        title_obj.enum = enum.text
        title_obj.add_subtitles(self.parse_subtitles(title))
        title_obj.add_sections(self.parse_sections(title))
        return title_obj

    def parse_subtitle(self, subtitle):
        if subtitle is None:
            return None
        header = subtitle.find('header', recursive=False)
        enum = subtitle.find('enum', recursive=False)
        text = subtitle.find('text', recursive=False)
        subtitle_obj = Subtitle(' '.join(text.text.split()) if text is not None else None, subtitle.attrs['id'])
        subtitle_obj.header = ' '.join(header.text.split())
        subtitle_obj.enum = enum.text
        subtitle_obj.add_parts(self.parse_parts(subtitle))
        subtitle_obj.add_sections(self.parse_sections(subtitle))
        return subtitle_obj

    def parse_subsections(self, entry):
        ss = []
        titles = []
        if entry is None:
            return ss
        subsections = entry.find_all('subsection', recursive=False)
        for subsection in subsections:
            toc = subsection.select_one('quoted-block > toc')
            #if toc:
            #    titles = self.parse_toc(toc, entry)
            #else:
            try:
                lines = [line.strip() for line in subsection.text.splitlines()]
                header = subsection.select_one('header')
                enum = subsection.select_one('enum')
                text = subsection.find('text', recursive=False)
                subsection_obj = Subsection(' '.join(text.text.split()) if text is not None else None, subsection.attrs['id'])
                subsection_obj.header = ' '.join(header.text.split()) if header is not None else None
                subsection_obj.enum = enum.text if enum is not None else None
                subsection_obj.parent = entry
                subsection_obj.add_quoted_block(self.parse_quoted_blocks(subsection))
                subsection_obj.add_paragraphs(self.parse_paragraphs(subsection))
                ss.append(subsection_obj)
            except Exception as e:
                print(f"Error parsing subsection: {e}")
        return ss

    def parse_titles(self, entry):
        titles_list = []
        if entry is None:
            return titles_list
        titles = entry.find_all('title', recursive=False)
        for title in titles:
            title_obj = self.parse_title(title)
            if title_obj is not None:
                titles_list.append(title_obj)
        return titles_list

    def parse_paragraphs(self, entry):
        pghs = []
        if entry is None:
            return pghs
        paragraphs = entry.find_all('paragraph', recursive=False)
        for paragraph in paragraphs:

            paragraph_text = paragraph.select_one('text')
            enum = paragraph.select_one('enum')
            header = paragraph.find('header', recursive=False)
            lines = [line.strip() for line in paragraph_text.text.splitlines()]

            paragraph_obj = Paragraph(' '.join(lines), paragraph.attrs['id'])
            paragraph_obj.header = header.text if header is not None else None
            paragraph_obj.enum = enum.text if enum is not None else None
            paragraph_obj.parent = entry
            paragraph_obj.add_subparagraph(self.parse_subparagraphs(paragraph))
            paragraph_obj.add_quoted_block(self.parse_quoted_blocks(paragraph))
            pghs.append(paragraph_obj)
        return pghs

    def parse_subparts(self, entry):
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
            subpart_obj.add_sections(self.parse_sections(subpart))
            sps.append(subpart_obj)
        return sps

    def parse_subparagraphs(self, entry):
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
            subparagraph_obj.add_quoted_block(self.parse_quoted_blocks(subparagraph))
            subparagraph_obj.add_clause(self.parse_clauses(subparagraph))
            pghs.append(subparagraph_obj)
        return pghs

    def parse_quoted_blocks(self, entry):
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
            block.add_sections(self.parse_sections(quoted_block))
            block.add_subsections(self.parse_subsections(quoted_block))
            block.add_paragraphs(self.parse_paragraphs(quoted_block))
            block.add_subparagraphs(self.parse_subparagraphs(quoted_block))
            block.add_clauses(self.parse_clauses(quoted_block))
            block.add_items(self.parse_items(quoted_block))
            block.add_titles(self.parse_titles(quoted_block))
            qbs.append(block)
        return qbs

    def parse_clauses(self, entry):
        cl = []
        if entry is None:
            return cl
        clauses = entry.find_all('clause', recursive=False)
        for clause in clauses:

            clause_text = clause.select_one('text')

            lines = [line.strip() for line in clause_text.text.splitlines()]
            full_text = ' '.join(lines)

            enum = clause.select_one('enum')
            header = clause.find('header', recursive=False)
            clause_obj = Clause(full_text, clause.attrs['id'])
            clause_obj.header = header.text if header is not None else None
            clause_obj.enum = enum.text if enum is not None else None
            clause_obj.add_subclauses(self.parse_subclauses(clause))
            cl.append(clause_obj)
        return cl

    def parse_subclauses(self, entry):
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
            subclause_obj.add_items(self.parse_items(subclause))
            scl.append(subclause_obj)
        return scl

    def extract_section_identifier(self, text):
        # Regex pattern:
        # (Sec\.\s+\d+) - Captures "Sec." followed by one or more spaces, then one or more digits.
        #                 This is group 1.
        # \.\s+         - Matches the dot and space(s) immediately following the section number.
        # (.+)          - Captures the rest of the string. This is group 2.
        # pattern = r"^(Sec\.\s+\d+)\.\s+(.+)$"
        # pattern = r"^Sec\.\s+(\d+)\.\s+(.+)$"
        pattern = r"^Sec\.\s+(\d+)\.\s+(.+)$"

        match = re.match(pattern, text)

        if match:
            section_identifier = match.group(1)
            remaining_text = match.group(2)
            # print(f"Section Identifier: '{section_identifier}'")
            # print(f"Remaining Text: '{remaining_text}'")
            return section_identifier, remaining_text
        else:
            # print("No match found.")
            return None, None

    def parse_toc(self, toc, soup):
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
                    (enum, header) = self.extract_section_identifier(' '.join(full_text.split()))
                    header_text = header
                    enum_text = enum
                    tag = entry.parent.parent.parent.parent.select_one(
                        f"section:has(enum:-soup-contains(\"{enum_text}\"))")
                    idref = tag.attrs['id'] if tag is not None else idref
                if level == 'title':
                    curr_title = self.parse_title(tag)
                    titles.append(curr_title)
                    curr_subtitle = None
                    current_part = None
        return titles

    def parse_findings(self, soup):
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
            section_type = entry.name  # entry.attrs['section-type'] if entry.has_attr('section-type') else None
            header = entry.select_one('header')
            enum = entry.select_one('enum')
            header_text = ' '.join(header.text.split())
            enum_text = ' '.join(enum.text.split())
            if section_type == 'title':
                currTitle = Title(text, idref)
                currTitle.header = header_text
                currTitle.enum = enum_text
                # titles.append(currTitle)
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
                newSection.add_subsection(self.parse_subsections(entry))
                newSection.add_quoted_block(self.parse_quoted_blocks(entry))
                newSection.add_paragraph(self.parse_paragraphs(entry))

                titles.append(newSection)  # Assuming Title class can hold sections directly

                # print(f"Warning: Section '{text}' found without a parent title or subtitle")

                # if tag is not None:
                # print(' '.join(tag.text.split()))
                # print(tag.text)
                # print('\n'.join(tag.text.rsplit('\n')))
                # pass  # break
        return titles

    def parse_document(self):
        # print(result)
        toc = self.soup.select_one('section:has(header:-soup-contains("Table of contents"))')
        findings = self.soup.select_one('section:has(header:-soup-contains("Findings"))')
        if toc:
            return self.parse_toc(toc, self.soup)
        elif findings:
            return self.parse_findings(self.soup)
        else:
            return []

    def parse_items(self, entry):
        all_items = []
        if entry is None:
            return all_items
        items = entry.find_all('item', recursive=False)
        for item in items:
            item_obj = self.parse_item(item)
            if item_obj is not None:
                all_items.append(item_obj)
        return all_items

    def parse_subitems(self, entry):
        all_subitems = []
        if entry is None:
            return all_subitems
        subitems = entry.find_all('subitem', recursive=False)
        for subitem in subitems:
            subitem_obj = self.parse_subitem(subitem)
            if subitem_obj is not None:
                all_subitems.append(subitem_obj)
        return all_subitems

    def parse_item(self, item):
        if item is None:
            return None
        item_text = item.select_one('text')
        enum = item.select_one('enum')
        header = item.find('header', recursive=False)
        item_obj = Item(' '.join(item_text.text.split()) if item_text is not None else None, item.attrs['id'])
        item_obj.header = header.text if header is not None else None
        item_obj.enum = enum.text if enum is not None else None
        item_obj.add_subitems(self.parse_subitems(item))
        return item_obj

    def parse_subitem(self, subitem):
        if subitem is None:
            return None
        item_text = subitem.select_one('text')
        enum = subitem.select_one('enum')
        header = subitem.find('header', recursive=False)
        item_obj = SubItem(' '.join(item_text.text.split()) if item_text is not None else None, subitem.attrs['id'])
        item_obj.header = header.text if header is not None else None
        item_obj.enum = enum.text if enum is not None else None
        return item_obj
