from bs4 import BeautifulSoup
import requests
import re


def WebScraping():
    
    URL = 'https://en.wikipedia.org/wiki/List_of_computer_scientists'

    response = requests.get(URL)

    soup = BeautifulSoup(response.text, 'html.parser')
    ul_elements = soup.find_all('ul')

    scientists_data = []

    # RE to match English letters only
    english_letters = re.compile(r'^[a-zA-Z\s-]+$')
    
    valuable_data=1
    # Loop the <ul> elements and extract scientist info
    for ul_element in ul_elements:
        # Find the li elements
        li_elements = ul_element.find_all('li')
        for li_element in li_elements:
            surname = ""
            awards = 0
            education = "None"
            
            text = re.sub(r'\([^)]*\)', '', li_element.get_text().strip())
            parts = text.split('–', 1)
            
            if len(parts) == 1:
                if(81<valuable_data<211):
                    name = parts[0].strip()
                    surname = name.split()[-1]
                    
                valuable_data+=1
            elif len(parts) == 2:
                name = parts[0].strip()
                surname = name.split()[-1]
                
                if parts[1].strip()!="":
                    expertise = parts[1].strip().split(',')
                    awards = len(expertise)
                    education = ', '.join(expertise)
                    
            #surname contains only English letters
            if english_letters.match(surname):
                scientists_data.append((surname, awards, education))
                      
    return scientists_data