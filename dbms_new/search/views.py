from __future__ import print_function
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
import pymongo
from bson.json_util import dumps
from bson.json_util import loads
from py2neo import *
from datetime import datetime
import mysql.connector
import random


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            #username = form.cleaned_data.get('username')
            #raw_password = form.cleaned_data.get('password1')
            #user = authenticate(username=username, password=raw_password)
            #login(request, user)
            return redirect('/login')
    else:
        form = UserCreationForm()
    return render(request, 'start/signup.html', {'form': form})


def index(request):
    videoIDs = None
    file_data = None
    datal = []
    relevant_data = None
    cur_user = request.user
    if request.GET.get('terms'):
        search_key = request.GET.get('terms')
        InsertToSQL(cur_user.username,search_key);
        videoIDs = relevantVideoData(relevantVideoID(search_key))
        statement = 'No Search data found';
        statement2 = 'Enter key words present in Data-base'
        if videoIDs:
            return render(request,'start/input.html',{
                'videoIDs': videoIDs,
            })
        else:
            return render(request,'start/input.html',{
                'string':statement,
                'string2':statement2
             })
    if request.GET.get('q'):
        req_id = request.GET.get('q')
        CrvToSQL(cur_user.username,req_id)
        file_data = CurrentVideoData(req_id)
        datal.append(file_data)
        ids = RelatedVideoID(req_id)
        relevant_data = relevantVideoData(ids)
        statement = 'No Related Videos Found'
        if relevant_data:
            return render(request, 'start/input.html', {
                'data': datal,
                'rel_data': relevant_data,
            })
        else:
            return render(request,'start/input.html',{
                'data':datal,
                'no_rel_data': statement,
            })
    if request.GET.get('videos'):
        req = request.GET.get('videos');
        videoIDs = relevantVideoData(getVideoslist(req));
        return render(request, 'start/input.html', {
            'channel_list': videoIDs,
        })

    if request.GET.get('type'):
        req  = request.GET.get('type');
        if req == 'history':
            videoIDs = relevantVideoData(getVideoId(cur_user.username))
            statement = 'No Recent Videos'
            statement2 = 'P.s: Watch few videos and come back :P'
            if videoIDs:
                return render(request, 'start/input.html', {
                    'videoIDs': videoIDs,
                })
            else:
                return render(request, 'start/input.html', {
                    'string': statement,
                    'string2': statement2,
                })
        if req == 'query':
            que = getVideoQuery(cur_user.username);
            #return HttpResponse("<html><h1>HI</Hi></html>")
            statement = 'No Recent Queries'
            statement2 = 'Happy Searching :)'
            if que:
                return render(request, 'start/input.html', {
                    'ques': que,
                })
            else:
                return render(request,'start/input.html',{
                    'string':statement,
                    'string2':statement2,
                })
        if req == 'bore':
            videoIDs = relevantVideoData(getRandom());
            return render(request, 'start/input.html', {
                'videoIDs': videoIDs,
            })

        if req == 'clear':
            clear_datamysql(cur_user.username);
            return render(request,'start/input.html')

    else:
        return render(request,'start/input.html')


################################################################################################################################################

def getVideoslist(req):
    connection = pymongo.MongoClient("mongodb://localhost:27017/")
    db = connection.new_database
    coll = db.test_collection
    arrayjson = coll.find()
    arrayjson = dumps(arrayjson)
    arrayjson = loads(arrayjson)
    flist = []
    for i in range(len(arrayjson)):
        if req == arrayjson[i]['videoInfo']['snippet']['channelId']:
            flist.append(arrayjson[i]['videoInfo']['id'])

    return flist;

def clear_datamysql(usern):
    cnx = mysql.connector.connect(user='root', password='kittu007', database='dbms');
    cursor = cnx.cursor();
    if (usern):
        cursor.execute("DELETE FROM query_data WHERE user_id = " + "'" +usern+"'");
        cursor.execute("DELETE FROM crv_data WHERE user_id = " + "'" +usern+"'");
    else:
        cursor.execute("DELETE FROM query_data WHERE user_id = ' ' " );
        cursor.execute("DELETE FROM crv_data WHERE user_id = ' '" );
    #cursor.execute("CREATE TABLE query_data(user_id varchar(50),query varchar(50), cur_time varchar(50))");
   # cursor.execute("CREATE TABLE crv_data(user_id varchar(50), crv_id varchar(50), cur_time varchar(50))");
    cnx.commit()
    cursor.close()
    cnx.close()

def getRandom():
    connection = pymongo.MongoClient("mongodb://localhost:27017/")
    db = connection.new_database
    coll = db.test_collection
    arrayjson = coll.find()
    arrayjson = dumps(arrayjson)
    arrayjson = loads(arrayjson)
    vals = {}
    flist = []
    int_r = random.sample(range(0,499),5);
    for i in int_r:
        flist.append(arrayjson[i]['videoInfo']['id']);
    arrayjson  = None
    return flist


def getVideoQuery(userid):
    que = [];
    us = (userid)
    cnx = mysql.connector.connect(user='root', password='kittu007', database='dbms')
    cursor = cnx.cursor()
    cmd = "SELECT query FROM query_data WHERE user_id = '"+userid+"' ORDER BY cur_time DESC LIMIT 15 "
    cursor.execute(cmd,us)
    result = cursor.fetchall()
    for row in result:
        que.append("%s" % (row[0]))
    cursor.close()
    cnx.close()
    return que

def getVideoId(userid):
    data = [];
    cnx = mysql.connector.connect(user='root', password='kittu007', database='dbms')
    cursor = cnx.cursor()
    cmd = "SELECT crv_Id FROM crv_data  WHERE user_id = '"+userid+"' ORDER BY cur_time DESC LIMIT 10 "
    cursor.execute(cmd)

    result = cursor.fetchall()
    for row in result:
        data.append("%s" % (row[0]))
    cursor.close()
    cnx.close()
    return data

def InsertToSQL(userid,w):
    cnx = mysql.connector.connect(user='root',password = 'kittu007', database='dbms')
    cursor = cnx.cursor()
    cur_time = (str(datetime.now()))
    add_data = "INSERT INTO query_data " "(user_id,query,cur_time) " "VALUES (%s,%s,%s)"
    data = (userid,w,cur_time)
    cursor.execute(add_data, data)
    # Make sure data is committed to the database
    cnx.commit()
    cursor.close()
    cnx.close()

def CrvToSQL(userid,w):
    cnx = mysql.connector.connect(user='root',password = 'kittu007', database='dbms')
    cursor = cnx.cursor()
    cur_time = (str(datetime.now()))
    add_data = "INSERT INTO crv_data " "(user_id,crv_Id,cur_time) " "VALUES (%s,%s,%s)"
    data = (userid,w,cur_time)
    cursor.execute(add_data, data)
    # Make sure data is committed to the database
    cnx.commit()
    cursor.close()
    cnx.close()

def descriptionCompare(description1, description2):
    word_description1 = description1.split()
    word_description2 = description2.split()
    word_description1 = [x.lower() for x in word_description1]
    word_description2 = [x.lower() for x in word_description2]
    count = len(set(word_description2) & set(word_description1))
    return count


def titleCompare(description1, description2):
    word_description1 = description1.split()
    word_description2 = description2.split()
    word_description1 = [x.lower() for x in word_description1]
    word_description2 = [x.lower() for x in word_description2]
    count = len(set(word_description2) & set(word_description1))
    return count


def tagsCompare(tags1, tags2):
    return len(set(tags1) & set(tags2))


def relevantVideoID(s):
    connection = pymongo.MongoClient("mongodb://localhost:27017/")
    db = connection.new_database
    coll = db.test_collection
    arrayjson = coll.find()
    arrayjson = dumps(arrayjson)
    arrayjson = loads(arrayjson)
    vals = {}
    flist = []
    for i in range(len(arrayjson)):
        if 'title' in arrayjson[i]['videoInfo']['snippet']:
            titleCount = titleCompare(arrayjson[i]['videoInfo']['snippet']['title'], s)

        if 'description' in arrayjson[i]['videoInfo']['snippet']:
            descCount = descriptionCompare(arrayjson[i]['videoInfo']['snippet']['description'], s)

        vals[arrayjson[i]['videoInfo']['id']] = titleCount + descCount
    i = 0
    for w in sorted(vals, key=vals.get, reverse=True):
        if vals[w] > 0 and i < 5:
            flist.append(w)
            i = i + 1

    arrayjson = None
    vals = None
    return flist




def relevantVideoData(flist):
	connection = pymongo.MongoClient("mongodb://localhost:27017/")
	db = connection.new_database
	coll = db.test_collection
	arrayjson = []
	desc = ""
	for w in flist:
		a = coll.find({"videoInfo.id":w},{"videoInfo.id":1,"videoInfo.snippet.localized.title":1,"_id":0,"videoInfo.snippet.thumbnails.default":1,"videoInfo.snippet.localized.description":1})
		a = dumps(a)
		a = loads(a)
		data = a[0]['videoInfo']['snippet']['localized']['description']
		a[0]['videoInfo']['snippet']['localized']['description'] = (data[:210] + '  .........') if len(data) > 110 else data
		arrayjson.append(a[0])
	return arrayjson


def RelatedVideoID(w):
	graph = Graph("http://neo4j:2580@localhost:7474/db/data/")
	query = "MATCH (n)-[r:`Matching Description`]->(n1)<-[r1:`Matching Tags`]-(n) where n.name = \""+w+"\" and r.weightage > 15 and r1.weightage > 1 return n1.name,r.weightage,r1.weightage order by (r.weightage) desc"
	res = graph.data(query)
	vals = {}
	for w in res:
		vals[w['n1.name']] = w['r.weightage'] + 0.7*w['r1.weightage'];
	result = []

	i=0
	for w in sorted(vals,key=vals.get,reverse=True):
		if i < 5:
			result.append(w)
			i=i+1
	return result

def CurrentVideoData(w):
	connection = pymongo.MongoClient("mongodb://localhost:27017/")
	db = connection.new_database
	coll = db.test_collection
	a = coll.find({"videoInfo.id":w},{"videoInfo.id":1,"videoInfo.snippet.localized.title":1,"videoInfo.snippet.thumbnails.high":1,"_id":0,"videoInfo.snippet.localized.description":1,"videoInfo.snippet.channelTitle":1,"videoInfo.snippet.channelId":1,"videoInfo.statistics":1})
	a = dumps(a)
	a = loads(a)
	return a[0]







