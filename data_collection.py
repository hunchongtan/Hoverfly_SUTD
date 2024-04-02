import pickle
import os
import pandas as pd
from googleapiclient.discovery import build
import shutil


#Initialise and Set up Google API Key
f = open("keys/google_key.txt", "r")
key = f.readlines()[0]
f.close()

youtube = build('youtube', 'v3', developerKey=key)


#User Inputs (prompt)
search_terms = "Repel Umbrella"       # insert prompt -> "Brand Product Model"
max_result = 20                       # No. of results (1-50)


#Define containers to store info
vid_id = []             	# video id
vid_page = []       		# video links (https...)
vid_title = []              # video title
num_comments = []           # official number of comments
load_error = 0              # error counter
can_load_title = []         # temp. list for storing title w/o loading error
can_load_page = []          # temp. list for storing links w/o loading error
num_page = []               # comment_response page number
page_title = []             # comment_response video title
comment_resp = []           # comment_response
comment_list = []           # temp. list for storing comments
comment_data = []           # comments & replies from comment_response
all_count = 0               # total number of comments


#Search for Video IDs based on User Inputs
print("Search for Videos IDs...")
request = youtube.search().list(
    q=search_terms,
    maxResults=max_result,
    part="id",
    type="video",
    order="viewCount"  # Sorting by view count
    )
search_response = request.execute()
print(search_response)


#Create a list of Video IDs and a corresponding list of weblinks
print("Videos found...")
for i in range(max_result):
    videoId = search_response['items'][i]['id']['videoId']
    print(videoId)
    vid_id.append(videoId)                          # a list of Video IDs
    page = "https://www.youtube.com/watch?v=" + videoId
    print(page)
    print()
    vid_page.append(page)                           # a list of Video links
print("\nThere are", len(vid_page), "videos.")


#Use the list of Video IDs to get video data
print("Get video data...")
for i in range(len(vid_id)):
    request = youtube.videos().list(
        part="snippet, statistics",
        id=vid_id[i]
        )
    video_response = request.execute()
    print(video_response)

    title = video_response['items'][0]['snippet']['title']
    vid_title.append(title)
    try:                        # use try/except as some videos might not load
        comment_count = video_response['items'][0]['statistics']['commentCount']
        print("Video", i + 1, "-", title, "-- Comment count: ", comment_count)
        print()
        num_comments.append(comment_count)
    except:
        print("Video", i + 1, "-", title, "-- Comments are turned off")
        print()
        num_comments.append(0)


#Use the list of Video IDs to get comments (by page)
print("Get comment data...")
for i in range(len(vid_id)):
    try:                                        # use try/except as some "comments are turned off"
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=vid_id[i]
            )
        comment_response = request.execute()
        print(comment_response)

        comment_resp.append(comment_response)   # append 1 page of comment_response
        pages = 1
        num_page.append(pages)                  # append page number of comment_response
        page_title.append(vid_title[i])         # append video title along with the comment_response

        can_load_page.append(vid_page[i])       # drop link if it can't load (have at least 1 comment page)
        can_load_title.append(vid_title[i])     # drop title if it can't load (have at least 1 comment page)

        test = comment_response.get('nextPageToken', 'nil')         # check for nextPageToken
        while test != 'nil':                                        # keep running until last comment page
            next_page_ = comment_response.get('nextPageToken')
            request = youtube.commentThreads().list(
                part="snippet,replies",
                pageToken=next_page_,
                videoId=vid_id[i]
                )
            comment_response = request.execute()
            print(comment_response)

            comment_resp.append(comment_response)                   # append next page of comment_response
            pages += 1
            num_page.append(pages)                                  # append page number of comment_response
            page_title.append(vid_title[i])                         # append video title along with the comment_response

            test = comment_response.get('nextPageToken', 'nil')     # check for nextPageToken (while loop)
    except:
        load_error += 1


#Show videos without loading errors
print("Videos that can load...")
vid_page = can_load_page                    # update vid_page with those with no load error
vid_title = can_load_title                  # update vid_title with those with no load error
for i in range(len(vid_title)):
    if vid_title[i] == 'YouTube':           # default error title is 'YouTube'
        vid_title[i] = 'Video_' + str(i+1)  # replace 'YouTube' with Video_1 format
    print(i + 1, vid_title[i])


#Sift through and store comments as a list
print("Get individual comment...")
for k in range(len(comment_resp)):
    count = 0                                                     # comment counter
    comments_found = comment_resp[k]['pageInfo']['totalResults']  # comments on 1 comment_response page
    count = count + comments_found
    for i in range(comments_found):
        try:
            comment_list.append(comment_resp[k]['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
            print(comment_resp[k]['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])
        except:
            print("missing comment")                              # or too many comments (e.g. 7.3K comments)

print(comment_list)
print()
print(len(comment_list), "comments in total.")


#Create directory
try:                                              # Create directory named after search terms
    os.makedirs("support/%s" % search_terms)
    print("Directory", search_terms, "created")
except FileExistsError:
    print("Directory", search_terms, "exists")

try:                                              # Create directory to store current search terms
    os.makedirs("support/_current_")
    print("Directory _current_ created")
except FileExistsError:
    print("Directory _current_ exists")


#Save files for future use
f = open("support/%s/comments.txt" % search_terms, "w+", encoding="utf-8")
for i in range(len(comment_list)):
    f.write("<<<" + comment_list[i] + ">>>")
f.close()

pickle.dump(search_terms, open("support/%s/searchTerms.pkl" % search_terms, "wb"))
pickle.dump(comment_list, open("support/%s/comment_list.pkl" % search_terms, "wb"))
pickle.dump(vid_title, open("support/%s/vid_title.pkl" % search_terms, "wb"))
pickle.dump(vid_page, open("support/%s/vid_page.pkl" % search_terms, "wb"))
pickle.dump(vid_id, open("support/%s/vid_id.pkl" % search_terms, "wb"))


#Save files for next step
source = "support/%s/comments.txt" % search_terms
destination = "support/_current_/comments.txt"
shutil.copyfile(source, destination)

pickle.dump(search_terms, open("support/_current_/searchTerms.pkl", "wb"))


# # Clear data for rerun
# comment_list.clear()
# vid_title.clear()
# vid_page.clear()
# vid_id.clear()