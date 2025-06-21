from parser.models import SubItem, Item, Subpart, Part, Subtitle, Title, Section, Subclause, Clause, Subparagraph, Paragraph, Subsection, QuotedBlock


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
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'paragraphs': obj.paragraphs, 'quoted_blocks': obj.quoted_blocks}
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
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'quoted_blocks': obj.quoted_blocks, 'items': obj.items}
    elif isinstance(obj, Subpart):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'sections': obj.sections}
    elif isinstance(obj, QuotedBlock):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subparagraphs': obj.subparagraphs, 'paragraphs': obj.paragraphs, 'clauses': obj.clauses, 'sections': obj.sections, 'subsections': obj.subsections, 'after_quoted_blocks': obj.after_quoted_block, 'items': obj.items, 'titles': obj.titles}
    elif isinstance(obj, Item):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum, 'subitems': obj.subitems}
    elif isinstance(obj, SubItem):
        # Return a dictionary representation of the User object
        # You can choose which attributes to include
        return {'type': obj.__class__.__name__, 'ref_id': obj.refId, 'text': obj.text, 'header': obj.header, 'enum': obj.enum}
    # You could add more isinstance checks for other custom classes here
    # For any other type it doesn't know, raise a TypeError as per default behavior
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")