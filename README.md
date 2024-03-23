# Youtube data harvesting and warehousing using sql and streamlit
## Introduction 

* YouTube, the online video-sharing platform, has revolutionized the way we consume and interact with media. Launched in 2005, it has grown into a global phenomenon, serving as a hub for entertainment, education and community engagement with its vast user base and diverse content library. YouTube has become a powerful tool for individuals, creators, and businesses to share their stories, express themselves, and connect with audiences worldwide.

## project objective:
  * Here, I completed a streamlit user interface project for YouTube data gathering and warehousing. This project pulls data from YouTube and saves it in a MySQL database using a YouTube API key. then it retrieves information from MySQL and produces a reply for every one of the ten sample queries. Lastly, a chart of analysis for the sample problem that I chose is shown.


## Developer Guide 

### 1. Tools Install

* Visual Studio.
* Python 3.11.0 or higher.
* MySQL.
* Youtube API key.

### 2. Requirement Libraries to Install

* pip install google-api-python-client, pymongo, mysql-connector-python, pymysql, pymysql, pandas, numpy, 
  plotly-express, streamlit.
  
 ( pip install google-api-python-client pymongo mysql-connector-python sqlalchemy pymysql pandas numpy plotly-express streamlit )
 
### 3. Import Libraries
**print library**
* import pprint

**Youtube API libraries**
* import googleapiclient.discovery
* from googleapiclient.discovery import build

**File handling libraries**
* import json
* import re

**SQL libraries**
* import mysql.connector
* import pymysql

**Datetime library**
* from datetime import datetime

**pandas, numpy**
* import pandas as pd
* import numpy as np

**Dashboard libraries**
* import streamlit as st
* import plotly.express as plt

### 4. E T L Process

#### a) Extract data

* Using the YouTube channel id and the YouTube API developer console, get the specific YouTube channel data.Using the playlist id, further video data can also be extracted from a specific channel.

#### b) Process and Transform the data

* Takes the necessary information from the extracted data and converts it into a complex JSON format after the extraction process.

#### c) Load  data 

* Create the required tables and database after the transformation process. then an insert query is used to store that complex JSON data in the MySQL database.

  
### 5. E D A Process and Framework

#### a) Access MySQL DB 

* Using the pymysql library and access tables, establish a connection to the MySQL server and get access to the specified MySQL DataBase.

#### b) Filter the data

* Apply SQL queries to process the information obtained from the tables in accordance with the given questions. Next, create a DataFrame format out of the processed data.

#### c) Visualization 

* Finally, make use of Streamlit to build a dashboard. Provide the user with dropdown options on the dashboard. Next, I was given a task to analyze the data for myself and see the outcomes in a Dataframe Table and a sample scatter-3D image.

## User Guide

#### Step 1. Data collection zone

* Search **channel_id**, copy and **paste on the input box** and click the **Extract Data to SQL** button.

#### Step 2. Channel Data Analysis zone

* **Select a Question** from the dropdown option you can get the **results in Dataframe format**.

#### Step 3. analysis zone

* By clicking the **view analysis** button, you can see the scatter-3D chart analysis for the above-mentioned problem.


  
