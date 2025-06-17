import json

from parser import Title, custom_encoder
from parser.USDocumentParser import USDocumentParser


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

doc = USDocumentParser('xml/BILLS-119hr1eh.xml')
titles = doc.parse_document()
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



