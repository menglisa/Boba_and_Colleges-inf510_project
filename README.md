# Boba and Colleges (INF510_project)
Do colleges affect profitability of nearby boba shops?

The goal of my study was to find correlating factors/variables about colleges and how it affects the profitability of nearby boba/coffee/drink shops. 

I hoped to find a correlation that showed that some attribute of a college affects the pricing, quality, or amount of customers of a shop. 
In other words, my question is: Is the profitability of a boba/coffee shop dependent or influenced by the college it is located nearby? 
Because it is well-known that college studies drink a lot of coffee (to study) and enjoy studing at coffee shops (at least I do, and I love boba), 
my hypothesis was: If boba/coffee shops are located close to a college, then they will have higher profitability due to the student population willing to spend more (tuition), more loyal customer base (year founded, equating to how long the school has been established), larger student population (numnber of enrollment), or proximity to school which allows better access to customers (distance from college).

Thus I webscraped (from 2 websites) a list of California 4-year colleges and universities, along with attributes I thought were meaningful, such as year the college was founded, tuition costs, number of enrollment, and location (city/address). I then used the Google Maps Autocomplete API to normalize the college names and obtain its unique place ID. Using another Google Maps Geocode API, I converted the unique place ID to coordinates (latitude and longitude). With the coordinates, I used Yelp API to find nearby boba/coffee shops within a 15 mile radius and collected data about their price, rating, review count, and distance from the colleges. (Assuming the more customers a shop has, the more reviews it will also have. Thus I a decided to use review count as a varible that measures size of a shop's customer population.)

Initially, I wanted to see the location of each college and shop on a map. So I made a dot map of California with a circle around each college representing a 15 mile radius, but it was hectic-looking and did not provide a lot of information. Then, I decided to make a heat map. When zoomed it, not only was it more aesthetic pleasing, but you are able to identify specific hotspots and view which colleges had a higher density of boba shops compared to others.

Since I am testing one college variable and one boba/coffee shop at a time, I performed a correlation study. And because my independent variables (college attributes) and dependent variables (shop attributes) are continuous, I decided to use line graphs and scatter plots as my visualizations to check for correlation, and used the Pearson method to determine the R^2 value to test for correlation

To test for correlation, I graphed the year which the colleges were founded vs. the average number of customer reviews, college tuition vs. average prices, college enrollment vs. average prices, college tuition vs. average rating, college enrollment vs. average rating, college tuition vs. average number of customer reviews, college enrollment vs. average number of customer reviews, and finally distance from college vs. average number of customer reviews, which ALL showed no dependency (according to the graph and R^2 values).

Thus as a Hail Mary, I decided to use a scatterplot matrix so I can visually see all at once the multiple variables and check if I missed any possible correlations between them. But unfortunately, the scatterplot matrix further suggested no correlation.

Ultimitely, my findings suggest that college attributes, such as tuition (student population willing to spend more), year founded (equating to how long the school has been established in order to develop a more loyal customer base), number of enrollment (larger student population), or distance from college (proximity to school which allows better access to customers) did not affect or influence profitability of nearyby boba/coffee shops, which was measure with price, rating, and review count. Therefore, my project validated the null hypothesis, that there is no correlation (or effect) between colleges and profitability of near by shops.

# How to run my code
This project requires the following packages:
pandas, numpy, seaborn, requests, beautifulsoup, json, pickle, pathlib, matplotlib, sqlite3, lxml, and folium

** Please note that Folium is not in the default Anaconda repository so it MUST be installed prior to running: conda install -c conda-forge folium. Or create environment (environment.yml in inf510_project repo).

When creating environment, cd into inf510_project folder first!
To run this project, make sure the above packages are installed, and then simply clone the repo and execute the Jupyter notebook. (You can read through the written section for a more in depth description of my project).

The "src" folder contains meng_lisa.py (main driver), modules to webscrape and run the APIs, data cleaning and pre-processing functions, and code to build the map and SQL database.
The "data" folder contains CSVs of webscaped college data, html of the maps, images of statistical anaylsis graphs, and pickle files of college and boba data. 
