import json
import requests
import re
import urllib.parse
import os
from urllib.parse import unquote
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

access_token = os.environ["CANVAS_ACCESS_TOKEN"]
base_url = "https://usu.instructure.com/api/v1"

boardID = ""
rowID = ""
columnID = ""
subitemParams = {}
statusValue = ""
kalturaId = ""

def fetchValuesOfBoard(action):
    url = "https://api.monday.com/v2"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization' : os.environ["MONDAY_API_KEY"]
    }
    
    data = {
        'query': action
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(response.text)
    response = json.loads(response.text)
    
    print(response)
    return response
    
def addCategories(entry_id, category_id):
    secrets_params = {
        'secret': os.environ["YOUTUBE_API_KEY"],
        'partnerId':1530551,
        'privileges':"",
        'type': 2,
        'userId':'captions@usu.edu',
        'format':1
        }
    
    url = 'https://www.kaltura.com/api_v3/service/session/action/start'
    response = requests.get(url, params=secrets_params)
    ks = response.json()
    
    categoriesMap = {
        '3play': 184368213,
        '3play_extended': 184764723,
        '3play_rush' : 289696852,
        '3play_same_day' : 289694022,
        '3play_two_hour' : 289697052,
        '3play_expedited' : 289696942
        }
    
    params = {  
          'ks': ks,
          'format':1,
          "categoryEntry": {
                    "categoryId": categoriesMap[category_id],
                    "entryId": entry_id,
            }
        }
    
    url = 'https://www.kaltura.com/api_v3/service/categoryentry/action/add'
    response = requests.post(url, json=params)
    response = response.json()
  
def extract_src_links(html_string):
    pattern = r'src=["\'](.*?)["\']'  # Regex pattern to match src links
    src_links = re.findall(pattern, html_string)
    return src_links

def getKalturaEntryId(html):
    # Regular expression pattern to match URLs in 'src' and 'href' attributes
    url_pattern = re.compile(r'(?:src|href)="(.*?)"')
    
    # Find all matches of URLs using the pattern
    matches = re.findall(url_pattern, html)
    
    entry_id = []
    # Print the extracted URLs
    for url in matches:
      url = unquote(url)
      # Regex pattern to match entry IDs in the first form (entryid/0_d09etxu6)
      pattern1 = r'/entryid/([^/?&]+)'
    
      # Regex pattern to match entry IDs in the second form (entry_id=0_d09etxu6)
      pattern2 = r'entry_id=([^"&]+)'
    
      entry_ids = []
      matches1 = re.findall(pattern1, url)
      matches2 = re.findall(pattern2, url)
    
      entry_ids.extend(matches1)
      entry_ids.extend(matches2)
      
      entry_id.extend(entry_ids)
    
    return set(entry_id)
    
def getYoutubeEntryId(html):
    # print(html)
    # Regular expression pattern to match URLs in 'src' and 'href' attributes
    url_pattern = re.compile(r'(?:src|href)="(.*?)"')

    # Find all matches of URLs using the pattern
    matches = re.findall(url_pattern, html)

    entry_id = []
    # Print the extracted URLs
    for url in matches:
      url = unquote(url)
      print(url)
      if not ('youtube' in url):
        continue
      # Regex pattern to match entry IDs in the first form (entryid/0_d09etxu6)
      pattern1 = r'/embed/([^/?&]+)'

      # Regex pattern to match entry IDs in the second form (entry_id=0_d09etxu6)
      pattern2 = r'v=([^"&]+)'

      entry_ids = []
      matches1 = re.findall(pattern1, url)
      matches2 = re.findall(pattern2, url)

      entry_ids.extend(matches1)
      entry_ids.extend(matches2)

      entry_id.extend(entry_ids)

    return set(entry_id)
    
def getVideoEntryId(html):
    print("hello")
    # print(html)
    # Regular expression pattern to match URLs in 'src' and 'href' attributes
    url_pattern = re.compile(r'(?:src|href)="(.*?)"')

    # Find all matches of URLs using the pattern
    matches = re.findall(url_pattern, html)

    entry_id = []
    # Print the extracted URLs
    for url in matches:
      url = unquote(url)
      print(url)
      if not ('media_objects_iframe' in url and 'type=video' in url):
        continue
      # Regex pattern to match entry IDs in the first form (entryid/0_d09etxu6)
      pattern1 = r'/media_objects_iframe/([^/?&]+)'

      matches1 = re.findall(pattern1, url)
      matches1[0] = matches1[0][-1:-7:-1]

      print("match1")
      print(matches1)
      entry_id.extend(matches1)

    return set(entry_id)

def getAudioEntryId(html):
    # print(html)
    # Regular expression pattern to match URLs in 'src' and 'href' attributes
    url_pattern = re.compile(r'(?:src|href)="(.*?)"')

    # Find all matches of URLs using the pattern
    matches = re.findall(url_pattern, html)

    entry_id = []
    # Print the extracted URLs
    for url in matches:
      url = unquote(url)
      print(url)
      if not ('media_objects_iframe' in url and 'type=audio' in url):
        continue
      # Regex pattern to match entry IDs in the first form (entryid/0_d09etxu6)
      pattern1 = r'/media_objects_iframe/([^/?&]+)'

      matches1 = re.findall(pattern1, url)
      matches1[0] = matches1[0][-1:-7:-1]
      print("match2")
      print(matches1)
      entry_id.extend(matches1)

    return set(entry_id)

def get_all_pages(course_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "per_page": 500  # Number of pages to retrieve per request
    }

    all_pages = []
    url = f"{base_url}/courses/{course_id}/pages"  # Replace <course_id> with the ID of the course

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request fails

        pages = response.json()
        all_pages.extend(pages)

        # Check if there are more pages
        url = response.links.get('next', {}).get('url')

    return all_pages


def get_all_assignments(course_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "per_page": 500  # Number of pages to retrieve per request
    }

    all_assignments = []
    url = f"{base_url}/courses/{course_id}/assignments"  # Replace <course_id> with the ID of the course

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request fails

        pages = response.json()
        all_assignments.extend(pages)

        # Check if there are more pages
        url = response.links.get('next', {}).get('url')

    return all_assignments

def get_all_discussions(course_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "per_page": 500  # Number of pages to retrieve per request
    }

    all_discussions = []
    url = f"{base_url}/courses/{course_id}/discussion_topics"  # Replace <course_id> with the ID of the course

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request fails

        pages = response.json()
        all_discussions.extend(pages)

        # Check if there are more pages
        url = response.links.get('next', {}).get('url')

    return all_discussions

def get_all_quizzes(course_id):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "per_page": 500  # Number of pages to retrieve per request
    }

    all_discussions = []
    url = f"{base_url}/courses/{course_id}/quizzes"  # Replace <course_id> with the ID of the course

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception if the request fails

        pages = response.json()
        all_discussions.extend(pages)

        # Check if there are more pages
        url = response.links.get('next', {}).get('url')

    return all_discussions

def get_url(course_id, all_pages, tab):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    all_urls = {}

    for page in all_pages:
      if(tab == "pages"):
        url = f"{base_url}/courses/{course_id}/pages/{page['page_id']}"  # Replace <course_id> with the ID of the course
        response = requests.get(url, headers=headers)
        json_response = response.json()
      else:
        json_response = page

      if(tab == "pages"):
        html_body = json_response['body']
        title = json_response['title']
      elif(tab == "assignments"):
        html_body = json_response['description']
        title = json_response['name']
      elif(tab == "discussions"):
        html_body = json_response['message']
        title = json_response['title']
      elif(tab == "quizzes"):
        html_body = json_response['description']
        title = json_response['title']

      if(not html_body):
        continue

      all_entry_ids = {}

      entry_ids = getKalturaEntryId(html_body)
      if(len(entry_ids) != 0):
        all_entry_ids['Kaltura'] = entry_ids

      entry_ids = getYoutubeEntryId(html_body)
      if(len(entry_ids) != 0):
        all_entry_ids['YouTube'] = entry_ids

      entry_ids = getVideoEntryId(html_body)
      if(len(entry_ids) != 0):
        all_entry_ids['Video'] = entry_ids

      entry_ids = getAudioEntryId(html_body)
      if(len(entry_ids) != 0):
        all_entry_ids['Audio'] = entry_ids

      if(len(all_entry_ids) == 0):
        continue

      all_urls[title] = {
          'entry_id' : all_entry_ids,
          'url': json_response['html_url'],
          'published': json_response['published'],
          }

    return all_urls


def checkCaptionedOrNot(entry_id):
    params = {'secret':'6e2753acd5c56f7d5b7e41d711e27f1e',
          'partnerId':1530551,
          'privileges':"",
          'type': 2,
          'userId':'captions@usu.edu',
          'format':1
          }
    
    url = 'https://www.kaltura.com/api_v3/service/session/action/start'
    response = requests.get(url, params=params)
    ks = response.json()
    
    params = {  'ks': ks,
              'partnerId':1530551,
              'format':1,
              "filter": {
                        "objectType": "KalturaAssetFilter",
                        "entryIdEqual": entry_id
                },
                "pager": {
                  "objectType": "KalturaPager",
                  "pageIndex": 0,
                  "pageSize": 0
                }
          }
    
    url = 'https://www.kaltura.com/api_v3/service/caption_captionasset/action/list'
    response = requests.post(url, json=params)
    response = response.json()

    return response["totalCount"] > 0

def checkYoutubeCaptionedOrNot(video_id):
    # Set up the YouTube Data API key and service
    API_KEY = "AIzaSyBJwzV0MlrBXlLsjoDydbmjILbAeN68QVc"
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        response = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        captions = response.get("items", [])
        print(captions)
        return len(captions) > 0

    except HttpError as e:
        print(f"An error occurred: {e}")
        return False
        
def getYoutubeCaptionedType(video_id):
    # Set up the YouTube Data API key and service
    API_KEY = "AIzaSyBcUZRre3TfiNG8YAyWgnM5lpwMYa-sxDI"
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        response = youtube.captions().list(
            part="snippet",
            videoId=video_id
        ).execute()

        captions = response.get("items", [])
        print(captions)
        
        if(len(captions) == 0):
            return "No Caption"
            
        caption_type = ""
        for caption in captions:
            caption_type += caption['snippet']['trackKind']
            caption_type += ", "
        return caption_type[:-2]

    except HttpError as e:
        print(f"An error occurred: {e}")
        return "No Caption"

def getCaptionedType(entry_id):
    secrets_params = {'secret':'6e2753acd5c56f7d5b7e41d711e27f1e',
          'partnerId':1530551,
          'privileges':"",
          'type': 2,
          'userId':'captions@usu.edu',
          'format':1
          }

    url = 'https://www.kaltura.com/api_v3/service/session/action/start'
    response = requests.get(url, params=secrets_params)
    ks = response.json()
    
    params = {  'ks': ks,
              'partnerId':1530551,
              'format':1,
              "filter": {
                        "objectType": "KalturaAssetFilter",
                        "entryIdEqual": entry_id,
                }
          }
    
    url = 'https://www.kaltura.com/api_v3/service/caption_captionasset/action/list'
    response = requests.post(url, json=params)
    response = response.json()
    
    for ele in response['objects']:
        if(ele['displayOnPlayer']):
          return ele['label'] if 'label' in ele else 'No Captions'
    
    return 'No Captions'
  
def getAllUrls(all_urls):
    for title in all_urls:
        print(title)
        captions = {}
        for key, value in all_urls[title]['entry_id'].items():
          for entry_id in value:
            if(key == "Kaltura"):
                captionedStatus = checkCaptionedOrNot(entry_id)
                captionType = getCaptionedType(entry_id)
            elif(key == "YouTube"):
                captionedStatus = checkYoutubeCaptionedOrNot(entry_id)
                captionType = getYoutubeCaptionedType(entry_id)
                if('standard' in captionType):
                    captionType = "standard"
                    captionedStatus = True
                elif not (captionType == "No Caption"):
                    captionedStatus = False
                    captionType = "esr"
            elif(key == "Video"):
                captionedStatus = None
                captionType = None
            elif(key == "Audio"):
                captionedStatus = None
                captionType = None
            captions[entry_id] = [captionedStatus, key, captionType]
        all_urls[title]['entry_id'] = captions
    return all_urls

def getCaptionedVideos(course_id):
    all_pages = get_all_pages(course_id)
    all_assignments = get_all_assignments(course_id)
    all_discussion = get_all_discussions(course_id)
    all_quizzes = get_all_quizzes(course_id)
    
    all_urls = get_url(course_id, all_pages, "pages")
    all_urls_assignment = get_url(course_id, all_assignments, "assignments")
    all_urls_discussion = get_url(course_id, all_discussion, "discussions")
    all_urls_quizzes = get_url(course_id, all_quizzes, "quizzes")
    
    result = []
    
    result.append(getAllUrls(all_urls))
    result.append(getAllUrls(all_urls_assignment))
    result.append(getAllUrls(all_urls_discussion))
    result.append(getAllUrls(all_urls_quizzes))
    
    return result
  
def lambda_handler(event, context):
    global statusValue
    global subitemParams
    
    # TODO implement
    bodyJSON = json.loads(event['body'])
    print(bodyJSON)
    
    if(bodyJSON != None and 'event' in bodyJSON):
        print(bodyJSON)
        if(bodyJSON['event']['value']['label']['text'] == "Begin Check"):
            statusValue = bodyJSON['event']['columnId']
            return getMethodHandler(bodyJSON)
        elif(bodyJSON['event']['value']['label']['text'] == "Check Caption"):
            statusValue = bodyJSON['event']['columnId']
            response = getBoardData(bodyJSON, "getCaption")
            kalturaId = response["data"]["boards"][0]["items"][0]["name"]
            print(subitemParams)
            column_value = {
                statusValue: "Done",
                subitemParams["captioned"]: "True" if checkCaptionedOrNot(kalturaId) else "False",
                subitemParams["caption_type"]: getCaptionedType(kalturaId)
            }
            
            addNewURLDataQuery = f"mutation {{change_multiple_column_values (board_id: {boardID}, item_id: {rowID}, column_values:{json.dumps(json.dumps(column_value))} ) {{ id }} }}"
            fetchValuesOfBoard(addNewURLDataQuery)
        # elif(bodyJSON['event']['value']['label']['text'] == "Check Captions for All"):
        #     statusValue = bodyJSON['event']['columnId']
        #     response = getBoardData(bodyJSON, "getCaptionAll")
        #     for response_item in response["data"]["boards"][0]["items"]:
        #         kalturaId = response_item["name"]
        #         print(response_item)
                # column_value = {
                #     statusValue: "Done",
                #     subitemParams["captioned"]: "True" if checkCaptionedOrNot(kalturaId) else "False",
                #     subitemParams["caption_type"]: getCaptionedType(kalturaId)
                # }
                
                # addNewURLDataQuery = f"mutation {{change_multiple_column_values (board_id: {boardID}, item_id: {rowID}, column_values:{json.dumps(json.dumps(column_value))} ) {{ id }} }}"
                # fetchValuesOfBoard(addNewURLDataQuery)
        elif(bodyJSON['event']['columnTitle'] == "3Play"):
            response = getBoardData(bodyJSON, "categories")
            entry_id = response['data']['boards'][0]['items'][0]['name']
            category_id = response['data']['boards'][0]['items'][0]['column_values'][0]['text']
            print(response)
            addCategories(entry_id, category_id)
            return {
                'statusCode': 200,
                'body': json.dumps("Updated the board successfully")
            }
    elif(bodyJSON != None and 'challenge' in bodyJSON):
        return postMethodHandler(event)
        
    return {
        'statusCode': 200,
        'body': json.dumps("Invalid request")
    }

def postMethodHandler(event):
    return {
        'statusCode': 200,
        'body': event['body']
    }

def getBoardData(req, method):
    global boardID
    global rowID
    global columnID
    global subitemParams
    global statusValue
    global kalturaId
    
    boardID = req['event']['boardId']
    rowID = req['event']['pulseId']
    columnID = req['event']['columnId']
    linkId = ""
    
    if(method != "categories"):
        column_value = {
            statusValue: "Check in Progress"
        }
        
        addNewURLDataQuery = f"mutation {{change_multiple_column_values (board_id: {boardID}, item_id: {rowID}, column_values:{json.dumps(json.dumps(column_value))} ) {{ id }} }}"
        fetchValuesOfBoard(addNewURLDataQuery)
    
    getTableSchema = """query {
                            boards (ids:%s){
                                id
                                columns{
                                  id 
                                  type
                                  title
                                  settings_str
                                }
                            }
                        }""" 

    schemaResponse = fetchValuesOfBoard(getTableSchema % (boardID))
    tableSchema = schemaResponse['data']['boards'][0]['columns']
    
    print("subitems")
    print(tableSchema)
    if(method != "categories"):
        for schema in tableSchema:
            if schema["title"] == "Link":
                linkId = schema["id"]
            if schema["title"] == "Kaltura":
                kalturaId = schema["id"]
            if schema["title"] == "Captioned?":
                subitemParams["captioned"] = schema["id"]
            if schema["title"] == "Caption Type":
                subitemParams["caption_type"] = schema["id"]
            if schema["title"] == "Subitems":
                temp = json.loads(schema["settings_str"])
                subitemBoardId = temp['boardIds'][0]
                subitemSchemaResponse = fetchValuesOfBoard(getTableSchema % (subitemBoardId))
                subitemTableSchema = subitemSchemaResponse['data']['boards'][0]['columns']
                print("checking")
                print(subitemTableSchema)
                for subitem_column in subitemTableSchema:
                    if subitem_column["title"] == "Page Name":
                        subitemParams['page_name'] = subitem_column["id"]
                    if subitem_column["title"] == "Link to Page":
                        subitemParams['link_to_page'] = subitem_column["id"]
                    if subitem_column["title"] == "Video Type":
                        subitemParams['video_type'] = subitem_column["id"]
                    if subitem_column["title"] == "Published":
                        subitemParams['published'] = subitem_column["id"]
                    if subitem_column["title"] == "Captioned?":
                        subitemParams['captioned'] = subitem_column["id"]
                    if subitem_column["title"] == "Caption Type":
                        subitemParams['caption_type'] = subitem_column["id"]
                    if subitem_column["title"] == "3Play":
                        subitemParams['3play'] = subitem_column["id"]
    else:
        for subitem_column in tableSchema:
            if subitem_column["title"] == "Page Name":
                subitemParams['page_name'] = subitem_column["id"]
            if subitem_column["title"] == "Link to Page":
                subitemParams['link_to_page'] = subitem_column["id"]
            if subitem_column["title"] == "Video Type":
                subitemParams['video_type'] = subitem_column["id"]
            if subitem_column["title"] == "Published":
                subitemParams['published'] = subitem_column["id"]
            if subitem_column["title"] == "Captioned?":
                subitemParams['captioned'] = subitem_column["id"]
            if subitem_column["title"] == "Caption Type":
                subitemParams['caption_type'] = subitem_column["id"]
            if subitem_column["title"] == "3Play":
                subitemParams['3play'] = subitem_column["id"]
            
        
    print("checking")
    print(subitemParams)
    getCaptionsTableData = """query {
                                    boards (ids:%s){
                                        name
                                        items(ids:%s) {
                                          id
                                          name
                                          column_values(ids:%s){
                                            id
                                            title
                                            type
                                            text
                                          }
                                        }
                                    }
                                }""" % (boardID, rowID, linkId)
                                
    getCaptionsTableData_2 = """query {
                                    boards (ids:%s){
                                        name
                                        items(ids:%s) {
                                          id
                                          name
                                          column_values(ids:%s){
                                            id
                                            title
                                            type
                                            text
                                          }
                                        }
                                    }
                                }""" % (boardID, rowID, columnID)
    
    getCategoriesTableData = """query {
                                    boards (ids:%s){
                                        name
                                        items(ids:%s) {
                                              id
                                              name
                                              column_values(ids:%s){
                                                id
                                                title
                                                type
                                                text
                                              }
                                            }
                                        }
                                }""" % (boardID, rowID, subitemParams['3play'] if '3play' in subitemParams else None)
    
    getCaptionsTableData_3 = """query {
                                    boards (ids:%s){
                                        name
                                        items {
                                          id
                                          name
                                          column_values{
                                            id
                                            title
                                            type
                                            text
                                          }
                                        }
                                    }
                                }""" %(boardID)
                                
    if method == "captions":
        print(getCaptionsTableData)
        return fetchValuesOfBoard(getCaptionsTableData)
    elif method == "categories":
        print("hello")
        print(getCategoriesTableData)
        return fetchValuesOfBoard(getCategoriesTableData)
    elif method == "getCaption":
        return fetchValuesOfBoard(getCaptionsTableData_2)
    elif method == "getCaptionAll":
        return fetchValuesOfBoard(getCaptionsTableData_3)

def getMethodHandler(req):
    global subitemParams
    global kalturaId
    
    print("fetching the data")
    
    response = getBoardData(req, "captions")
    course_link = response['data']['boards'][0]['items'][0]['column_values'][0]['text']
    course_number = 0
    
    pattern = r'/courses/(\d+)'
    
    # Use the regular expression to find matches in the link
    matches = re.findall(pattern, course_link)
    
    if matches:
        # The first match group contains the course number
        course_number = matches[0]
    
    result = getCaptionedVideos(course_number)
    total_kaltura_videos = 0
    
    for key, value in result[0].items():
        total_kaltura_videos += len(value['entry_id'])
    
    for key, value in result[1].items():
        total_kaltura_videos += len(value['entry_id'])
    
    for key, value in result[2].items():
        total_kaltura_videos += len(value['entry_id'])
        
    for key, value in result[3].items():
        total_kaltura_videos += len(value['entry_id'])
        
    column_value = {
        kalturaId: total_kaltura_videos
    }
    
    print(total_kaltura_videos)
    
    addNewURLDataQuery = f"mutation {{change_multiple_column_values (board_id: {boardID}, item_id: {rowID}, column_values:{json.dumps(json.dumps(column_value))} ) {{ id }} }}"
    print(addNewURLDataQuery)
    fetchValuesOfBoard(addNewURLDataQuery)
    
    for key, value in result[0].items():
        for entry_ids, details in value['entry_id'].items():
            sub_item_column_value = {   
                                        subitemParams['page_name']: key,
                                        subitemParams['link_to_page']: {
                                                    "url":value['url'],
                                                    "text": value['url']
                                                },
                                        subitemParams['captioned']: "True" if details[0] else "False",
                                        subitemParams['published']: "True" if value["published"] else "False",
                                        subitemParams['video_type']: details[1],
                                        subitemParams['caption_type']:details[2]
                                    }
                                    
            addSubitems = f'mutation {{ create_subitem (parent_item_id: {rowID} , item_name: {json.dumps(entry_ids)}, column_values:{json.dumps(json.dumps(sub_item_column_value))}) {{id}}}}'
            print(addSubitems)
            fetchValuesOfBoard(addSubitems)
    
    for key, value in result[1].items():
        for entry_ids, details in value['entry_id'].items():
            sub_item_column_value = {   
                                        subitemParams['page_name']: key,
                                        subitemParams['link_to_page']: {
                                                    "url":value['url'],
                                                    "text": value['url']
                                                },
                                        subitemParams['captioned']: "True" if details[0] else "False",
                                        subitemParams['published']: "True" if value["published"] else "False",
                                        subitemParams['video_type']: details[1],
                                        subitemParams['caption_type']:details[2]
                                    }
                                    
            addSubitems = f'mutation {{ create_subitem (parent_item_id: {rowID} , item_name: {json.dumps(entry_ids)}, column_values:{json.dumps(json.dumps(sub_item_column_value))}) {{id}}}}'
            print(addSubitems)
            fetchValuesOfBoard(addSubitems)
            
    for key, value in result[2].items():
        for entry_ids, details in value['entry_id'].items():
            sub_item_column_value = {   
                                        subitemParams['page_name']: key,
                                        subitemParams['link_to_page']: {
                                                    "url":value['url'],
                                                    "text": value['url']
                                                },
                                        subitemParams['captioned']: "True" if details[0] else "False",
                                        subitemParams['published']: "True" if value["published"] else "False",
                                        subitemParams['video_type']: details[1],
                                        subitemParams['caption_type']:details[2]
                                    }
                                    
            addSubitems = f'mutation {{ create_subitem (parent_item_id: {rowID} , item_name: {json.dumps(entry_ids)}, column_values:{json.dumps(json.dumps(sub_item_column_value))}) {{id}}}}'
            fetchValuesOfBoard(addSubitems)
            
    for key, value in result[3].items():
        for entry_ids, details in value['entry_id'].items():
            sub_item_column_value = {   
                                        subitemParams['page_name']: key,
                                        subitemParams['link_to_page']: {
                                                    "url":value['url'],
                                                    "text": value['url']
                                                },
                                        subitemParams['captioned']: "True" if details[0] else "False",
                                        subitemParams['published']: "True" if value["published"] else "False",
                                        subitemParams['video_type']: details[1],
                                        subitemParams['caption_type']:details[2]
                                    }
                                    
            addSubitems = f'mutation {{ create_subitem (parent_item_id: {rowID} , item_name: {json.dumps(entry_ids)}, column_values:{json.dumps(json.dumps(sub_item_column_value))}) {{id}}}}'
            fetchValuesOfBoard(addSubitems)
    
    column_value = {
        statusValue: "Check Complete"
    }
    
    addNewURLDataQuery = f"mutation {{change_multiple_column_values (board_id: {boardID}, item_id: {rowID}, column_values:{json.dumps(json.dumps(column_value))} ) {{ id }} }}"
    fetchValuesOfBoard(addNewURLDataQuery)
    
    return {
        'statusCode': 200,
        'body': json.dumps("Updated the board successfully")
    }
