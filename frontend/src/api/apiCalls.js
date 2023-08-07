import axios from "axios";

const platform = window.navigator.platform

console.log(platform)

const BASE_URL = platform === 'Win32' ? 'http://127.0.0.1:8000' :'http://0.0.0.0:8000';

const exampleExpandedData = {
  url: "https://arxiv.org/pdf/1810.04805.pdf",
  concepts: [
    {
      name: "Concept 1",
      referenceUrl: "https://referenceUrl1",
      description: "This is a description of Concept 1",
      referenceText: "",
      id: "",
      parent: "",
      children: [],
    },
    {
      name: "Concept 2",
      referenceUrl: "https://referenceUrl2",
      description: "This is a description of Concept 2",
      referenceText: "",
      id: "",
      parent: "",
      children: [],
    },
    //... more concept nodes
  ],
};

export async function generateTwoLayers(searchTerm) {
  return axios
    .post(`${BASE_URL}/query`, { query: searchTerm })
    .then((response) => {
      console.log(response);
      return response.data;
    })
    .catch((error) => {
      console.error("Error sending query:", error);
      // instead of throwing the error, return an error indication
      return { error: true, message: error.message };
    });
}

// const paperInsights = await getLongDescription(node, node.data.name === "Residual calcium effects" ); // Add any necessary arguments

export async function getLongDescription(node, state) {
  delete node.data.__rd3t;
  delete node.data.depth;
  delete node.data.height;
  delete node.data.x;
  delete node.data.y;

  console.log(node.data);

  return axios
    .post(`${BASE_URL}/more-info`, node.data)
    .then((response) => {
      console.log(response);
      return response.data;
    })
    .catch((error) => {
      console.error("Error fetching text:", error);
      throw error;
    });
}

export async function expandGraphWithNewNodes(nodeId, query, node) {
  console.log(nodeId);

  return axios
    .post(`${BASE_URL}/expand-graph-with-new-nodes`, {
      id: nodeId,
      query: query,
      concept: node.data,
    })
    .then((response) => response.data)
    .catch((error) => {
      console.error("Error expanding graph with new nodes:", error);
      throw error;
    });
}
