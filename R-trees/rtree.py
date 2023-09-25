import lsh
import web_scraping as web
import time
import rtree_helper as plt
import os

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


Max_nodes=4
exp=0

#the mbr is presented by this class, it has 4 pints int x-y axis  
class Rectangle:
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

#each scientist tha i read i make him an entry and then i proceed to put him in my tree
class Entry:
    def __init__(self, surname, awards,education):
        self.surname = surname
        self.awards = awards
        self.hashed_surname = self.hash()
        self.education=education

    def hash(self):
        #simple hash method that matches the first letter of the surname to a number a=1,b=2...
        return ord(self.surname[0].lower()) - ord('a') + 1

#my node class that has information about the node 
class Node:
    def __init__(self, leaf=False):
        self.leaf = leaf #leaf or not
        self.entries = [] #the entries are stored here or the non entry nodes(python gives this option :))
        self.mbr = None #every nodes mbr
        self.parent = None # a parent pointer

    def add_entry(self, entry):
        if self.leaf:
            self.entries.append(entry) #if its a leaf we store the scientist
            entry_rect = Rectangle(entry.hashed_surname, entry.awards, entry.hashed_surname, entry.awards) #we make the mbr in order for later calculations
            if not hasattr(self, 'mbr') or not self.mbr: #if it doesnt have an mbr the mbr is the point
                self.mbr = entry_rect
            else:
                self.mbr = self.enlarg_rect(self.mbr, entry_rect) #else we enlarge the already existing mbr
        else:
            # if it isnt an entry like we said we store it again
            node = entry
            self.entries.append(node)
            node.parent = self
            #we update the mbr of the node
            if not hasattr(self, 'mbr') or not self.mbr:
                self.mbr = node.mbr
            elif node.mbr:  # Ensure node.mbr is not None
                self.mbr = self.enlarg_rect(self.mbr, node.mbr)

        if len(self.entries) > Max_nodes: #if we have more than Max_nodes we need to split our node 
            if exp==1: #2 kind of splitting methods for comparison purposes
                return self.split()
            else:
                return self.linear_split()

        return None


    def enlarg_rect(self, rect1, rect2): #simple enlargement method that finds the minimum and the maximum coordinates
        enl_xmin = min(rect1.xmin, rect2.xmin)
        enl_ymin = min(rect1.ymin, rect2.ymin)
        enl_xmax = max(rect1.xmax, rect2.xmax)
        enl_ymax = max(rect1.ymax, rect2.ymax)
        
        return Rectangle(enl_xmin, enl_ymin, enl_xmax, enl_ymax)


    def split(self): #fist simpling method 
        mid = len(self.entries) // 2 #here we do nothing more than to split the node in half
        new_node = Node(leaf=self.leaf)
        new_node.entries = self.entries[mid:]
        self.entries = self.entries[:mid]

        for entry in new_node.entries: #put the correct parent
            entry.parent = new_node


        # Update the MBRs of both nodes
        self.mbr = self.compute_mbr()  #re-compute the mbr's for each splitted node 
        new_node.mbr = new_node.compute_mbr() #complexity O(N^2)

        return new_node
    
    def linear_split(self): #This is the linear split method 
        new_node = Node(leaf=self.leaf)
        
        if self.leaf: #either if its a leaf or not we make a list of the coordinates
            x_mins = [e.hashed_surname for e in self.entries]
            y_mins = [e.awards for e in self.entries]
            x_maxs = x_mins.copy()
            y_maxs = y_mins.copy()
        else:
            x_mins = []
            y_mins = []
            x_maxs = []
            y_maxs = []
            

            for e in self.entries:
                x_mins.append(e.mbr.xmin)
                y_mins.append(e.mbr.ymin)
                x_maxs.append(e.mbr.xmax)
                y_maxs.append(e.mbr.ymax)

        #here we subtract the maximum x,y value from the minimum in order to find in which
        #axis we will sort the rectangle
        x_span = max(x_maxs) - min(x_mins)
        y_span = max(y_maxs) - min(y_mins)

        if x_span > y_span:#for x sorted based on the surname
            self.entries.sort(key=lambda e: e.hashed_surname if self.leaf else e.mbr.xmin)
        else:#for y on the awards
            self.entries.sort(key=lambda e: e.awards if self.leaf else e.mbr.ymin)

        mid = len(self.entries) // 2 #split in 2 again
        new_node.entries = self.entries[mid:]
        self.entries = self.entries[:mid]

        for entry in new_node.entries: #adjust the parent
            entry.parent = new_node 

        # Update the MBRs of both nodes
        self.mbr = self.compute_mbr() #re-compute the mbrs
        new_node.mbr = new_node.compute_mbr()

        return new_node #complexity O(N)




    def compute_mbr(self): #computing the mbr 
        if not self.entries:
            return None
        
        if self.leaf: #if its a point xmin=xmax ,ymin=ymax
            x_mins = [e.hashed_surname for e in self.entries]
            y_mins = [e.awards for e in self.entries]
            x_maxs = x_mins.copy()
            y_maxs = y_mins.copy()
        else:
            x_mins = []
            y_mins = []
            x_maxs = []
            y_maxs = []

            for e in self.entries:
                x_mins.append(e.mbr.xmin)
                y_mins.append(e.mbr.ymin)
                x_maxs.append(e.mbr.xmax)
                y_maxs.append(e.mbr.ymax)
        
        #same calculation as before but we return a rectanle object
        return Rectangle(min(x_mins), min(y_mins), max(x_maxs), max(y_maxs))
    

#our tree class   
class Rtree:
    def __init__(self):
        self.root = Node(leaf=True) #the root, its a leaf in thestart because we store entries

    def insert(self, entry):
        #when a new entry is inserted we calculate the rectangle 
        rect = Rectangle(entry.hashed_surname, entry.awards, entry.hashed_surname, entry.awards)
        #we call leaf_area to finnd the beast area for the entry to be inserted
        leaf = self.leaf_area(self.root, rect)
        #and add the the entry to the node that the leaf area method has returned
        new_node = leaf.add_entry(entry) 

        if new_node:
            #in case the add entry doesnt return None
            # and returns a spitted node we balance the tree
            self.balance_tree(leaf, new_node)



    def balance_tree(self, node, new_node):
        #rare case if the nnode is the root 
        if node == self.root:
            #we make a new_root 
            new_root = Node(leaf=False)
            #her children(the previous root is one of them)
            new_root.add_entry(node)
            new_root.add_entry(new_node)
            #we adjust the pointers
            self.root = new_root
            node.parent = new_root  
            new_node.parent = new_root
            return

        #in the other cases we propagate the split upwards
        parent = node.parent
        sibling = parent.add_entry(new_node)
        
        if sibling:
            self.balance_tree(parent, sibling)




    def leaf_area(self, node, rect):
        if node.leaf:
            #when we find the node we return it
            return node

        opt_child = None
        opt_enlarg = float('inf')#first enlargemnt is the infinity
        
        #here we search the tree for the best(minimum enlargemnt) location in order
        #to put the new entry
        for child_node in node.entries:
            if child_node.mbr:  # Ensure child_node.mbr is not None
                enlarged_mbr = child_node.enlarg_rect(child_node.mbr, rect)
                old_area = (child_node.mbr.xmax - child_node.mbr.xmin) * (child_node.mbr.ymax - child_node.mbr.ymin)
                new_area = (enlarged_mbr.xmax - enlarged_mbr.xmin) * (enlarged_mbr.ymax - enlarged_mbr.ymin)
                enlargement = new_area - old_area

                if enlargement < opt_enlarg:
                    opt_enlarg = enlargement
                    opt_child = child_node

        # Handle the scenario when opt_child is None
        if not opt_child:
            return node
                    
        return self.leaf_area(opt_child, rect) #recursive algorithm until it finds a leaf
    

    #the query method 
    def query_rtree(self, node, name_range, min_awards):
        query_result = []

        if node.leaf:
           #if it reaches a leaf it searches all the entries 
            for entry in node.entries:
                surname_first_letter = entry.surname[0].lower()
                start, end = name_range
                #ti puts the entries that we want in the list
                if start <= surname_first_letter <= end and entry.awards > min_awards:
                    query_result.append((entry.surname, entry.awards, entry.education))
        else:
            #else we search based on the mbrs for each child
            for child_node in node.entries:
                if child_node.mbr:  # we ensure child_node.mbr is not None
                    #we find the characters that the mbr is representing 
                    mbr_start = chr(child_node.mbr.xmin + ord('a') - 1)
                    mbr_end = chr(child_node.mbr.xmax + ord('a') - 1)
                    query_start, query_end = name_range

                    
                    # we check if there's an overlap between the MBR and query range
                    #and we recursively call the method until it finds the corrects mbr's
                    if not (mbr_start > query_end or mbr_end < query_start):
                        query_result.extend(self.query_rtree(child_node, name_range, min_awards))

        return query_result #return the list



def print_scientists_in_range(scientists_data, end_letter):
    #helping method nothing special
    end_letter = end_letter.upper()

    for surname, awards, education in scientists_data:
        
        if surname[0].upper() <= end_letter:
            print(f"Surname: {surname}")
            print(f"Awards: {awards}")
            print(f"Education: {education}\n") 




if __name__ == "__main__":
    tree = Rtree()

    # call the web scraper
    scientists_data=web.WebScraping()

    # Insert entries into the R-tree
    for surname, awards, education in scientists_data:
        entry = Entry(surname,awards,education)
        #print(entry.surname,entry.awards,entry.education)
        tree.insert(entry)

    while True:

        # menu
        print("\nMENU:")
        print("0 - Print Tree")
        print("1 - Range Search and LSH")
        print("2 - Plot tree")
        print("3 - Exit Program\n")
        
        # Get user choice and validate it
        while True:
            try:
                print("Please, make a choice (0-3): ")
                choice = int(input())
                if 0 <= choice <= 3:
                    break
                else:
                    print("Invalid choice. Please enter a number between 0 and 3.")
            except ValueError:
                print("Invalid input. Please enter a number between 0 and 3.")

        # Print Tree
        if choice == 0:
            plt.print_tree(tree.root)

            input("Press Enter to continue...")
            clear_terminal()

        elif choice == 1:
            # Get name range and validate it
            while True:
                start_name = input("Give the starting letter of the surname range (e.g., a): ")
                if len(start_name) == 1 and 'a' <= start_name <= 'z':
                    break
                else:
                    print("Invalid input. Please enter a single letter between 'a' and 'z'.")
        
        # Get ending name and validate it
            while True:
                end_name = input("Give the ending letter of the surname range (e.g., g): ")
                if len(end_name) == 1 and 'a' <= end_name <= 'z':
                    break
                else:
                    print("Invalid input. Please enter a single letter between 'a' and 'z'.")
            
            # Get award range and validate it
            while True:
                try:
                    print("Give the number of awards (e.g., 2):")
                    awards = int(input())
                    if 0 <= awards:
                        break
                    else:
                        print("Invalid number. Please enter a positive integer for awards.")
                except ValueError:
                    print("Invalid input. Please enter a positive integer for awards.")
        
                
            start_time = time.time()
            query_result = tree.query_rtree(tree.root, (start_name,end_name), awards)
            end_time = time.time()

            execution_time = end_time - start_time
            print(f"Execution time of query: {execution_time:.6f} seconds")
        
            for q in query_result:
                print(f"name:{q[0]} awards:{q[1]} education:{q[2]}" )
             # Print the tree and plot it
            while True:
                try:
                    similarity = float(input("Enter the desired percentage of similarity for LSH (e.g., 60): "))
                    if 0 <= similarity <= 100:
                        x = similarity / 100
                        break
                    else:
                        print("Invalid percentage. Please enter a value between 0 and 100.")
                except ValueError:
                    print("Invalid input. Please enter a valid percentage.")

                    
            similar_science=lsh.lsh(query_result,x)

            if not similar_science:
                print("No matches found.")
            else:
                for scientists in similar_science:
                    scientist1, scientist2 = scientists
                    print(f"Scientists {scientist1[0]} and {scientist2[0]} have more than {x*100}% similarity in their education.")

            input("Press Enter to continue...")
            clear_terminal()

        elif choice == 2:
            plt.plot_rtree(tree)

            input("Press Enter to continue...")
            clear_terminal()

        elif choice == 3:
            break


    