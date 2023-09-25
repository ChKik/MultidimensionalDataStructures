# The logic behind this quadtree is that x-axis will contain one of the 26 letters of the
# english alphabet,while the y-axis will contain the # of awards
# Letter A->1
# Letter Z->26


import re
import requests
from bs4 import BeautifulSoup
import csv
import random


def shingle(text, k=2):
    return {text[i:i+k] for i in range(len(text) - k + 1)}

def jaccard(s1,s2):
    intersect_size=len(s1.intersection(s2))
    union_size=len(s1.union(s2))
    return intersect_size/union_size

def func_hash(a,b,modulo):
    return lambda x:(a*x+b)%modulo

def minhash(shingles,hashes=50):
    max_hash = 2 ** 32 - 1  # hash of 32 bits
    modulo = 2 ** 32

    funcs = []
    for _ in range(hashes):
        a, b = random.randint(0, max_hash), random.randint(0, max_hash)
        func = lambda x, a=a, b=b: (a * hash(x) + b) % modulo
        funcs.append(func)

    sign_x = [min([f(shingle) for shingle in shingles]) for f in funcs]

    return sign_x


def bucket_creator(sign, bands, rows):
    buckets = []
    for band in range(bands):
        start = band * rows
        end = (band + 1) * rows
        buckets.append(hash(tuple(sign[start:end])))
    return buckets


def lsh(query, threshold):
    shingles = [shingle(entry[2]) for entry in query]



    signatures = [minhash(s) for s in shingles]


    bands = 10
    rows = 10
    buckets = [bucket_creator(sign, bands, rows) for sign in signatures]

    pairs = set()

    for i, buckets1 in enumerate(buckets):
        for j, buckets2 in enumerate(buckets):
            if i != j and any(b1 == b2 for b1, b2 in zip(buckets1, buckets2)):
                if i < j:
                    pairs.add((i, j))
                else:
                    pairs.add((j, i))

    final_pairs = []
    for i, j in pairs:
        similarity = jaccard(shingles[i], shingles[j])
        print(f"this is the similarity: {similarity}")
        if similarity >= threshold:
            final_pairs.append((query[i], query[j]))
    print("ftaneis edw?")
    return final_pairs


def WebScraping():
    # Web scraping in wiki page
    URL = 'https://en.wikipedia.org/wiki/List_of_computer_scientists'

    response = requests.get(URL)

    soup = BeautifulSoup(response.text, 'html.parser')
    ul_elements = soup.find_all('ul')

    scientists_data = []

    # RE to match English letters only
    english_letters = re.compile(r'^[a-zA-Z\s-]+$')

    valuable_data = 1
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
                if (81 < valuable_data < 211):
                    name = parts[0].strip()
                    surname = name.split()[-1]

                valuable_data += 1
            elif len(parts) == 2:
                name = parts[0].strip()
                surname = name.split()[-1]

                if parts[1].strip() != "":
                    expertise = parts[1].strip().split(',')
                    awards = len(expertise)
                    education = ', '.join(expertise)

            # surname contains only English letters
            if english_letters.match(surname):
                scientists_data.append((surname, awards, education))

    # eisagwgh sto csv
    csv_filename = "scientists_data.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write header
        csv_writer.writerow(["Surname", "#Awards", "Education"])
        # Write scientist data
        csv_writer.writerows(scientists_data)
    return scientists_data


def CharAsciiToRange(
        z):  # check if the input is in uppercase letters otherwise turn it into an uppercase letter # becasue it's a name.
    if (z.isupper()) == False:
        upperstring = z.upper()
    else:
        upperstring = z
    temp = ord(upperstring) - ord('A') + 1  # 65 is the polarization for the number,+1 to get it in range [1,26]
    if (temp > 26 or temp < 1):
        print("The letter does not belong to the English Alphabet")
        exit(0)
    # print(f"{z} --> {temp}")
    return temp


class Point:  #(x,y)
    def __init__(self, x, y):
        self.x = x
        self.y = y


class QuadTreeNode:  # self is used for accessing the methods and attributes of the Class
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.points = []
        self.children = [None, None, None, None]

    def insert(self, point):
        if not self.boundary(point):
            return

        if len(self.points) < 4:  # 4 because it's a quadtree. Fills the child with max 4 points and then subdivides. There are other trees with different # of children
            self.points.append(point)
        else:
            if self.children[0] is None:
                self.subdivide()

            for child in self.children:
                child.insert(point)

    def subdivide(self):
        half_width = self.width / 2  # takes the starting width and height and divides it to create new quadtrees
        half_height = self.height / 2 #that have this parameter as width and height
        x = self.x
        y = self.y

        # new instance of quadtree
        self.children[0] = QuadTreeNode(x, y, half_width, half_height)
        self.children[1] = QuadTreeNode(x + half_width, y, half_width, half_height)
        self.children[2] = QuadTreeNode(x, y + half_height, half_width, half_height)
        self.children[3] = QuadTreeNode(x + half_width, y + half_height, half_width, half_height)

    def boundary(self, point):  # checks if the point added is inside the boundary, set by the quadtree(27,100 in our case)
        return (
                self.x <= point.x < self.x + self.width and
                self.y <= point.y < self.y + self.height
        )

    def query_range(self, range_x,
                    range_y):  # searches for every point that is within the arguments given and returns it
        results = []
        if not (self.x < range_x[0] + range_x[1] and self.x + self.width > range_x[0] and   #first check that that x given is inside the range of the tree otherwise return the current results
                self.y < range_y[0] + range_y[1] and self.y + self.height > range_y[0]):
            return results

        for point in self.points:
            if range_x[0] <= point.x < range_x[0] + range_x[1] and range_y[0] <= point.y < range_y[0] + range_y[1]:
                results.append(point)      #if it is inside the range and append the point to the return query

        if self.children[0] is not None:
            for child in self.children:
                results.extend(child.query_range(range_x, range_y))   #checks if there are children created and recursively uses query range to the children.

        return results


if __name__ == "__main__":
    scientist_list = []
    scientist_list = WebScraping()
    scientist_len = len(scientist_list)

    modscilist = scientist_list[:scientist_len]  # ModdedScientistList
    for i in range(scientist_len):
        modscilist[i] = scientist_list[i][:2]  # takes the name and #of awards only

    firstletter = []  # first letter of each scientist
    for x in range(scientist_len):
        firstletter.append(modscilist[x][0][0])

    awardsonly = []  # number of awards
    for x in range(scientist_len):
        awardsonly.append(modscilist[x][1])

    asciifirst = []
    for x in range(scientist_len):
        asciifirst.append(CharAsciiToRange(firstletter[x]))

    root = QuadTreeNode(0, 0, 27, 100)  # 26 letters and max 100 awards
    for x in range(scientist_len):
        root.insert(Point(asciifirst[x], awardsonly[x]))

    # 65-90 ascii range of english capital letters
    print("Give the space of characters you want returned ")
    x1 = input("Give the lower character boundary: ")
    x2 = input("Give the upper character boundary: ")
    intx1 = CharAsciiToRange(x1)
    intx2 = CharAsciiToRange(x2)
    numberofawards = input(
        "Give a number of minimum awards you want the scientist to have(max 100): ")  # max exei 10 kapoios
    intNoA = int(numberofawards) + 1
    query_result = root.query_range((intx1, intx2), (intNoA - 1, 100))
    print("Result points in the query range:", [(p.x, p.y) for p in query_result])

    results_scientist_list = []
    results_query_list = []
    for p in query_result:
        results_query_list.append([p.x, p.y])

    used_keys = set()  # to ensure there are no duplicate values in the final list

    for x in range(len(results_query_list)):
        for j in range(scientist_len):
            if (results_query_list[x][0] == asciifirst[j] and
                results_query_list[x][1] == awardsonly[j] and
                j not in used_keys):  # if the letters and the # of awards match append the result
                results_scientist_list.append(scientist_list[j])
                used_keys.add(j)

    for x in range(len(results_scientist_list)):
        print(
            f'Name: {results_scientist_list[x][0]} || Awards: {results_scientist_list[x][1]} || Education: {results_scientist_list[x][2]}')

    AFF22 = input("Press any key to continue to LSH and clear the screen.")
    print("\n" * 50)

    #LSH
    similarity_percentage = input("Give the similarity percentage you want with max of 1 e.x 0.2: ")
    similarity_float = float(similarity_percentage)
    similar_science = lsh(results_scientist_list, similarity_float)


    for scientists in similar_science:
        scientist1, scientist2 = scientists
        print(
            f"Scientists {scientist1[0]} and {scientist2[0]} have more than {similarity_float * 100}% similarity in their education.")

