import { useEffect, useState } from "react";
import { checkApiHealth } from "./api/health";

export function App() {
  const [status, setStatus] = useState("Checking API connection…");

  useEffect(() => {
    const controller = new AbortController();
    checkApiHealth(controller.signal)
      .then(() => setStatus("API connected."))
      .catch(() => {
        if (!controller.signal.aborted) {
          setStatus("API unavailable. Start the FastAPI server and reload.");
        }
      });
    return () => controller.abort();
  }, []);

  return (
    <main>
      <h1>ScholarPal</h1>
      <p role="status">{status}</p>
    </main>
  );
}
