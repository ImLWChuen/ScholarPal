export async function checkApiHealth(signal: AbortSignal): Promise<void> {
  const response = await fetch("/api/health", { signal });
  if (!response.ok) {
    throw new Error(`Health check failed with HTTP ${response.status}`);
  }

  const { status } = await response.json();
  if (status !== "ok") {
    throw new Error("Unexpected API health response");
  }
}
