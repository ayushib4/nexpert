import React, { useContext, useEffect, useState } from "react";
import Tree from "react-d3-tree";
import cloneDeep from "lodash/cloneDeep";
import ExpandedNode from "./ExpandedNode.js";
import { NodeContext } from "../NodeContext.js";
import { Modal } from "@mui/material";

import {
  getLongDescription,
  expandGraphWithNewNodes,
} from "../api/apiCalls.js"; // or wherever your API functions are stored
import "./styles/Graph.css";

// Helper functions
function mergeData(nodeId, treeData, expandedData) {
  // Function to recursively search for a node
  function findNode(node) {
    if (node.id === nodeId) {
      // Node found, append children
      node.children = expandedData.children;
    } else if (node.children) {
      // Node not found, search children
      node.children.forEach(findNode);
    }
  }

  // Make a deep copy of the tree data and search it
  const newTreeData = cloneDeep(treeData);
  findNode(newTreeData);

  return newTreeData;
}

// Function to recursively update node description
function updateDescription(node, currentNode, longDescription) {
  if (node.id === currentNode.id) {
    // Return a new object for the node
    return { ...node, description: longDescription };
  }
  if (node.children) {
    // Iterate through children, creating new objects for any that have changed
    return {
      ...node,
      children: node.children.map((child) =>
        updateDescription(child, currentNode, longDescription),
      ),
    };
  }
  // No changes to this node or its children
  return node;
}

const getLongDesc = async (node, callbackFunc, currentTreeData) => {
  return new Promise(async (resolve, reject) => {
    try {
      console.log(currentTreeData.name);
      const paperInsights = await getLongDescription(
        node,
        node.data.name === "Residual calcium effects",
      ); // Add any necessary arguments
      // Update node description in treeData
      const updatedTreeData = updateDescription(
        currentTreeData,
        node.data,
        paperInsights,
      );
      callbackFunc(updatedTreeData);
      resolve(updatedTreeData); // Return the updated data
    } catch (error) {
      reject(error);
    }
  });
};

const expandGraph = async (node, callbackFunc, currentTreeData) => {
  const expandedGraphData = await expandGraphWithNewNodes(
    node.data.id,
    currentTreeData.name,
    node,
  );
  const newTreeData = mergeData(
    node.data.id,
    currentTreeData,
    expandedGraphData,
  );
  callbackFunc(newTreeData);
};

// Main component
const Graph = () => {
  const {
    scale,
    translate,
    handleNodeClick,
    currentNode,
    setLoading,
    treeData,
    setTreeData,
    expandedNode,
  } = useContext(NodeContext);
  const [modalOpen, setModalOpen] = useState(false);
  useEffect(() => {
    if (!currentNode) return;

    const fetchData = async () => {
      try {
        if (currentNode && currentNode.data) {
          setLoading(true);
          const updatedTreeData = await getLongDesc(
            currentNode,
            setTreeData,
            treeData,
          );
          await expandGraph(currentNode, setTreeData, updatedTreeData);
          setLoading(false);
        }
      } catch (error) {
        console.error("An error occurred while fetching data:", error);
      }
    };

    fetchData();
  }, [currentNode, setLoading, setTreeData, treeData]);

  const onClick = (nodeData) => {
    handleNodeClick(nodeData);
    setModalOpen(true);
  };

  useEffect(() => {
    if (expandedNode) {
      setModalOpen(true);
    }
  }, [expandedNode]);

  const _onClose = () => setModalOpen(false);

  return (
    <>
      <Modal open={modalOpen} close={_onClose}>
        <ExpandedNode modalOnClose={_onClose} />
      </Modal>
      <div className="graph" style={{ transform: `scale(${scale})` }}>
        <div className="helperText">
          <i>
            Use cmd-s (in mac) or ctrl-q (in windows) to open the prompt editor.
          </i>
        </div>
        {treeData && (
          <Tree
            data={treeData}
            translate={translate}
            onNodeClick={onClick}
            separation={{ siblings: 1, nonSiblings: 1 }}
            // pathFunc="step"
            rootNodeClassName="node__root"
            branchNodeClassName="node__branch"
            leafNodeClassName="node__leaf"
          />
        )}
      </div>
    </>
  );
};

export default Graph;
