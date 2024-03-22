# Youtube data harvesting and warehousing using sql and streamlit
## Introduction 

* YouTube, the online video-sharing platform, has revolutionized the way we consume and interact with media. Launched in 2005, it has grown into a global phenomenon, serving as a hub for entertainment, education, and community engagement. With its vast user base and diverse content library, YouTube has become a powerful tool for individuals, creators, and businesses to share their stories, express themselves, and connect with audiences worldwide.

project objective:
  Here, I'm working on a streamlit user interface project for YOUTUBE data harvesting. Using a YouTube API key, this project retrieves data from particular YouTube channel details and stores it in a MySQL database. then it pulls data from MySQL and generates a response for each of the ten example queries. Finally, an analysis chart for the example problem I took is displayed.


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
**print library
*import pprint

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

**Voice library**
*import pyttsx3 [If necessary, but not required]

### 4. E T L Process

#### a) Extract data

* Extract the particular youtube channel data by using the youtube channel id, with the help of the youtube API developer console.

#### b) Process and Transform the data

* After the extraction process, takes the required details from the extraction data and transform it into complex JSON format.

#### c) Load  data 

* After the transformation process, the JSON format data is stored in the MySQL database.


### 5. E D A Process and Framework

#### a) Access MySQL DB 

* Create a connection to the MySQL server and access the specified MySQL DataBase by using pymysql library and access tables.

#### b) Filter the data

* Filter and process the collected data from the tables depending on the given requirements by using SQL queries and transform the processed data into a DataFrame format.

#### c) Visualization 

* Finally, create a Dashboard by using Streamlit and give dropdown options on the Dashboard to the user and select a question from that menu to analyse the data and show the output in Dataframe Table and example scatter-3D chart: I set myself a particular query.

## User Guide

#### Step 1. Data collection zone

* Search **channel_id**, copy and **paste on the input box** and click the **Extract Data to SQL** button.

#### Step 2. Channel Data Analysis zone

* **Select a Question** from the dropdown option you can get the **results in Dataframe format**.

#### Step 3. analysis zone

* select **view analysis** button and you can view the scatter-3D chart analysis for given aim mentioned above.

  
