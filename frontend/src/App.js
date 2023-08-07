import React, { useState, useEffect, useContext } from "react";
import { NodeProvider, NodeContext } from "./NodeContext.js";
import Graph from "./components/Graph.js";
import History from "./components/History.js";
import PromptBar from "./components/PromptBar.js";

import "./App.css";

// This is where the data needs to be passed in...
// TODO: We need to do an array of papers and map over them to generate individual graphs

function App() {
  const [isPromptBarVisible, setPromptBarVisible] = useState(true);

  useEffect(() => {
    // Keep this later
    const handleKeyDown = (event) => {
      if (event.metaKey && event.key === "s") {
        event.preventDefault();
        setPromptBarVisible(true);
      }
      if (event.ctrlKey && event.key === "q") {
        event.preventDefault();
        setPromptBarVisible(true);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const closeSearchBar = () => {
    setPromptBarVisible(false);
  };

  return (
    <NodeProvider>
      <div className="App">
        {isPromptBarVisible && <PromptBar onClose={closeSearchBar} />}
        <History />
        {/* <ExpandedNode /> */}
        <Graph />
      </div>
    </NodeProvider>
  );
}

export default App;
