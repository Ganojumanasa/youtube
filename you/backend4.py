from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import shutil
import logging

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlaylistRequest(BaseModel):
    playlist_url: str

@app.post("/download")
async def download_playlist(request: PlaylistRequest):
    playlist_url = request.playlist_url
    if not playlist_url:
        raise HTTPException(status_code=400, detail="Playlist URL is required")

    save_path = './vids'
    zip_path = './vids.zip'

    # Clean up previous files
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    if os.path.exists(zip_path):
        os.remove(zip_path)

    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': False,
        'progress_hooks': [lambda d: logger.info(f"Progress: {d.get('status', 'Unknown status')}")]  # Logging download progress
    }

    try:
        logger.info(f"Starting download from URL: {playlist_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
        
        # Archive the downloaded files into a zip file
        logger.info("Creating zip file...")
        shutil.make_archive('./vids', 'zip', save_path)

        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Failed to create zip file.")

        return {"message": "Download completed successfully! Files are being prepared for download."}
    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download playlist: {str(e)}")

@app.get("/download-zip")
async def download_zip():
    zip_path = './vids.zip'
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="No zip file found. Please request a download.")

    return FileResponse(zip_path, media_type='application/zip', filename='vids.zip')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
