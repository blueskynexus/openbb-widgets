# SETUP
Create a `.env` file and add your `VIANEXUS_API_KEY`
```.env
VIANEXUS_API_KEY="pk_xxx"
```

Start the server:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 7779
```

Go to https://pro.openbb.co/app, select Connect Backend, and add your server