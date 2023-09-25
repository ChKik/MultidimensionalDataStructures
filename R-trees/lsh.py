#lsh
import random


def shingle(text, k=2): #we make the education text into k shingles
    return {text[i:i+k] for i in range(len(text) - k + 1)}


def jaccard(s1,s2):#the jaccard method that gives us how similar are 2 sets
    intersect_size=len(s1.intersection(s2))
    union_size=len(s1.union(s2))

    return intersect_size/union_size

def func_hash(a,b,modulo): #hash function creator
    return lambda x:(a*x+b)%modulo

def minhash(shingles,hashes=50): #the minhash method
    max_hash=2**32-1 #hash of 32 bits
    modulo=2**32

    funcs=[] #we make hashes hash funnctions
    for _ in range(hashes):
        a, b = random.randint(0, max_hash), random.randint(0, max_hash)
        func=lambda x,a=a,b=b:(a*hash(x)+b)%modulo
        funcs.append(func)

    sign_x=[min([f(shingle) for shingle in shingles]) for f in funcs] #and then for each hash function we calculate the minimun shingle

    return sign_x #we return the list on minimum shingles for each function

def backet_creator(sign,bands,rows): #we then create our buckets
    buckets=[]
    for band in range(bands):
        start = band * rows
        end = (band + 1) * rows
        buckets.append(hash(tuple(sign[start:end])))
    return buckets

def lsh(query, threshold):
    shingles = [shingle(entry[2]) for entry in query] #we calculate all the shingles and signatures of the education strings
    
    signatures = [minhash(s) for s in shingles]

    bands = 10
    rows = 10
    buckets = [backet_creator(sign, bands, rows) for sign in signatures] #we create the buckets

    pairs = set()

    for i, buckets1 in enumerate(buckets): #for the buckets we create pairs in order to test the jaccard method for each pair
        for j, buckets2 in enumerate(buckets):
            if i != j and any(b1 == b2 for b1, b2 in zip(buckets1, buckets2)):
                if i < j:
                    pairs.add((i, j))
                else:
                    pairs.add((j, i))

    final_pairs = []
    for i, j in pairs: #for ecach pair we test the  jaccard similarity of its shingles 
        similarity = jaccard(shingles[i], shingles[j])
    #and then if the similarity is above a specific threshold we add the pair to our result
        if similarity >= threshold:
            #i,j are the scientist we want beause there is 1-1 match between the shingles and the query
            final_pairs.append((query[i], query[j]))

    return final_pairs