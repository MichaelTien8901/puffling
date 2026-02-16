import { api } from "@/lib/api";

describe("API client", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  it("makes GET requests", async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    });

    const result = await api.get("/api/health");
    expect(result).toEqual({ status: "ok" });
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/health",
      expect.objectContaining({ headers: expect.any(Object) })
    );
  });

  it("makes POST requests with body", async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 1 }),
    });

    const result = await api.post("/api/strategies/", { name: "test" });
    expect(result).toEqual({ id: 1 });
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/strategies/",
      expect.objectContaining({ method: "POST", body: '{"name":"test"}' })
    );
  });

  it("throws on non-ok response", async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
    });

    await expect(api.get("/api/missing")).rejects.toThrow("API error: 404 Not Found");
  });
});
