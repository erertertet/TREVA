import React, { useState } from 'react';

function VideoUploader() {
    const [file, setFile] = useState(null);
    const [response, setResponse] = useState("");

    async function uploadVideo(file) {
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            setResponse(data.message);
        } catch (error) {
            console.error('Error:', error);
            setResponse('An error occurred');
        }
    }

    function inputChanged(e) {
        // Check if user has selected a file and set it to state
        if (e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    }

    function handleUploadClick() {
        console.log(file.type)
        if (file) {
            uploadVideo(file);
            setResponse("file uploaded")
        } else {
            setResponse("Please select a valid MP4 video file.");
        }
    }

    return (
        <>
            <div className="flex">
                <input
                    type="file"
                    onChange={inputChanged}
                    accept="multipart/form-data"
                />
                <button onClick={handleUploadClick}>Upload SRT File</button>

            </div>
            <div className="note">
                {response}
            </div>
        </>
    );
}

export default VideoUploader;
