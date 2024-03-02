import React, { useState } from 'react';

function YouTubeLinkSender() {
    const [input, setInput] = useState("");
    const [response, setResponse] = useState("");

    const youtubeLinkRegex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;

    async function sendYouTubeLink(link) {
        try {
            const response = await fetch('http://127.0.0.1:8000/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ x: link }),
            });
            const data = await response.json();
            setResponse(data.message);
        } catch (error) {
            console.error('Error:', error);
            setResponse('An error occurred');
        }
    }

    function inputChanged(e) {
        const value = e.target.value;
        setInput(value);
    }

    function handleSendClick() {
        if (youtubeLinkRegex.test(input)) {
            sendYouTubeLink(input);
        } else {
            setResponse("Invalid YouTube link.");
        }
    }

    return (
        <>
            <input
                type="text"
                value={input}
                onChange={inputChanged}
                placeholder="Paste a YouTube link here..."
            />
            <button onClick={handleSendClick}>Send Link</button>
            <p>{response}</p>
        </>
    );
}

export default YouTubeLinkSender;
