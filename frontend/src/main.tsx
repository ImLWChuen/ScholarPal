import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./index.css";

const root = document.getElementById("root");
if (!root) {
  throw new Error("ScholarPal requires a root element");
}

createRoot(root).render(<App />);
