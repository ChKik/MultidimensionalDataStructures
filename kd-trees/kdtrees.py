import sys
import requests
import csv
import re
import random
import time
from bs4 import BeautifulSoup

# Number of dimensions
k = 2

# A structure to represent node of kd tree
class Node:
	def __init__(self, point):
		self.point = point
		self.surname = point[0]
		self.awards = point[1]
		self.education = point[2]
		self.left = None
		self.right = None
  
def WebScraping():
    # Web scraping in wiki page
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
                      
    #eisagwgh sto csv       
    csv_filename = "scientists_data.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write header
        csv_writer.writerow(["Surname", "#Awards", "Education"])
        # Write scientist data
        csv_writer.writerows(scientists_data)
    return scientists_data

# A method to create a node of K D tree
def newNode(point):
	return Node(point)

# Inserts a new node and returns root of modified tree
# The parameter depth is used to decide axis of comparison
def insertRec(root, point, depth):
	# Tree is empty?
	if not root:
		return newNode(point)
	
	# Calculate current dimension (cd) of comparison
	cd = depth % k
	 
	# Compare the new point with root on current dimension 'cd' and decide the left or right subtree
	if point[cd] < root.point[cd]:
		root.left = insertRec(root.left, point, depth + 1)
	else:
		root.right = insertRec(root.right, point, depth + 1)

	return root

# Function to insert a new point with given point in KD Tree and return new root. It mainly uses above recursive function "insertRec()"
def insert(root, point):
	return insertRec(root, point, 0)

# A utility method to determine if two Points are same in K Dimensional space
def arePointsSame(point1, point2):
	# Compare individual coordinate values
	for i in range(k):
		if point1[i] != point2[i]:
			return False

	return True

# Searches a Point represented by "point[]" in the K D tree.
# The parameter depth is used to determine current axis.
def search_pointRec(root, point, depth):
	# Base cases
	if not root:
		return False
	if arePointsSame(root.point, point):
		return True

	# Current dimension is computed using current depth and total dimensions (k)
	cd = depth % k

	# Compare point with root with respect to cd (Current dimension)
	if point[cd] < root.point[cd]:
		return search_pointRec(root.left, point, depth + 1)

	return search_pointRec(root.right, point, depth + 1)

# Searches a Point in the K D tree. It mainly uses searchRec()
def search_point(root, point):
	# Pass current depth as 0
	return search_pointRec(root, point, 0)

def findRec(root, first_letter, last_letter, awards, array, depth):
    # Base case: If the root is None, return
    if not root:
        return

    # Calculate current dimension (cd) of comparison
    cd = depth % k

    # Check if the surname's first letter is within the specified range
    if first_letter <= root.surname[0] <= last_letter and root.awards >= awards:
        array.append((root.surname, root.awards, root.education))

    # Recursively search both left and right subtrees based on the current dimension
    if cd == 0:
        if first_letter > root.surname[0]:
            findRec(root.right, first_letter, last_letter, awards, array, depth + 1)   
        elif first_letter <= root.surname[0] <= last_letter:
            findRec(root.left, first_letter, last_letter, awards, array, depth + 1)    
            findRec(root.right, first_letter, last_letter, awards, array, depth + 1)
        else:
            findRec(root.left, first_letter, last_letter, awards, array, depth + 1)
    elif cd == 1:
        if awards >= root.awards:
            findRec(root.right, first_letter, last_letter, awards, array, depth + 1)
        else:
            findRec(root.left, first_letter, last_letter, awards, array, depth + 1) 
            findRec(root.right, first_letter, last_letter, awards, array, depth + 1)
    else:
        print("Something went wrong! Current dimension took wrong value outside of dimension value range [0,k-1].")
    
    return

def find_range(root, first_letter, last_letter, awards, array):
	# Pass current depth as 0
	return findRec(root, first_letter, last_letter, awards, array, 0)

def find_specific(root, letter, awards, array):
	return find_range(root, letter, letter, awards, array)

def shingle(text, k=2):
    return {text[i:i+k] for i in range(len(text) - k + 1)}

def jaccard(s1,s2):
    intersect_size=len(s1.intersection(s2))
    union_size=len(s1.union(s2))
    #print(f"{intersect_size/union_size} this is the score")
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

def backet_creator(sign, bands, rows):
    buckets = []
    for band in range(bands):
        start = band * rows
        end = (band + 1) * rows
        buckets.append(hash(tuple(sign[start:end])))
    return buckets

def lsh(query, threshold):
    shingles = [shingle(entry[2]) for entry in query]

    # for i in range(5):  # adjust as needed testing
    # print(f"Entry {i}: {shingles[i]}")

    signatures = [minhash(s) for s in shingles]

    # for i in range(5):  # adjust as needed testing
    # print(f"Signature {i}: {signatures[i]}")

    bands = 10
    rows = 10
    buckets = [backet_creator(sign, bands, rows) for sign in signatures]

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
        #print(f"This is the similarity: {similarity}")
        if similarity >= threshold:
            final_pairs.append((query[i], query[j]))
            
    #print()
    
    return final_pairs

# Driver program to test above functions
if __name__ == '__main__':
    root = None
    
    points = []
    
    try:
        points = WebScraping()
    except requests.exceptions.ConnectionError:
        print("There has been an connection error. Please check your network!")
        sys.exit(1)
    
    n = len(points)
    
    for i in range(n):
        root = insert(root, points[i])
        
    results = []
    
    try:
        awards = int(input("Give the least amount of awards the scientists should have: "))
        print()
    except ValueError:
        print("Invalid number of awards. Please enter a valid integer!")
    
    while True:
        option = input("Type <range> if you want a range of letters otherwise type <specific> if you want a specific one: ")
        print()
        
        if(option == "range"):
            first_letter = str.upper(input("Type the first letter of the range: "))
            last_letter = str.upper(input("Type the last letter of the range: "))
            print()
            
            start_time = time.time()
            find_range(root, first_letter, last_letter, awards, results)
            end_time = time.time()
            break
        elif(option == "specific"):
            letter = str.upper(input("Give the letter that the surname of the scientists start with: "))
            print()
            start_time = time.time()
            find_specific(root, letter, awards, results)
            end_time = time.time()
            break
        else:
            print("Wrong option! Type <range> or <specific>!")
            print()
    
    elapsed_time = end_time - start_time
    
    print("Scientists with the specified characteristics")
    print("---------------------------------------------------------------------------------------------------------")
    
    for result in results:
        print(f"Surname: {result[0]}, Awards: {result[1]}, Education: {result[2]}")
    
    print("---------------------------------------------------------------------------------------------------------")
    print()
    
    similarity_percentage = float(input("Give the similarity percentage x, where 0<=x<=1: "))
    print()
    
    similar_science = lsh(results, similarity_percentage)

    #print("this is the query:")
    #print(similar_science)
    #print()

    for scientists in similar_science:
        scientist1, scientist2 = scientists
        print(f"Scientists {scientist1[0]} and {scientist2[0]} have more or equal than {similarity_percentage * 100}% similarity in their education.")
    
    print()
    
    print("Previous scientists that have the required similarity")
    print("---------------------------------------------------------------------------------------------------------")
    
    for scientists in similar_science:
        for i in range(2):
            print(f"Surname: {scientists[i][0]}, Awards: {scientists[i][1]}, Education: {scientists[i][2]}")
    
    print("---------------------------------------------------------------------------------------------------------")
    print()
    
    print(f"Elapsed time: {elapsed_time} seconds")