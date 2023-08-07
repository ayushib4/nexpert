import { createContext, useState } from "react";
import "../src/App.css";

export const NodeContext = createContext();

const exampleTreeDataToRemove = {
  name: "",
  id: "",
  // parent: null,
  description: "",
  referenceUrl: [],
  children: [],
};

export function NodeProvider({ children }) {
  const [currentNode, setCurrentNode] = useState(null);
  const [treeData, setTreeData] = useState(exampleTreeDataToRemove);

  const [expandedNode, setExpandedNode] = useState(false);

  const [nodeHistory, setNodeHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const [scale, setScale] = useState(1);

  const handleNodeClick = (nodeData) => {
    setExpandedNode(true);
    setCurrentNode(nodeData);
    setNodeHistory((prev) => [...prev, nodeData]);
  };

  const goToNodeInHistory = (nodeData) => {
    setCurrentNode(nodeData);
    zoomToNode(nodeData.x, nodeData.y); // Zoom to the selected node
  };

  const zoomToNode = (x, y) => {
    const svgWidth = 800;
    const svgHeight = 800;

    setTranslate({
      x: svgWidth / 2 - x,
      y: svgHeight / 2 - y,
    });
  };

  return (
    <NodeContext.Provider
      value={{
        setCurrentNode,
        currentNode,
        nodeHistory,
        expandedNode,
        handleNodeClick,
        goToNodeInHistory,
        translate,
        scale,
        loading,
        setLoading,
        treeData,
        setTreeData,
      }}
    >
      {children}
    </NodeContext.Provider>
  );
}
