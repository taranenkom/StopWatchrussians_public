from flask import Flask, request
from flask_restful import Resource, Api, reqparse

from flask_cors import CORS

import json

# Imports the Google Cloud client library
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

from back import *
import users_administration as u_manage

from waitress import serve

app = Flask(__name__)
api = Api(app)
CORS(app)
# activate_youtube_api()#activate youtube api



@app.route('/works', methods=['GET'])
def works():
    return 'Works',200

@app.route('/check_video', methods=['GET'])
def is_video_bad_by_url():
    # video_url = request.args.get('video_url')
    # if not request.is_json:
    #     return "Wrong input(not JSON)", 400
    
    # video_url = request.json[0].get('video_url')
    status_code = 200
    video_url = request.args.get('video_url')
    # name = request.args.get('name')
    # print(video_url)
    
    # data = make_summary()
    # response = app.response_class(
    #     response=json.dumps(data),
    #     status=200,
    #     mimetype='application/json'
    # )
    # return response
    data = None
    if video_url == None:
        data = "Wrong variables(video_url)"
        status_code=400
        # return "Wrong variables(video_url)",400
    try:
        data = get_yt_video_info(video_url)
    except Exception as e:
        data =  str(e)
        status_code = 400
        response = app.response_class(
            response=json.dumps({"is_bad":False,"error":data}),
            status=status_code,
            mimetype='application/json'
        )
        return response
    # info = get_yt_video_info(video_url)
    
    if data is None:
        data ="No info, but BAD"
    
    is_bad = False
    if data is not None:
        if data != {"owner": "Unknown", "actions": "Unknown"}:
            is_bad = True
    response = app.response_class(
        response=json.dumps({"is_bad":is_bad,"data":data}),
        status=status_code,
        mimetype='application/json'
    )
    return response

@app.route('/check_channel', methods=['GET'])
def is_channel_bad_by_url():
    # if not request.is_json:
    #     return "Wrong input(not JSON)", 400
    # channel_url = request.json[0].get('channel_url')
    channel_url = request.args.get('channel_url')
    data = None
    status_code = 200
    is_bad = False
    if channel_url == None:
        data = "Wrong variables(channel_url)"
        status_code = 400
        # return "Wrong variables(channel_url)",400
    else:
        try:
            data = get_channel_info_by_url(channel_url)
        except Exception as e:
            error = str(e)
            status_code = 400
            response = app.response_class(
                response=json.dumps({"is_bad":is_bad,"error":error}),
                status=status_code,
                mimetype='application/json'
            )
            return response
    # try:
    #     info = get_channel_info_by_url(channel_url)
    # except Exception as e:
    #     return str(e), 400
    if data is not None:
        if data != {"owner": "Unknown", "actions": "Unknown"} and data != "Wrong variables(channel_url)":
            is_bad = True
    response = app.response_class(
        response=json.dumps({"is_bad":is_bad,"data":data}),
        status=status_code,
        mimetype='application/json'
    )
    return response

@app.route('/ban_channel', methods=['POST'])
def ban_channel():
    if not request.is_json:
        return "Wrong input(not JSON)", 400
    data = request.json[0]
    
    channel_url = data.get('channel_url')
    actions = data.get('actions')
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    
    if channel_url == None or username==None or password == None or actions == None or name == None:
        return "Wrong variables(channel_url, username, password, actions, name)",400
    
    if u_manage.admin_validation(username, password) != "admin":
        return "Wrong username or password", 400
    
    youtube_id = get_youtube_id_by_channel_url(channel_url)
    try:
        add_owner_to_db(name,actions,youtube_id)
    except Exception as e:
        return str(e), 400
    # except Exception as e:
    #     return str(e), 400
    return "Channel banned", 200


@app.route('/ban_video', methods=['POST'])
def ban_video():
    if not request.is_json:
        return "Wrong input(Not JSON)", 400
    
    data = request.json[0]
    video_url = data.get('video_url')
    actions = data.get('actions')
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    
    if video_url == None or username==None or password == None or actions == None or name == None:
        return "Wrong variables(video_url,actions,name,username,password)", 400
        
    if u_manage.admin_validation(username, password) != "admin":
        return "Wrong username or password", 400
    
    youtube_id, country_code = get_youtube_id_and_country_from_video_url(video_url)
    if youtube_id is None:
        return "Wrong video url", 400
    try:
        add_owner_to_db(name,actions,youtube_id)
    except Exception as e:
        return str(e), 400
    
    return "Video and the channel banned", 200
 
@app.route('/get_banned_info', methods=['GET'])  
def get_all_banned_channels():
    # if not request.is_json:
    #     return "Wrong input(not JSON)", 400
    # data = request.json[0]
    data = request.args
    
    find_who = data.get('find_who')
    if find_who is None:
        return "Wrong input(find_who)?", 400
     
    if find_who is None:
        return "Wrong input", 400
    if find_who == "channels":
        return get_banned_channels(), 200
    if find_who == "owners":
        return get_banned_owners(), 200
    else:
        return "Wrong input", 400


@app.route("/unban_channel", methods=['POST'])
def delete_banned():
    if not request.is_json:
        return "Wrong input", 400
    
    data = request.json[0]
    
    video_url = data.get('video_url')
    channel_url = data.get('channel_url')
    username = data.get('username')
    password = data.get('password')
    
    if (video_url == None and channel_url ==None) or username==None or password == None:
        return "Note enough variables", 400
    if u_manage.admin_validation(username, password) != "admin":
        return "Wrong username or password", 400
    
    try:
        youtube_id = get_youtube_id_by_channel_url(channel_url)
    except Exception as e:
        try:
            youtube_id, country_code = get_youtube_id_and_country_from_video_url(video_url)
        except Exception as e:
            return str(e), 400

    try:
        # print(youtube_id)
        # channel_id = get_channel_id(youtube_id)
        # print(channel_id)
        remove_channel_from_db(youtube_id)
    except Exception as e:
        return str(e), 400
    
    return "Channel removed", 200


@app.route('/unban_creator', methods = ['POST'])
def unban_creator():
    if not request.is_json:
        return "Wrong input(not JSON)", 400
    
    data = request.json[0]
    
    owner_id = data.get('owner_id')
    username = data.get('username')
    password = data.get('password')
    
    if owner_id == None or username==None or password == None:
        return "Please make sure that you entered all variables(owner_id,username,password)", 400
    
    if u_manage.admin_validation(username, password) != "admin":
        return "Wrong username or password", 400
    
    try:
        remove_youtuber(owner_id)
    except Exception as e:
        return str(e), 400
    
    return "Youtuber unbanned", 200

@app.route("/unban_creator_and_all_channels", methods=['POST'])
def unban_creator_and_all_his_channels():
    if not request.is_json:
        return "Wrong input(not JSON)", 400
    
    data = request.json[0]
    
    owner_id = data.get('owner_id')
    username = data.get('username')
    password = data.get('password')
    
    if owner_id == None or username==None or password == None:
        return "Please make sure that you entered all variables(owner_id,username,password)", 400
    
    if u_manage.admin_validation(username, password) != "admin":
        return "Wrong username or password", 400
    
    try:
        remove_youtuber_and_all_his_channels(owner_id)
    except Exception as e:
        return str(e), 400
    
    
if __name__ == "__main__":
    # app.run(debug=True)
    # app.run()
    serve(app, host="0.0.0.0", port=5000)
    # app.run(ssl_context=('cert.pem', 'key.pem'))