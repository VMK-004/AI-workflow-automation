import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { Test } from "./Test.tsx";

// Temporary: Test if React renders at all
const USE_TEST_MODE = false;

createRoot(document.getElementById("root")!).render(
  <StrictMode>{USE_TEST_MODE ? <Test /> : <App />}</StrictMode>
);
