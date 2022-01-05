#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 22:25:25 2021

This module provides a number of functions for the analysis of the Stanford 
Encyclopedia of Philosophy.

@author: fabianbeigang
"""

import re
import requests
from bs4 import BeautifulSoup

# For the data extraction notebook

def get_bib_elements(url):
    """
    Find and return a list of references on the provided webpage.
    

    Parameters
    ----------
    url : str
        A string containing the URL of the encyclopedia page.

    Returns
    -------
    li_elements : bs4.element.ResultSet
        A list of <li> html elements representing the individual references on the page.

    """
    
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

def extract_year(reference):
    """
    Extract the publication year from the reference.

    Parameters
    ----------
    reference : str
        A string containing the raw reference.

    Returns
    -------
    year : str
        A string containing the publication year or "forthcoming".

    """
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
    """
    Extract the list of authors from the reference.

    Parameters
    ----------
    reference : str
        A string containing the raw reference.
    year : str
        A string containing the publication year.

    Returns
    -------
    names_list : list
        A list of names of the authors of the referenced publication.

    """
    
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
     """
     Extract the title from the reference.

     Parameters
     ----------
     reference : str
         A string containing the raw reference.

     Returns
     -------
     title : str
         A string containing the title of the publication.

    """

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

def sort_names(names):
    """
    Split the list of names into two lists: one where the first name is complete,
    and one where its only initials

    Parameters
    ----------
    names : Iterable
        An iterable object of first author names.

    Returns
    -------
    full_names : list
        A list of first authors whose full first names were available.
    abr_names : list
        A list of first authors whose first names was abbreviated.

    """
    
    # Initialize empty lists for full names and for initials
    full_names = []
    abr_names = []
    
    # Sort into full and abbreviated names by checking whether what is before 
    #the first whitespace is only uppercase letters
    for name in names:
        if name.split(" ")[0].isupper():
            abr_names.append(name)
        else:
            full_names.append(name)
    
    return full_names, abr_names

def get_matches(full_names, abr_names):
    """
    Match names where only the initial of the first name is available to full names

    Parameters
    ----------
    full_names : list
        A list of first authors whose full first names were available.
    abr_names : list
        A list of first authors whose first names was abbreviated.

    Returns
    -------
    matches : list
        A list of lists where the first element is the abbreviated names, 
        the second element yet another list of matching full names.

    """    
    # Initialize a list to store matches in
    matches = []
    
    # Iterate through abbreviated names
    for name in abr_names:
        
        # extract first letter of first name and last name
        initial = name[0]
        last_name = name.split(" ")[-1]
    
        # Boolean flag to indicate whether there is a unique match
        matches_temp = []
        
        # Iterate through full name list
        for full_name in full_names:
            
            initial_f = full_name[0]
            last_name_f = full_name.split(" ")[-1]
        
            # Match if it's the same initial, same last name (+ add that first name has to have at least two letters without )
            if initial==initial_f and last_name==last_name_f:
                #print(f"Abbreviated: {name}, Full: {full_name}")
                matches_temp.append(full_name)
        # If there are any specific matches, append to match list
        if matches_temp:
            matches.append([name, matches_temp])

    return matches
    
def get_full_name(name, unique_matches):
    """
    Return the corresponding full name.

    Parameters
    ----------
    name : str
        Abbreviated name.
    unique_matches : list
        A list of lists where the first element is the abbreviated names, 
        the second element the uniquely matching full name.

    Returns
    -------
    name: str
        The full name.

    """
    
    # Check whether name is an abbreviated name
    if name.split(" ")[0].isupper():
        # Check whether there's a unique match
        for unique_match in unique_matches:
            # If the name matches, return that name
            if name==unique_match[0]:
                return unique_match[1][0]
    return name

# For the analysis notebook

def published_between(str,start_year,end_year):
    """
    Check whether a publication was published in a given year range.

    Parameters
    ----------
    str : str
        A string containing the publication year.
    start_year : int
        The beginning year of the range.
    end_year : int
        The final year of the range.

    Returns
    -------
    bool
        Truth value whether the string is a year within the range.

    """
    
    if str.isdecimal():
        if int(str) in range(start_year,end_year):
            return True
    return False








    