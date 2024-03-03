import React, { useState, useEffect } from 'react';

function SRTUploader() {
  const [response, setResponse] = useState('');

  async function uploadSRT() {
    const srtData = `1
00:00:13,040 --> 00:00:15,120
i'd like to welcome people to
...
792
00:29:30,000 --> 00:29:32,240
all of these details are in the syllabus
um and i'll stick around and answer
questions hope to see you next week`;

    const blob = new Blob([srtData], { type: 'text/plain' });
    const formData = new FormData();
    formData.append('file', blob, 'transcript.srt');

    try {
      const response = await fetch('http://127.0.0.1:8000/upload-srt', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      setResponse(result.message);
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while uploading the SRT file');
    }
  }

  // useEffect hook to automatically call uploadSRT when the component mounts
  useEffect(() => {
    uploadSRT();
  }, []); // The empty array means this effect runs only once after the initial render

  return (
    <div>
      <div>Response: {response}</div>
    </div>
  );
}

export default SRTUploader;
