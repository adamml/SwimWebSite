build:
	gcc -I. main.c .\swimwebsite\util.c .\swimwebsite\EPABeachInformation.c .\jsmn\jsmn.c -o swimwebsite.exe  -L.\lib  -lcurl -Wall
