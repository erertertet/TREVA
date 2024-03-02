import React, { useState } from "react";

function VideoUploader() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState("");

  async function uploadVideo(file) {
    const formData = new FormData();
    formData.append("video", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/transcribe", {
        method: "POST",
        body: formData, // FormData will set the `Content-Type` to `multipart/form-data` and include the boundary automatically
      });
      const data = await response.json();
      setResponse(data.message);
    } catch (error) {
      console.error("Error:", error);
      setResponse("An error occurred");
    }
  }

  function inputChanged(e) {
    // Check if user has selected a file and set it to state
    if (e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  }

  function handleUploadClick() {
    if (file && file.type === "video/mp4") {
      uploadVideo(file);
      setResponse("file uploaded");
    } else {
      setResponse("Please select a valid MP4 video file.");
    }
  }

  return (
    <>
      <input type="file" onChange={inputChanged} accept="video/mp4" />
      <button onClick={handleUploadClick}>Upload Video</button>
      <p>{response}</p>
    </>
  );
}

export default VideoUploader;
