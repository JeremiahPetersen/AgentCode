import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (typeof prompt !== "string") {
      console.error("Prompt is not a string:", prompt);
      return;
    }
    try {
      console.log({ prompt }); // Check what is being sent in the axios post request
      const result = await axios.post("http://localhost:5000/chat", { prompt });
      setResponse(result.data.response);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="container">
      <div className="textareaContainer">
        <div className="inputContainer">
          <textarea
            value={prompt}
            onChange={handleChange}
            className="inputArea"
          />
        </div>
        <div className="buttonContainer">
          <button onClick={handleSubmit} className="transformButton">
            Submit
          </button>
        </div>
        <div className="outputContainer">
          <textarea value={response} readOnly className="outputArea" />
        </div>
      </div>
    </div>
  );
}

export default App;
