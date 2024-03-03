import React, { useState, useEffect } from 'react';

function HoverSentence({ children, timestamp }) {
    const [isHovered, setIsHovered] = useState(false);
    const [timer, setTimer] = useState(null);

    // Function to show the timestamp and highlight
    const handleMouseEnter = () => {
        // Set a timer to change the state after 1 second
        const newTimer = setTimeout(() => {
            setIsHovered(true);
        }, 1000);
        setTimer(newTimer);
    };

    // Function to hide the timestamp and remove highlight
    const handleMouseLeave = () => {
        // Clear the timer if the mouse leaves before 1 second
        if (timer) {
            clearTimeout(timer);
            setTimer(null);
        }
        setIsHovered(false);
    };

    // Clean up the timer if the component is unmounted while hovering
    useEffect(() => {
        return () => {
            if (timer) {
                clearTimeout(timer);
            }
        };
    }, [timer]);

    const parts = children.split("\n");

    const formattedParts = parts.map((part, index) => (
        <React.Fragment key={index}>
          <span>{part}</span>
          {index < parts.length - 1 && <><br /><span><br /></span></>}
        </React.Fragment>
      ));

    return (
        <span onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} style={{ position: 'relative', cursor: 'pointer' }}>
            <span style={{ fontWeight: isHovered ? 'bold' : 'normal' }}>
                {formattedParts}
            </span>
            {isHovered && (
                <div style={{ position: 'absolute', top: '-20px', left: 0, backgroundColor: "rgba(0,0,0,0.5)", padding: '2px', color: 'white' }}>
                    {timestamp}
                </div>
            )}
        </span>
    );
}

function Article({ sentences }) {

    const zipped = sentences[0].map((element, index) => [element, sentences[1][index]]);


    console.log(zipped, "???")

    return (
        <>
            {zipped.map((x) => {
                return <HoverSentence timestamp={x[1][0] + "->" + x[1][1]}>{x[0]}</HoverSentence>
            })}
        </>
    )
}

function VideoUploader() {
    const [file, setFile] = useState(null);
    const [response, setResponse] = useState([[],[]]);

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
            // setResponse('An error occurred');
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
            // setResponse("file uploaded")
        } else {
            // setResponse("Please select a valid MP4 video file.");
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
                
                

                <Article sentences={response}></Article>
            </div>
        </>
    );
}

export default VideoUploader;
