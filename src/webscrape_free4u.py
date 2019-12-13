import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

cal_colleges_info = {}
cal_colleges_info["college_name"] = []
cal_colleges_info["url"] = []
cal_colleges_info["college_city"] = []
cal_colleges_info["enrollment"] = []
cal_colleges_info["tuition"] = []

def free4u_table(link):
	r = requests.get(link)
	soup = BeautifulSoup(r.content, 'lxml')

	main_table = soup.findAll('table', {"class" : "fixed"})[0]
	main_body = main_table.find('tbody')
	for college in main_body.findAll('tr'):
	    if (len(college.findAll('td')) > 0):
	        
	        # get college name
	        college_name = college.findAll('a')[0].text
	        if "-" in college_name:
	            college_name = college_name.replace("-"," ")
	        cal_colleges_info["college_name"].append(college_name)
	#print(cal_colleges_info["college_name"])

	        # get college url
	        url = college.findAll('a')[0].attrs['href']
	        url = 'https://www.free-4u.com' + url
	        cal_colleges_info["url"].append(url)
	#print(cal_colleges_info["url"])

	        # get college city
	        college_city = college.findAll('td')[1].text
	        if college_city == " ":
	            college_city = None
	        cal_colleges_info["college_city"].append(college_city)
	#print(cal_colleges_info["college_city"])
	        
	        # get enrollment
	        enrollment = college.findAll('td')[2].text
	        if enrollment == "0":
	            enrollment = None
	        cal_colleges_info["enrollment"].append(enrollment)
	#print(cal_colleges_info["enrollment"])

	        # get tuition
	        tuition = college.findAll('td')[3].text
	        if tuition == "-":
	            tuition = None
	        cal_colleges_info["tuition"].append(tuition)
	#print(cal_colleges_info["tuition"])

	return cal_colleges_info

#Create CSV database
def free4u_data(free4u_dict):
	df = pd.DataFrame(free4u_dict)
	df.columns = free4u_dict.keys()
	df.to_csv("free4u_raw_data.csv", index=0)
	print("free4u_raw_data.csv has been created!")


if __name__ == "__main__":
    print('You called me from the command line!')
    free4u_dict = free4u_table('https://www.free-4u.com/Colleges/California-Colleges.html')
    free4u_data(free4u_dict)
else:
    print(__name__ , 'was imported as a module!')
