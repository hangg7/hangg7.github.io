Launch a local dev server with hot reload on port 8081, accessible from LAN for phone testing.

Kill any existing process on port 8081, then start live-server in the background:
```
lsof -ti:8081 | xargs kill -9 2>/dev/null; sleep 1 && npx live-server --port=8081 --host=0.0.0.0
```

After starting, print the local URL (http://127.0.0.1:8081) and the LAN URL by running `ipconfig getifaddr en0` to get the local IP.
