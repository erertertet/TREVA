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

    return (
        <span onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave} style={{ position: 'relative', cursor: 'pointer' }}>
            <span style={{ fontWeight: isHovered ? 'bold' : 'normal' }}>
                {children}
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
                
                

                <Article sentences={[
    [
        "I'd like to welcome people to Introduction to Psychology. My name is Dr. Paul Bloom, and I'm the ",
        "professor for this course. Uh, if you haven't yet picked up a syllabus from the front of the class, ",
        "please raise your hand. Are we out? Are we at a syllabus? Oh, please raise your hand, and ",
        "when the teaching fellows will bring it to you. If you don't yet have a syllabus, um, ",
        "the syllabus is also available on this website. This website will become important to you should you choose to ",
        "take this class. It will include the syllabus, which will occasionally be revised well in advance. ",
        "Also, all of the class material will be on this site, including copies of the slides I'm presenting, including these ",
        "slides right now, practice exams, and any details on the written assignments. So you'll need to use this website ",
        "regularly to keep in touch with the course. Today will be a short class. What I just want ",
        "to do today is orient you, tell you what this course is about. I know this is shopping period, and I ",
        "want to give you a good sense of what you'd be in for if you took this course. I want to go over the style of the ",
        "classes, the evaluation, the readings, and so on, and then give some examples of some of ",
        "the specific topics that we'll be covering. But before I get started, I have to point ",
        "out something a little bit unusual about this class.\nWe are being filmed. This course is one of seven courses ",
        "chosen to begin the Yale University Open Educational Resources video lecture project. ",
        "And what this means is that when the year is over, these videos will be available on the ",
        "internet free for anybody who wants to see them, and ideally will be accessed by people ",
        "across many different countries, some who would not normally have access to a university education.\n",
        "I see this as a good and honorable use of Yale's resources. And of course, it's also part of Yale's plan for world ",
        "domination. So because of this, a Yale University production team from the Center of Media ",
        "Initiatives is going to be taping all the class lectures. The idea is that this should be as unobtrusive as",
        "as possible, and the classroom experience should essentially be the same as if they're ",
        "not there. So it's their intention to tape the lectures, to take me, and sometimes, uh, ",
        "the slides but not tape your faces or voices. So we're not having you sign release forms. \n",
        "Um, two things. One thing is, personally, I have to remind myself not to use profanity because children.\n",
        "may be watching so i'll try not to do that. there's also another complexity if you"
    ],
    [
        [
            "00:00:13,040",
            "00:00:18,960"
        ],
        [
            "00:00:18,960",
            "00:00:25,279"
        ],
        [
            "00:00:25,279",
            "00:00:32,079"
        ],
        [
            "00:00:32,079",
            "00:00:40,559"
        ],
        [
            "00:00:40,559",
            "00:00:47,360"
        ],
        [
            "00:00:47,360",
            "00:00:57,440"
        ],
        [
            "00:00:57,440",
            "00:01:03,680"
        ],
        [
            "00:01:03,680",
            "00:01:13,119"
        ],
        [
            "00:01:13,119",
            "00:01:19,600"
        ],
        [
            "00:01:19,600",
            "00:01:25,920"
        ],
        [
            "00:01:25,920",
            "00:01:31,840"
        ],
        [
            "00:01:31,840",
            "00:01:37,439"
        ],
        [
            "00:01:37,439",
            "00:01:44,159"
        ],
        [
            "00:01:44,159",
            "00:01:51,680"
        ],
        [
            "00:01:51,680",
            "00:01:58,719"
        ],
        [
            "00:01:58,719",
            "00:02:04,560"
        ],
        [
            "00:02:04,560",
            "00:02:10,959"
        ],
        [
            "00:02:10,959",
            "00:02:18,239"
        ],
        [
            "00:02:18,239",
            "00:02:24,400"
        ],
        [
            "00:02:24,400",
            "00:02:32,239"
        ],
        [
            "00:02:32,239",
            "00:02:39,440"
        ],
        [
            "00:02:39,440",
            "00:02:45,519"
        ],
        [
            "00:02:45,519",
            "00:02:52,239"
        ],
        [
            "00:02:52,239",
            "00:02:58,480"
        ],
        [
            "00:02:58,480",
            "00:03:05,200"
        ],
        [
            "00:03:05,200",
            "00:03:09,760"
        ]
    ]
]}></Article>
                <HoverSentence timestamp={12313}>aaaa aaaa</HoverSentence>
                <HoverSentence timestamp={12313}>aaaa aaaa</HoverSentence>
            </div>
        </>
    );
}

export default VideoUploader;
