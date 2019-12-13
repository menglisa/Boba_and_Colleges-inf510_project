import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

cal_colleges_info = {}
cal_colleges_info["college_name"] = []
cal_colleges_info["college_city"] = []
cal_colleges_info["enrollment"] = []
cal_colleges_info["year_founded"] = []

def wiki_tables(wiki_link):
	r = requests.get(wiki_link)
	soup = BeautifulSoup(r.content, 'lxml')

	main_table = soup.findAll('table', {"class" : "wikitable sortable"})
	for tables in main_table:
	    main_body = tables.find('tbody')
	    for college in main_body.findAll('tr'):
	        if (len(college.findAll('td')) > 0):

	            #get college name
	            college_name = college.findAll('a')[0].text
	            cal_colleges_info["college_name"].append(college_name)
	#print(cal_colleges_info["college_name"])

	            #get college city
	            try:
	                location = college.findAll('a')[1].attrs['title']
	                if ', ' not in location:
	                    cal_colleges_info["college_city"].append(location)
	                else:
	                    college_city = (location.split(', '))[0]
	                    cal_colleges_info["college_city"].append(college_city)
	            except IndexError:
	                location = None
	                cal_colleges_info["college_city"].append(location)
	#print(cal_colleges_info["college_city"])

	            # get enrollment
	            try:
	                enrollment = college.findAll('td', {"align" : "center"})[0].text.strip()
	                # need to account for last 2 tables not having "enrollment" column
	                # "State graduate institutions" table is missing "enrollment" column
	                # since it is known that State Grad schools have more than a thousand students, will remove value without comma
	                if "," not in enrollment:
	                    enrollment = None
	                cal_colleges_info["enrollment"].append(enrollment)
	            # "Private colleges and universities" table missing "enrollment" column
	            except IndexError:
	                enrollment = None
	                cal_colleges_info["enrollment"].append(enrollment)
	# print(cal_colleges_info["enrollment"])

	            # get founding year
	            # first 2 tables and last 2 tables "Founded" column does not match
	            if (len(college.findAll('td')) == 5):
	                year_founded = college.findAll('td')[4].text.strip().strip("*")
	                cal_colleges_info["year_founded"].append(year_founded)
	            else:
	                year_founded = college.findAll('td')[3].text.strip()
	                if year_founded == "---":
	                    year_founded = None
	                cal_colleges_info["year_founded"].append(year_founded)
	#print(cal_colleges_info["year_founded"])

	return cal_colleges_info

#Create CSV database
def wiki_data(wiki_dict):
	df = pd.DataFrame(wiki_dict)
	df.columns = wiki_dict.keys()
	df.to_csv("wiki_raw_data.csv", index=0)
	print("wiki_raw_data.csv has been created!")

if __name__ == "__main__":
    print('You called me from the command line!')
    wiki_dict = wiki_tables('https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_California')
    wiki_data(wiki_dict)
else:
    print(__name__ , 'was imported as a module!')

