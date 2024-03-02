import React, { useState } from 'react';

function SendButton() {
    const [input, setInput] = useState("");

    const [response, setResponse] = useState("");

    async function send() {
        try {
            const response = await fetch(
                'http://127.0.0.1:8000/test',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ x: input }),
                });
            const data = await response.json();
            // Assuming the API response contains a field 'message'
            setResponse(data.message);
        } catch (error) {
            console.error('Error:', error);
            setResponse('An error occurred');
        }
    }

    function input_changed(e) {
        setInput(e.target.value);
    }

    return (
        <>
            <input type="text" value={input} onChange={input_changed} />
            <button onClick={send}>Send</button>
            <p>{response}</p>
        </>
    );
}

export default SendButton;

