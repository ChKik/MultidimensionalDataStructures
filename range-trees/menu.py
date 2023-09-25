import csv
import re
import requests
from bs4 import BeautifulSoup
import main as m
import my_lsh as lsh
import time


#### Functions ####

# gia tin print tree: pre-order traversal
def pre_order(root, string=""):
    if root:
        print(string + str(root.coords) + "|Name:" + str(root.name))
        pre_order(root.left, "\t" + string + "-left-")
        pre_order(root.right, "\t" + string + "-right-")


# gia tin range search: print result
def print_nodes(nodes_list):
    for node in nodes_list:
        print(str(node.coords) + "\t|\tName:" + str(node.name))


#### Menu ####
my_nodes = []
nodes_counter = 0


# Function to perform web scraping
def perform_web_scraping():
    URL = 'https://en.wikipedia.org/wiki/List_of_computer_scientists'
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize a list to store scraped data
    scientists_data = []

    # Regular expression pattern to match English letters and spaces
    english_letters = re.compile(r'^[a-zA-Z\s-]+$')

    # Find relevant elements and extract data
    for li_element in soup.select('div.mw-parser-output ul li'):
        text = li_element.get_text(strip=True)

        # Check if the text contains a hyphen
        if '–' in text:
            name_parts = text.split('–', 1)
            name = name_parts[0].strip()
            surname = name.split()[-1]
            if english_letters.match(surname):
                expertise = name_parts[1].strip().split(',')
                awards = len(expertise)
                education = ', '.join(expertise)
                scientists_data.append([surname, awards, education])

    return scientists_data


# Function to save data to a CSV file
def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Surname", "#Awards", "Education"])
        csv_writer.writerows(data)


# Perform web scraping
scientists_data = perform_web_scraping()

# Save data to CSV file
csv_filename = 'scientists_data.csv'
save_to_csv(scientists_data, csv_filename)

# Diavazoume to arxeio kai dimiourgoume kateytheian node objects
with open(csv_filename, mode='r', encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')  # Use ',' as the delimiter
    header = next(csv_reader)
    for row in csv_reader:
        my_nodes.append(m.Node([row[0].replace(',', '.'), int(row[1].replace(',', '.'))], row[2]))
        nodes_counter += 1
    print('Number of Nodes: ' + str(nodes_counter))

# Sortaroume tis syntetagmenes twn komvwn kai ftiaxnoume to dentro
sorted_nodes = sorted(my_nodes, key=lambda l: (l.coords[0], l.coords[1]))
my_root, _ = m.create_range_tree(sorted_nodes)

while True:

    # Menu gia tis diadikasies tou dentrou
    print("\nMENU:")
    print("0 - Print Tree")
    print("1 - Range Search and LSH")
    print("-1 - Exit Program\n")
    print("Please,make a choice: ")
    choice = int(input())

    # Print Tree
    if choice == 0:
        print('-----------------------')
        pre_order(my_root)
        print('-----------------------')

    # Range Search
    elif choice == 1:
        my_range = []

        # Record the start time
        start_time = time.time()

        for d in range(m.DIMENSIONS):
            d_range = []

            if d == 0:
                print("Give min coordinate for dimension " + str(d+1))
                d_range.append(input())
                print("Give max coordinate for dimension " + str(d+1))
                d_range.append(input())

            elif d == 1:  # Second dimension (awards)
                print("Give min coordinate for dimension " + str(d + 1))
                d_range.append(input())
                # Set the default max coordinate for the second dimension (awards) to 100
                d_range.append(100)  # Default maximum awards value

            my_range.append(d_range)
        print('-----------------------')

        res_list = m.range_search(my_root, my_range)

        if len(res_list) == 0:
            print('-----------------------')
            print("Not Found!")
            print('-----------------------')

        else:
            print('-----------------------')
            print('Nodes found (' + str(len(res_list)) + ')')
            print_nodes(res_list)
            print('-----------------------')

        AFF22 = input("Press any key to continue to LSH and clear the screen.")

        # LSH
        similarity_percentage = input("Give the similarity percentage you want with max of 1 e.x 0.2: ")
        similarity_float = float(similarity_percentage)
        # Create a list of names and education data to pass to lsh
        similar_science = lsh.lsh(res_list, similarity_float)

        #Gia na kanw rid of ta duplicates
        unique_pairs = set()
        for scientists in similar_science:
            scientist1, scientist2 = scientists
            name1, name2 = scientist1.coords[0], scientist2.coords[0]
            similarity_percentage = similarity_float * 100
            similarity_message = f"Scientists {name1} and {name2} have more than {similarity_percentage:.1f}% similarity in their education."

            # Check if the pair is not in unique_pairs, then print and add it
            if (name1, name2) not in unique_pairs and (name2, name1) not in unique_pairs:
                print(similarity_message)
                unique_pairs.add((name1, name2))

        # Calculate and print the execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.2f} seconds")

    elif choice == -1:
        exit(0)

choice = int(input())