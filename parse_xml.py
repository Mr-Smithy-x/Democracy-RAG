from bs4 import BeautifulSoup

from bs4 import XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Open the XML file and parse it with BeautifulSoup
with open('xml/BILLS-119hr1eh.xml', 'r') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find and print all tags
for tag in soup.find_all("title"):
    for child in tag.children:
        print(child.find_all_next('subtitle'))

    break



