#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
import json
import argparse
import pickle
from pathlib import Path


# ## DATA COLLECTION

# import scraper modules
import webscrape_wiki
import webscrape_free4u

# import api modules
import api_autocomplete
import api_geocode
import api_yelp

# import sqlite for final db
import sqlite3
import sql_tables
import convert_boba_data
import create_fk_list

# data visualization
import folium # need to "conda install -c conda-forge folium"
from folium import plugins
from folium.plugins import HeatMap
import maps #module

import matplotlib
import matplotlib.pyplot as plt
#%matplotlib inline
import numpy as np
import seaborn as sns



def main():
    
    parser = argparse.ArgumentParser(description= 'This is main driver.')
    # tried to use "nargs = '1' " but error
    parser.add_argument("-source", choices=["local", "remote", "test"], required = True, help="where data should be gotten from")
    args = parser.parse_args()

    location = args.source
    
    #if local: grab raw data from csv files
    if location == "local":
        #check if pickle files have been created before grabbing data
        try:
            # read pickle files as pandas df
            data_folder = Path("./data/")
            college_data = pd.read_pickle(data_folder / "college_pickle.pkl")
            boba_shops_data = pd.read_pickle(data_folder / "boba_pickle.pkl")
        #if csv files do not exist, must run remote first to create csv files
        except FileNotFoundError:
            print('Please run meng_lisa.py on remote/test first to create data files.')
            return
    #if remote: grab raw data by webscraping and API requests
    else:
        # input websites that I want scrape 
        # collect data as dictionary
        wiki_dict = webscrape_wiki.wiki_tables('https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_California')
        free4u_dict = webscrape_free4u.free4u_table('https://www.free-4u.com/Colleges/California-Colleges.html')

        # create CSV databases from raw data
        webscrape_wiki.wiki_data(wiki_dict)
        webscrape_free4u.free4u_data(free4u_dict)
        
        wiki_df = pd.read_csv('wiki_raw_data.csv')
        free4u_df = pd.read_csv('free4u_raw_data.csv')
        
    
        ## # DATA CLEANING
        
        # check for duplicate data from wiki
        wiki_df[wiki_df.duplicated(['college_name']) == True]
        # wiki data has no duplicates!
        
        # check for duplicate data from free4u
        free4u_df[free4u_df.duplicated(['college_name'], keep=False) == True]
        
        # remove duplicate data!
        #pd.set_option('display.max_rows', 300)
        updated_free4u_df = free4u_df.drop_duplicates(['college_name'], keep = 'last')
        
        # use GoogleMap API "Places Autocomplete" on both raw dataframes to get full name of colleges and place IDs to normalize
        wiki_normalize = api_autocomplete.normalize_college_name(wiki_df)
        free4u_normalize = api_autocomplete.normalize_college_name(updated_free4u_df)
    
        # add full names and place IDs into individual dataframes
        # turn off warning as I am aware I am operating on the copy of the dataframe, not original
        pd.set_option('mode.chained_assignment', None)
        wiki_df['normalize_name'] = wiki_normalize['normalize_name']
        wiki_df['place_id'] = wiki_normalize['place_id']

        updated_free4u_df['normalize_name'] = free4u_normalize['normalize_name']
        updated_free4u_df['place_id'] = free4u_normalize['place_id']
    
        # remove rows from dataframe if place_id is None because can't be used with Yelp API to find nearby boba shops
        new_wiki_df = wiki_df.dropna(subset=['place_id'])
        new_free4u_df = updated_free4u_df.dropna(subset=['place_id'])
        
        # combine dataframes
        # reset index
        concat_df = pd.concat([new_wiki_df, new_free4u_df], axis=0, sort=False).reset_index(drop=True)

        # clean duplicates by:
        # 1. group by place_id (same location/campus)
        # 2. combine duplicate rows by filling missing data in wiki with free4u data (url and tuition) (because wiki data is more up to date)
        # will use enrollment data from free4u if none in wiki
        # removed "college_name" column because no longer needed
        final_df = concat_df.groupby('place_id').agg({'normalize_name':'first',
                                                          'college_city':'first',
                                                          'enrollment': 'first',
                                                          'place_id':'first',
                                                          'url':'last',
                                                          'tuition':'last',
                                                           'year_founded':'first'
                                                     }).sort_values(by=['normalize_name']).reset_index(drop=True)
    
        # use GoogleMaps API "Geocoding" to get latitude, longitude
        coordinates_list = api_geocode.coordinates(final_df)
        
        # add coordinates to dataframe
        final_df['latitude'] = coordinates_list['latitude']
        final_df['longitude'] = coordinates_list['longitude']

        # impute missing values in city_names from city in normalized_name
        final_df['college_city'] = final_df.apply(
            lambda row: row['normalize_name'].split(",")[-3] if pd.isnull(row['college_city']) 
            else row['college_city'], axis=1)

        # store cleaned college data as pickle file
        final_df.to_pickle("college_pickle.pkl")

        # pandas read college pickle file to use data for Yelp API
        college_data = pd.read_pickle("college_pickle.pkl")

        # use Yelp API with parameters: boba (business category) within 10 mile of colleges (radius)
        # to get data on store names, rating, number of reviews, price, coordinates, and distance from colleges
        # NOTE: Yelp maxes you out at 20 stores (so total stores don't matter)
        boba_data = api_yelp.boba_shops(college_data)

        # store boba_data (type = nested dictionaty) as pickle file
        boba_pickle = open("boba_pickle.pkl", "wb")
        pickle.dump(boba_data, boba_pickle)
        boba_pickle.close()

        # pandas read boba pickle file 
        boba_shops_data = pd.read_pickle("boba_pickle.pkl")

    # use SQLite to insert both boba and college pickle dataframe into SQL data model due to relational data of colleges to boba shops
    # create SQL tables
    sql_tables.create_tables()
    print("total_data.db as been created!")

    # create separate college data into separate panda df's with foreign/primary key 
    city_name = []
    for name in college_data["college_city"]:
        if name not in city_name:
            city_name.append(name)

    # create foreign key lists
    colleges_city_id = create_fk_list.fk_dict(college_data["college_city"])

    city_fk_id = create_fk_list.city_fk_list(college_data, colleges_city_id)

    college_data = college_data.drop(columns=['college_city'])
    college_data["city_id"] = city_fk_id
    
    # add pandas df to sql Colleges and Cities table
    conn = sqlite3.connect("total_data.db")
    cur = conn.cursor()
    college_data.to_sql('Colleges', conn, if_exists='append', index = False)
    for c_name in city_name:
        cur.execute("INSERT INTO Cities (city_name) VALUES (?)", (c_name,))
    conn.commit()

    # make df for Yelp boba data to insert into SQL table
    boba_dict = convert_boba_data.boba_data_dict(boba_shops_data)   
    boba_df = pd.DataFrame.from_dict(boba_dict)
    
    # create Boba df 
    boba_table = boba_df[['store_name', 'latitude', 'longitude']]
    # filter out duplicates based on name and coordinates and fit into SQL table with primary key
    boba_table = boba_table.groupby(['store_name', 'latitude', 'longitude']).size().reset_index(name='count')
    boba_table = boba_table.rename(columns={"store_name":"shop_name"})
    boba_table = boba_table.drop(columns=['count'])
    # add primary key for None (to account for colleges with no shops nearby)
    boba_table = boba_table.append({'shop_name': None}, ignore_index=True)
    boba_table['shop_id'] = range(1,len(boba_table)+1)
    boba_table.to_sql('Shops', conn, if_exists='replace', index = False)

    # create foreign key list
    shop_fkid = boba_table.drop(columns=['latitude','longitude'])
    shop_fkid = shop_fkid.set_index(['shop_name'])
    shop_fkid = shop_fkid.to_dict()

    shop_fkid_list = []
    for shop_name in boba_df['store_name']:
        shop_fkid_list.append(shop_fkid['shop_id'][shop_name])

    boba_df['store_name'] = shop_fkid_list
    boba_df = boba_df.rename(columns={'store_name':'shop_id'})
    boba_df.to_sql('Boba_near_Colleges', conn, if_exists='replace', index = False)

    print("All clean data as been inserted into total_data.db!")

# ## DATA VISUALIZATIONS/ANALYSIS

    # read sql db as pandas df and show tables
    colleges_df = pd.read_sql_query("SELECT * from Colleges", conn)
    #colleges_df

    cities_df = pd.read_sql_query("SELECT * from Cities", conn)
    #cities_df

    shops_df = pd.read_sql_query("SELECT * from Shops", conn)
    #shops_df

    boba_near_colleges_df = pd.read_sql_query("SELECT * from Boba_near_Colleges", conn)
    #boba_near_colleges_df


    # Dot Map
    maps.dot_map(colleges_df,shops_df)
    print('Dot map has been saved as html file!')

    '''My inital thought process was plotting the colleges on a map 
    and their nearby boba/coffee shops, with a 15 mile (~24140 meter) radius,
    in order to visually see the proximity/distances between the colleges and shops,
    and to see which colleges share the same shop. 
    But as you can see, the map looks very hectic, so I then decided to use a heat map.'''

    # Heat Map
    maps.heat_map(colleges_df,shops_df)
    print('Heat map has been saved as html file!')

    ''' Although at bird-eye view, the heat map also does not seem as useful because
    I purposely gathered data about shops within a 15 mi radius of colleges, so it seems like 
    EVERYTHING near the colleges are red. But the heat map is more valuable once zooomed in. 
    Once zoomed in, you'll be able to identify more specific hotpots and notice that some
    colleges don't have as high density of boba shops as compared to others.'''

    # Merge college and boba_near_colleges df to make graphs
    df = pd.merge(colleges_df, boba_near_colleges_df, on='college_id', how='inner')

    # find corelation between how long school has been estsblished (year_founded) and amount of customers (will test with mean review count)
    ave_reviews = df[['year_founded','review_count']].groupby(by=['year_founded']).mean()
    ave_reviews.plot(title='Year colleges were founded vs Average review counts of nearby shops')

    # find r^2 to determine percentage of correlation/dependence between variables
    ave_reviews.reset_index().corr()
    # r^s = -0.077 --> insignificant dependence

    # determine if tuition or enrollment affect price of shops nearby
    df['tuition'] = df['tuition'].replace('[\$,]','', regex=True).astype(float)
    df['enrollment'] = df['enrollment'].replace(',','', regex=True).astype(float)
    price_vs_tuition = df[['price','tuition']].groupby(by=['tuition']).mean()
    price_vs_enrollment = df[['price','enrollment']].groupby(by=['enrollment']).mean()

    price_vs_tuition.plot(title='College tuition vs Price of drinks of nearby shops')
    price_vs_tuition.reset_index().corr()
    # r^2 = 0.039 --> insignificant


    # for enrollment, there is an outlier of 107,170, so it will but cutoff from analysis
    price_vs_enrollment.reset_index().plot(kind='scatter', 
                                        title = 'College enrollment vs Price of drinks of nearby shops',
                                        x='enrollment',y='price', 
                                       xlim = (0,46000), ylim=(1,2), figsize=(7,7))
    price_vs_enrollment.reset_index().corr()
    # r^2 = -0.154 --> insignificant
    ''' it is very noticable that there is a large cluster of data points for enrollment from 0-5000, 
        which shows randomess/insignificance, so will use 5000-9000 to check for correlation'''
    price_vs_enrollment.reset_index().plot(kind='scatter', 
                                        title = 'College enrollment (up to 5000) vs Price of drinks of nearby shops',
                                        x='enrollment',y='price', 
                                        xlim = (0,5000), ylim=(1,2), figsize=(7,7))

    price_vs_enrollment = price_vs_enrollment.reset_index()
    price_vs_enrollment = price_vs_enrollment[price_vs_enrollment['enrollment'] > 5000]
    price_vs_enrollment = price_vs_enrollment[price_vs_enrollment['enrollment'] < 90000].groupby(by='enrollment').mean()
    price_vs_enrollment.reset_index().corr()

    price_vs_enrollment = price_vs_enrollment.reset_index()
    sns.lmplot(x='enrollment',y='price',data=price_vs_enrollment,fit_reg=True)
    price_vs_enrollment.corr()
    # r^2 = 0.062 ---> still insignificant

    # determine if tuiton or enrollment affect rating of nearby shops
    rating_vs_tuition = df[['rating','tuition']].groupby(by=['tuition']).mean()
    rating_vs_enrollment = df[['rating','enrollment']].groupby(by=['enrollment']).mean()

    rating_vs_tuition.plot(title = 'College tuition vs Rating of nearby shops')
    rating_vs_tuition.reset_index().corr()
    # r^2 = 0.050 --> insignigicant

    rating_vs_enrollment.reset_index().plot(kind='scatter', title = 'College enrollment vs Rating of nearby shops', x='enrollment', y='rating', xlim=(0,6000))
    rating_vs_enrollment.reset_index().corr()
    # r^2 = -0.007 --> insignigicant

    ''' Assuming the more customers a shop has, the more reviews it will also have.
        I am using review_count as a varible that translates to size of customer population'''
    # determine if tuiton or enrollment affect review_count of nearby shops
    review_count_vs_tuition = df[['review_count','tuition']].groupby(by=['tuition']).mean()
    review_count_vs_enrollment = df[['review_count','enrollment']].groupby(by=['enrollment']).mean()

    review_count_vs_tuition.reset_index().plot(kind='scatter', title = 'College tuition vs Number of reviews of nearby shops', x='tuition', y='review_count', xlim=(0,None))
    review_count_vs_tuition.reset_index().corr()
    # r^2 = -0.069 -- > insignificant

    review_count_vs_enrollment.reset_index().plot(kind='scatter', title = 'College enrollment vs Number of reviews of nearby shops', x='enrollment', y='review_count', xlim=(0,None))
    review_count_vs_enrollment.reset_index().corr()
    # r^2 = -0.004 -- > insignificant

    # determine if distance from college affects amount of customers for shop
    ''' Because this graph plots the distances between colleges and each shop within a 15 mi radius, 
        it will generate too many lines on the graph, making it incomprehendable. Thus I will randomly
        choose 5 colleges and 5 shops near though colleges. But if you would like to see the code that 
        plots all the schools and shops, here it is below:

        review_count_vs_distance = df[['normalize_name','review_count','distance_from_college']].dropna().set_index('normalize_name')
        review_count_vs_distance = review_count_vs_distance.sort_values(by = 'distance_from_college')

        fig, ax = plt.subplots()
        for name, group in review_count_vs_distance.groupby('normalize_name'):
            group.plot('distance_from_college', y='review_count', ax=ax, label=name, xlim=(0,15000), ylim=(0,None))
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()'''
    review_count_vs_distance = df[['normalize_name','review_count','distance_from_college']].dropna().set_index('normalize_name')

    # shuffle df
    review_count_vs_distance = review_count_vs_distance.sample(frac=1)

    # randomly choose 5 shops from 5 colleges
    sample_df = pd.concat(
        [g.head(5) for rows, g in review_count_vs_distance.groupby(['normalize_name'], sort=False)][:5])

    # sort values to make distance ascending to make line graph, then grouby 
    sample_df = sample_df.sort_values(['normalize_name', 'distance_from_college']).groupby('normalize_name')

    fig, ax = plt.subplots()
    for name, group in sample_df:
        group.plot('distance_from_college', title = 'Distance from college vs Number of reviews of nearby shops', y='review_count', ax=ax, label=name)
     
    # move legend to outside of graph   
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig('review_count_vs_distance_linegraph.png')
    plt.show()

    ''' After all these graphs and analysis, it is clear that the attributes of a boba/coffee shop (rating, price, amount of customers('review count'))
    are not significantly correlated or dependent on the attributes of colleges (year founded, tuition, enrillment, or distance from shops).
    But as a final crap-shot, I made a scatterplot matrix to see if there are ANY possible correlations that I may have missed.
    '''

    total_df = pd.merge(df, cities_df, on='city_id', how='inner')
    total_df = pd.merge(total_df, shops_df, on='shop_id', how='inner').drop(columns=['college_id','city_id','shop_id','place_id','url','latitude','longitude','latitude_x','longitude_x', 'latitude_y','longitude_y'])
    #total_df

    ''' I am aware that my total_df has NaNs, but out of curiousity and as a final Hail Mary, I would like to see what the scatterplot matrix looks like
        to view the multiple variables at once and see if there is a correlatoin. Therefore I will silent this runtime warning.
    '''
    np.warnings.filterwarnings('ignore')

    sns.pairplot(total_df, kind="scatter")
    #save the map as an html
    plt.savefig('scatterplot_matrix.png')
    print('Scatterplot matrix has been saved as png file!')
    plt.show()

    #sadly, the scatterplot seems nonsensical and does not show any relevant correlations.


    
if __name__ == "__main__":
    main()

