# API

Call the API, get data.

### Sessions

Get data regarding user sessions

#### List Sessions
Find all sessions currently being tracked by the application

`URL = HOST:PORT + '/api/sessions'`

**Example URL**

http://127.0.0.1:8080/api/sessions

**Example Response**
````json
{
  "sessions": [
    "0.0.0.0-http://www-itec.uni-klu.ac.at", 
    "0.0.0.1-http://www-itec.uni-klu.ac.at"
  ]
}
````

#### Session Data
Return all data for specific session IDs. Get data for multiple sessions with one query by separating `session_id`s with commas.

`URL = HOST:PORT + '/api/sessions/' + session_id`

**Example URL**

http://127.0.0.1:8080/api/sessions/0.0.0.0-http://www-itec.uni-klu.ac.at

**Example Response**
````json
{
  "0.0.0.0-http://www-itec.uni-klu.ac.at": [
    {
      "mimeType": "video/mp4",
      "src_ip": "0.0.0.0",
      "timestamp": 1423839108,
      "file_": "bunny_2s4.m4s",
      "host": "http://www-itec.uni-klu.ac.at",
      "height": "1080",
      "startWithSAP": "1",
      "width": "1920",
      "bandwidth": "4219897",
      "codecs": "avc1",
      "duration": 2,
      "path": "ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/bunny_2s_8000kbit/bunny_2s4.m4s",
      "bitrate": 8000,
      "id": "19"
    }
  ]
}
````

**Optional Fields**

It's possible to retrieve only the fields that are useful for your application by using the "fields" query string parameter.

Field			| Description
:--------------	| :---------- 
mimeType		| Internet media type, indicates the type of content requested
src_ip			| IP address of the client requesting content
timestamp		| Epoch time when the get request was received
file_			| The file requested
host			| Destination IP/hostname of the get request
height			| Height of the requested video in pixels
width			| Width of the requested video in pixels
startsWithSAP	| *N/A*
bandwidth		| Size of the requested segment in bytes (please confirm?)
codecs			| The codec the requested segment has been encoded with
duration		| The duration of the segment in seconds
path			| The full path as present in the URL
bitrate			| The bitrate of the video segment
id				| *N/A*

**Example URL**

http://127.0.0.1:8080/api/sessions/0.0.0.0-http://www-itec.uni-klu.ac.at?fields=timestamp,file_

**Example Response**
````json
{
  "0.0.0.0-http://www-itec.uni-klu.ac.at": [
	{
		"timestamp": 1423839108,
		"file_": "bunny_2s4.m4s"
    },
    {
		"timestamp": 1423839109,
		"file_": "bunny_2s5.m4s"
    }
  ]
}
````
