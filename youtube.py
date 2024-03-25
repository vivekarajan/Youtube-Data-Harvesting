import streamlit as st
import googleapiclient.discovery
import googleapiclient.errors
import pprint
import pandas as pd
import mysql.connector
from datetime import datetime
import re
import plotly.express as plt

connection = mysql.connector.connect(
        host='host',
        user='user',
        password="pswd",
        database="dbname"
    )
cur = connection.cursor()

#------------------------------------------------------------------------------------------------------------------

def convert_duration_to_seconds(duration_str):
    # Extract hours, minutes, and seconds using regular expressions
    hours_match = re.search(r"PT(\d+)H", duration_str)
    minutes_match = re.search(r"(\d+)H(\d+)M", duration_str)
    seconds_match = re.search(r"(\d+)M(\d+)S", duration_str)
    
    # Initialize hours, minutes, and seconds
    hours = 0
    minutes = 0
    seconds = 0
    
    # Convert hours if available
    if hours_match:
        hours = int(hours_match.group(1))
    
    # Convert minutes if available
    if minutes_match:
        minutes = int(minutes_match.group(1))
    
    # Convert seconds if available
    if seconds_match:
        seconds = int(seconds_match.group(1))
    
    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds

#------------------------------------------------------------------------------------------------------------------
def extract_date_and_time(datetime_str):
    # Original datetime string
    datetime_str = datetime_str
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    # Format the datetime object for MySQL insertion
    formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime
#--------------------------------------------------------------------------------------------------------------
# Function to fetch channel info
def channel_info(res_channel, res_playlist):
    
    title = res_channel['items'][0]['snippet']['localized']['title']
    channel_id = res_channel['items'][0]['id']
    subscription_count = res_channel['items'][0]['statistics']['subscriberCount']
    channel_views = res_channel['items'][0]['statistics']['viewCount']
    channel_description = res_channel['items'][0]['snippet']['description']
    if '\n' in channel_description:
        channel_description = channel_description.split('\n')[2] if len(channel_description.split('\n')) > 2 else ""
    else:
        channel_description = ""
    playlist_id = res_playlist['items'][0]['id']
    playlist_name = res_playlist['items'][0]['snippet']['title']

    channeldet = {}
    channel_details = {
      "Channel_Name": title,
      "Channel_Id": channel_id,
      "Subscription_Count": subscription_count,
      "Channel_Views": channel_views,
      "Channel_Description": channel_description,
      "Playlist_Id": playlist_id,
      "Playlist_Name": playlist_name 
    }
    channeldet[f'{title}'] = channel_details
    return channeldet

# Function to fetch comments for a video
def fetch_comments(youtube, video_id):
    comments_response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()

    comments_data = comments_response.get('items', [])
    formatted_comments = {}
    comment_index = {}
    for index, comment in enumerate(comments_data, start=1):
        comment_details = {
            'Comment_Id': comment['id'],
            'Comment_Text': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
            'Comment_Author': comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            'Comment_PublishedAt': comment['snippet']['topLevelComment']['snippet']['publishedAt']
        }
        comment_index = comment_details
        formatted_comments['Comments'] = comment_index
    return formatted_comments

def video_details(youtube, response):
    # getting video dict
    data = response

    # Get the list of video items from that dict
    items = data.get('items', [])

    video_details = {}
    for index, item in enumerate(items, start=1):
        video_id = item.get('id', '') 
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        #using fetch_comments getting comment details for each video
        comments = fetch_comments(youtube, video_id)
        details = {
            'Video_Id': video_id,
            'Video_Name': snippet.get('title', ''),
            'Video_Description': snippet.get('description', ''),
            'Tags': snippet.get('tags', []),
            'PublishedAt': snippet.get('publishedAt', ''),
            'View_Count': int(statistics.get('viewCount', 0)),
            'Like_Count': int(statistics.get('likeCount', 0)),
            'Dislike_Count': int(statistics.get('dislikeCount', 0)),
            'Favorite_Count': int(statistics.get('favoriteCount', 0)),
            'Comment_Count': int(statistics.get('commentCount', 0)),
            'Duration': item.get('contentDetails', {}).get('duration', ''),
            'Thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
            'Caption_Status': item.get('contentDetails', {}).get('caption', ''),
            'Comments': comments  
        }
        # convert all details to dict
        video_details[f'Video_Id_{index}'] = details

    return video_details
#-------------------------------------------------------------------------------------------------------------
# function to inject the all data into Mysql
def inject_data(data,res_playlist):
    playlist_id = res_playlist['items'][0]['id']
    # Connect to Mysql
    connection = mysql.connector.connect(
        host='host',
        user='user',
        password="pswd",
        database="dbname"
    )
    cur = connection.cursor()
    data=data
    # Create channel table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS channel (
            Channel_Id VARCHAR(255) PRIMARY KEY,
            Channel_Name VARCHAR(255),
            Subscription_Count INT,
            Channel_Views INT,
            Channel_Description VARCHAR(255)
        )
    """)
    # Create playlist table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist (
            Playlist_Id VARCHAR(255) PRIMARY KEY,
            Channel_Id VARCHAR(255),
            Playlist_Name VARCHAR(255),
            FOREIGN KEY (Channel_Id) REFERENCES channel(Channel_Id)
        )
    """)
    # Create video table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS video (
            Video_Id VARCHAR(255) PRIMARY KEY,
            Playlist_Id VARCHAR(255),
            Video_Name VARCHAR(255),
            Video_Description TEXT,
            PublishedAt DATETIME,
            View_Count INT,
            Like_Count INT,
            Dislike_Count INT,
            Favorite_Count INT,
            Comment_Count INT,
            Duration INT,
            Thumbnail VARCHAR(255),
            Caption_Status VARCHAR(255) )
    """)
    # Create comment table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comment (
            Comment_Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            Video_Id VARCHAR(255),
            Comment_Text TEXT,
            Comment_Author VARCHAR(255),
            Comment_PublishedAt DATETIME )
    """)
    # Insert channel data into the channel table
    for key, value in data.items():
        
        if 'Channel_Name' in value:
            query = """INSERT INTO channel (Channel_Id, Channel_Name, Subscription_Count, 
                   Channel_Views, Channel_Description) 
                   VALUES (%s, %s, %s, %s, %s)"""
            channel_data = (value.get('Channel_Id', ''), value.get('Channel_Name', ''), 
                            int(value.get('Subscription_Count', '')), int(value.get('Channel_Views', '')), 
                            value.get('Channel_Description', '') 
                           )
            cur.execute(query, channel_data)
        # Insert playlist data into the playlist table 
        if 'Playlist_Id' in value:
            query = """INSERT INTO playlist (Playlist_Id, Channel_Id, Playlist_Name) 
                       VALUES (%s, %s, %s)"""
            playlist_data = (value.get('Playlist_Id', ''), value.get('Channel_Id', ''), 
                             value.get('Playlist_Name', '') 
                            )
            cur.execute(query, playlist_data)
        # Insert video data into the video table
        if 'Video_Id' in value:
            date_to_extract=value.get('PublishedAt', '')
            date=extract_date_and_time(date_to_extract)
            duration_str = value.get('Duration', '')
            duration_seconds = convert_duration_to_seconds(duration_str)
            query = """INSERT INTO video (Video_Id, Playlist_Id, Video_Name, Video_Description, 
                    PublishedAt, View_Count, Like_Count, Dislike_Count, Favorite_Count, 
                    Comment_Count, Duration, Thumbnail, Caption_Status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            video_data= (value.get('Video_Id', ''),playlist_id,  # Ensure correct column name
            value.get('Video_Name', ''), value.get('Video_Description', ''), 
            date, value.get('View_Count', ''), value.get('Like_Count', ''), 
            value.get('Dislike_Count', ''), value.get('Favorite_Count', ''), 
            value.get('Comment_Count', ''), duration_seconds, 
            value.get('Thumbnail', ''), value.get('Caption_Status', ''))
            cur.execute(query,video_data)
        if 'Comments' in value: # here chech comments 
            #one more loop for inserting comments data into comment table
            for comment_key, comment_value in value['Comments'].items():
                date_to_extract=comment_value.get('Comment_PublishedAt', '')
                date=extract_date_and_time(date_to_extract)
                query="""INSERT INTO comment (Video_Id, Comment_Text, Comment_Author, Comment_PublishedAt) 
                    VALUES (%s, %s, %s, %s)"""
                comment_data=(value.get('Video_Id', ''),
                        comment_value.get('Comment_Text', ''),comment_value.get('Comment_Author', ''),
                        date)
                cur.execute(query,comment_data)
    connection.commit()
    cur.close() 
#------------------------------------------------------------------------------------------------------------------
# def functions to show the answer for all 10 questions 
def one():
    cur.execute("""
        SELECT Video_Name, Channel_Name
        FROM video
        JOIN playlist ON video.Playlist_Id = playlist.Playlist_Id
        JOIN channel ON playlist.Channel_Id = channel.Channel_Id
    """)
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def two():
    cur.execute("""select channel.channel_name,count(video.video_id) as num_videos from channel
            join playlist on channel.channel_id = playlist.channel_id
            join video on playlist.playlist_id = video.playlist_id 
            group by channel.channel_name order by num_videos desc limit 1;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def three():
    cur.execute("""select * from (select video.View_Count,channel.channel_name,video.Video_name from video 
                join playlist on video.playlist_id = playlist.playlist_id
                join channel on playlist.Channel_Id = channel.Channel_Id
                order by video.view_count desc limit 10) as new;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def four():
    cur.execute("""select channel.Channel_Name,video.Video_Name,video.Comment_Count from video
                join playlist on video.playlist_id = playlist.playlist_id
                join channel on playlist.Channel_Id = channel.Channel_Id;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def five():
    cur.execute("""select channel.Channel_Name,max(video.Like_Count) as highest_likes from video 
                join playlist on video.playlist_id =playlist.Playlist_Id
                join channel on playlist.Channel_Id = channel.Channel_Id 
                group by channel.Channel_Name order by highest_likes desc;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def six():
    cur.execute("""select channel.Channel_Name,video.Video_Name,sum(video.Like_Count) as total_likes,
                sum(video.Dislike_Count) as total_dislike from video
                join playlist on video.playlist_id = playlist.Playlist_Id
                join channel on playlist.Channel_Id = channel.Channel_Id group by video.Video_Id;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def seven():
    cur.execute("""select channel.Channel_Name,channel.Channel_Views as total_no_views from channel;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def eight():
    cur.execute("""select channel.Channel_Name,video.Video_Name,video.PublishedAt as published_at_2023 from channel
                join playlist on channel.Channel_Id = playlist.Channel_Id
                join video on playlist.Playlist_Id = video.Playlist_Id where video.PublishedAt
                between '2023-01-01 00:00:00' and '2023-12-31 23:59:59' order by published_at_2023;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def nine():
    cur.execute("""select channel.Channel_Name,avg(video.Duration) as avg_mins_duration from video
                join playlist on video.Playlist_Id = playlist.Playlist_Id
                join channel on playlist.Channel_Id = channel.Channel_Id group by channel.Channel_Name;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

def ten():
    cur.execute("""select channel.Channel_Name,video.Video_Name,
                max(video.Comment_Count) as highest_count from video
                join playlist on video.Playlist_Id = playlist.Playlist_Id
                join channel on playlist.Channel_Id = channel.Channel_Id
                where video.Comment_Count = (select max(video.Comment_Count) from video
                where video.Playlist_Id = playlist.Playlist_Id) 
                group by channel.channel_name,video.Video_Name order by highest_count desc ;""")
    video_channel_names = cur.fetchall()
    cur.close()
    connection.close()
    return video_channel_names

# to handling the corressponding question as selected
def handle_question(selected_question):
    if selected_question == '1':
        function_1()
    if selected_question == '2':
        function_2()
    if selected_question == '3':
        function_3()
    if selected_question == '4':
        function_4()
    if selected_question == '5':
        function_5()
    if selected_question == '6':
        function_6()
    if selected_question == '7':
        function_7()
    if selected_question == '8':
        function_8()
    if selected_question == '9':
        function_9()
    if selected_question == '10':
        function_10()
# def function to display the answer for questions with streamlit function
def function_1():
    det1 = one()
    st.write("Answer for Question 1:")
    det1_with_columns = pd.DataFrame(det1,columns=['video_name', 'channel_name'])
    st.table(det1_with_columns)
def function_2():
    det2 = two()
    st.write("Answer for Question 2:")
    det2_with_columns = pd.DataFrame(det2,columns=['Channel_Name', 'num_videos'])
    st.table(det2_with_columns)
def function_3():
    det3 = three()
    st.write("Answer for Question 3:")
    det3_with_columns = pd.DataFrame(det3,columns=['View_Count', 'channel_name', 'Video_name'])
    st.table(det3_with_columns)
def function_4():
    det4 = four()
    st.write("Answer for Question 4:")
    det4_with_columns = pd.DataFrame(det4,columns=['Channel_Name', 'Video_Name', 'Comment_Count'])
    st.table(det4_with_columns)
def function_5():
    det5 = five()
    st.write("Answer for Question 5:")
    det5_with_columns = pd.DataFrame(det5,columns=['Channel_Name', 'highest_likes'])
    st.table(det5_with_columns)
def function_6():
    det6 = six()
    st.write("Answer for Question 6 with additional details:")
    det6_with_columns = pd.DataFrame(det6,columns=['Channel_Name', 'Video_Name', 'total_likes','total_dislikes'])
    st.table(det6_with_columns)
def function_7():
    det7 = seven()
    st.write("Answer for Question 7:")
    det7_with_columns = pd.DataFrame(det7,columns=['Channel_Name', 'total_no_views'])
    st.table(det7_with_columns)
def function_8():
    det8 = eight()
    st.write("Answer for Question 8:")
    det8_with_columns = pd.DataFrame(det8,columns=['Channel_Name', 'Video_Name', 'published_at_2023'])
    st.table(det8_with_columns)
def function_9():
    det9 = nine()
    st.write("Answer for Question 9:")
    det9_with_columns = pd.DataFrame(det9,columns=['Channel_Name', 'avg_mins_duration'])
    st.table(det9_with_columns)
def function_10():
    det10 = ten()
    st.write("Answer for Question 10:")
    det10_with_columns = pd.DataFrame(det10,columns=['Channel_Name', 'Video_Name', 'highest_no.of_comments'])
    st.table(det10_with_columns)
    
#-----------------------------------------------------------------------------------------------------------------
#getting data from Mysql for analysis
def get_data_sql():
    cur.execute("""SELECT channel.Channel_Name,video.Video_Id,
                EXTRACT(YEAR FROM PublishedAt) AS year,
                EXTRACT(MONTH FROM PublishedAt) AS month,
                sum(View_Count) AS View_Counts FROM video
                join playlist on video.Playlist_Id = playlist.Playlist_Id
                join channel on playlist.channel_Id = channel.Channel_Id 
                where video.PublishedAt between '2023-01-01 00:00:00' and '2023-12-31 23:59:59'
                GROUP BY video_id,EXTRACT(YEAR FROM PublishedAt),
                EXTRACT(MONTH FROM PublishedAt)
                ORDER BY year,month;""")
    row_details = cur.fetchall()
    cur.close()
    connection.close()
    data_list=[]
    #getting details and append to dict with variables 
    for row in row_details:
        channel_Name, video_id, year, month, view_counts = row
        data_list.append({
            "Channel_Name": channel_Name,
            "Video_ID": video_id,
            "Year": year,
            "Month": month,
            "View_Counts": view_counts
        })
    return data_list
#-----------------------------------------------------------------------------------------------------------------
#create main function and pass user input channel id
def main(channel_id):
    # Initialize the YouTube API client
    api_key = "use_your_api_key"
    id=channel_id
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    # getting channel info
    res_channel = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=id
    ).execute()

    # getting playlist details
    res_playlist = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId=id,
        maxResults=20
    ).execute()

    # getting no. of video ids using playlist id
    upload_playlist_id = res_channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    response_videos = youtube.playlistItems().list(
        part='snippet',
        playlistId=upload_playlist_id,
        maxResults=100
    ).execute()

    video_ids = ','.join([item['snippet']['resourceId']['videoId'] for item in response_videos['items']])
    response_video_details = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_ids
    ).execute()

    # fetch and parse channel details
    channel_details = channel_info(res_channel, res_playlist)

    # fetch and parse video details
    video_details_dict = video_details(youtube, response_video_details)

    # merge all details into channel_details
    channel_details.update(video_details_dict)

    # Print the channel_details
    #pprint.pprint(channel_details)
    
    # inject data into Mysql
    inject_data(channel_details,res_playlist)

#------------------------------------------------------------------------------------------------------------------
#using streamlite to create a web page 
st.title('YOUTUBE DATA HARVESTING') #title
st.text("Enter YouTube channel_id below:") #text
st.text("Hint: go to channel's home page >> right  click >> view page resource >>Find channel_id")
channel_id = st.text_input("Enter Channel ID:", "") #inputbox
if st.button("Extract Data to SQL"): #button
    main(channel_id) #start main function here
#------------------------------------------------------------------------------------------------------------------
#questions are mentioned in streamlit selectbox
question_tosql = st.selectbox('Select your Question', (
    '1. What are the names of all the videos and their corresponding channels?',
    '2. Which channels have the most number of videos, and how many videos do they have?',
    '3. What are the top 10 most viewed videos and their respective channels?',
    '4. How many comments were made on each video, and what are their corresponding video names?',
    '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
    '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
    '7. What is the total number of views for each channel, and what are their corresponding channel names?',
    '8. What are the names of all the channels that have published videos in the year 2023?',
    '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
    '10. Which videos have the highest number of comments, and what are their corresponding channel names?'
))
# button performs to activate that given function call 
if st.button("Submit"):
    handle_question(question_tosql.split(".")[0])
# button performs the analysis process using that function
if st.button("VIEW ANALYSIS"):
    datas = get_data_sql()
    df = pd.DataFrame(datas)
    # converting that column values into numeric data
    df['View_Counts'] = pd.to_numeric(df['View_Counts'])
    fig = plt.scatter_3d(df, x='Year', y='Month', z='View_Counts', color='Channel_Name', symbol='Video_ID', size='View_Counts',
                    hover_data=['Channel_Name', 'Video_ID'])
    fig.update_layout(title='A three-dimensional scatter plot displaying the amount of likes they get each month in 2023',
                  scene=dict(xaxis_title='Year', yaxis_title='Month', zaxis_title='View Counts'))
    fig.show()
