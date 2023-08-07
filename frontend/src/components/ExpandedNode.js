import React, { useContext, useEffect, useState } from "react";
import { NodeContext } from "../NodeContext.js";
import "./styles/ExpandedNode.css";
import { Close } from "@material-ui/icons";

function ExpandedNode({ modalOnClose, children }) {
  const { currentNode, loading, treeData, expandedNode } =
    useContext(NodeContext);
  const [foundNode, setFoundNode] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const findNode = (node, id) => {
    if (node.id === id) {
      return node;
    }

    if (node.children) {
      for (let child of node.children) {
        const result = findNode(child, id);
        if (result) {
          return result;
        }
      }
    }

    return null;
  };

  useEffect(() => {
    if (currentNode && treeData) {
      setFoundNode(findNode(treeData, currentNode.data.id));
    }
  }, [currentNode, treeData]);

  useEffect(() => {
    if (expandedNode) {
      setModalOpen(true);
    }
  }, [expandedNode]);

  const _onClose = () => setModalOpen(false);

  return (
    treeData && (
      <div className="expandedNode">
        {loading && <div className="noNodeTag">Loading...</div>}
        {!loading && foundNode && (
          <div>
            <div
              className="nodeTag"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <h3>{foundNode.name}</h3>
              <button
                onClick={modalOnClose}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "white",
                }}
              >
                <Close />
              </button>
            </div>
            <div className="nodeTag">{foundNode.description}</div>
            <button
              className="nodeTag"
              style={{
                background: "#758dbe",
                border: "#758dbe",
                cursor: "pointer",
                color: "white",
                width: "100px",
                height: "25px",
                textAlign: "center",
              }}
            >
              <a href={foundNode?.referenceUrl} target="_blank">
                Open paper
              </a>
            </button>
          </div>
        )}
        {children}
      </div>
    )
  );
}

export default ExpandedNode;
