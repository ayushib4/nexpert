import React, { useState, useContext } from "react";
import { NodeContext } from "../NodeContext.js";
import "./styles/History.css";
import AccessTimeIcon from "@material-ui/icons/AccessTime";

const History = () => {
  const { nodeHistory, goToNodeInHistory } = useContext(NodeContext);
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseEnter = () => {
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
  };

  return (
    <div
      className={`history ${isHovering ? "expanded" : "collapsed"}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {!isHovering && (
        <div className="clock-icon">
          <AccessTimeIcon />
        </div>
      )}
      {isHovering && (
        <>
          <h3>Exploration History</h3>
          {nodeHistory?.map((nodeData, index) => (
            <div key={index}>
              <div
                className="nodeInHistory"
                onClick={() => goToNodeInHistory(nodeData)}
              >
                {nodeData.data.name}
              </div>
              {index + 1 !== nodeHistory.length && (
                <div className="arrow">↓</div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default History;
