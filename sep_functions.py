#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 22:25:25 2021

This class should take the txt file and turn it into a nice pandas data frame

@author: fabianbeigang
"""

import re
import requests
from bs4 import BeautifulSoup

### For the data extraction

# Function which extracts li elements from the bibliography
def get_bib_elements(url):
    
    # Get the HTML content from that page
    r = requests.get(url)
    page = r.text
    
    # Get only the part inbetween h2 headings "Bibliography" and "Academic Tools"
    page = page.split('<div id="bibliography">')[1]
    page = page.split('<div id="academic-tools">')[0]
    soup = BeautifulSoup(page, 'html.parser')

    # Get all li elements (since references are save in li)
    li_elements = soup.findAll('li')
    
    return li_elements

# Retrieve the publication year (9999 if forthcoming, -1 if no year)
def extract_year(reference):
    # find the first regex occurrence of a four 
    # digit number starting with 1 or 2 
    try:
        year = re.findall("[1-2][0-9]{3}", reference)[0]
    except IndexError:
        if "forthcoming" in reference:
            year = "forthcoming"
        else:
            year = None
    return year

# Retrieve a list of author names of format "Beigang, F" - 
# -- here we have to control for different citation styles, some have full names
def extract_authors(reference, year):
    
    # Split at year
    names = reference.split(year)[0]
    #Remove the HTML tags
    names = BeautifulSoup(names, "lxml").text
    #Remove trailing comma (last 2)
    names = names[:-2]
    # Replace colon with comma to unify
    names = names.replace(";",",")
    
    # Gateway check that names isn't empty
    if not names:
        return ["(No names)"]
    
    # Replace "and" by comma to unify the style
    names_list = []
    names = names.replace(", and", ",")
    names = names.replace(" and", ",")
        
    # Assign first and last names to variable
    lastname_first_author = names.split(",")[0].strip()
    firstname_first_author = names.split(",")[1].strip()
        
    # Gateway check whether the name is overly long (which indicates a non-standard format and should be discarded)
    if len(f"{firstname_first_author} {lastname_first_author}")>35:
        return ["(No names)"]
    
 
    # Replace "and" by comma to unify the style
    names_list = []
    names = names.replace(", and", ",")
    names = names.replace(" and", ",")
        
    # Assign first and last names to variable
    lastname_first_author = names.split(",")[0].strip()
    firstname_first_author = names.split(",")[1].strip()
        
      
    # Add to return object
    names_list.append(f"{firstname_first_author} {lastname_first_author}")
        
    # Here I have to see whether there is one single element somewhere
        
    # BooleAn flag to see whether the names 2,..,n are in FN LN Order
    full_name = True
    
    # Check whether there is a single name element between commas (",Christian,")      
    split_up = names.split(",")[2:]
    for element in split_up:
        if len(element.strip().split(" "))==1:
            full_name = False
        

    if full_name:
        for element in split_up:
            names_list.append(element)
    else:
        for i in range(len(split_up))[::2]:
            names_list.append(f"{split_up[i+1]} {split_up[i]}")
            
        
    # Remove last empty one, if there is
    if names_list[-1]=="":
        names_list = names_list[:-1]
            
    return names_list

def extract_title(reference):
    
     # Remove newline characters from title
     title = reference.replace("\n", " ")
     
     
     try:
        # Remove the irregular beginning and end quotatopn marks
        title = title.replace(r'“', r'"')
        title = title.replace(r'”',r'"')
        # Retrieve what's inbetween the first pair of quotation marks
        title = title.split('"')[1::2][0]
        # If there is a trailing comma remove
        if title[-1]==",":
            title = title[:-1]
     except IndexError:
         try:
             # Retrieve what's inbetween ems
             title = title.replace(r'</em>', r'<em>')
             title = title.split('<em>')[1::2][0]
        # This error still has to be taken care of
         except IndexError:
             title = "(Couldn't determine title)"
    
    
     return title


### For the analysis notebook

# Return true if a publication year is within the year range, False if it is not a number or not in the range
def published_between(str,start_year,end_year):
    if str.isdecimal():
        if int(str) in range(start_year,end_year):
            return True
    return False








    