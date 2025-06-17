
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