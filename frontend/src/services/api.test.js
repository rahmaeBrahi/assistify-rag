import {
  login,
  logout,
  register,
  getMe,
  updateMe,
  fetchProducts,
  fetchOffers,
  fetchProductById,
  placeOrder,
  sendChatMessage,
} from "./api";

const OLD_FETCH = global.fetch;

beforeEach(() => {
  localStorage.clear();
  global.fetch = jest.fn();
});

afterEach(() => {
  global.fetch = OLD_FETCH;
  jest.clearAllMocks();
});

function mockOk(body) {
  global.fetch.mockResolvedValueOnce({ ok: true, json: async () => body });
}

function mockFail(body) {
  global.fetch.mockResolvedValueOnce({ ok: false, json: async () => body });
}

describe("api — login", () => {
  it("calls the login endpoint with correct payload", async () => {
    mockOk({ access: "x", refresh: "y" });

    await login({ email: "a@b.com", password: "pass" });

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/login/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ email: "a@b.com", password: "pass" }),
      })
    );
  });

  it("stores access and refresh tokens on success", async () => {
    mockOk({ access: "tok-access", refresh: "tok-refresh" });

    await login({ email: "a@b.com", password: "pass" });

    expect(localStorage.getItem("access_token")).toBe("tok-access");
    expect(localStorage.getItem("refresh_token")).toBe("tok-refresh");
  });

  it("returns the response data on success", async () => {
    mockOk({ access: "x", refresh: "y", user: { email: "a@b.com" } });

    const result = await login({ email: "a@b.com", password: "pass" });

    expect(result).toEqual({ access: "x", refresh: "y", user: { email: "a@b.com" } });
  });

  it("throws response body on non-ok response", async () => {
    mockFail({ detail: "Not authorized" });

    await expect(login({ email: "a", password: "b" })).rejects.toEqual({
      detail: "Not authorized",
    });
  });

  it("does not store tokens when login fails", async () => {
    mockFail({ detail: "Bad credentials" });

    try { await login({ email: "a", password: "b" }); } catch {}

    expect(localStorage.getItem("access_token")).toBeNull();
  });
});

describe("api — logout", () => {
  it("removes access_token from localStorage", () => {
    localStorage.setItem("access_token", "abc");
    logout();
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("removes refresh_token from localStorage", () => {
    localStorage.setItem("refresh_token", "def");
    logout();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });
});

describe("api — register", () => {
  it("calls register endpoint with correct payload", async () => {
    mockOk({ id: 1 });

    await register({ username: "john", email: "j@j.com", password: "p", password2: "p", role: "customer" });

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/register/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ username: "john", email: "j@j.com", password: "p", password2: "p", role: "customer" }),
      })
    );
  });

  it("throws on registration failure", async () => {
    mockFail({ email: ["Already exists."] });

    await expect(
      register({ username: "j", email: "dup@j.com", password: "p", password2: "p", role: "customer" })
    ).rejects.toEqual({ email: ["Already exists."] });
  });
});

describe("api — getMe", () => {
  it("calls /auth/me/ with Authorization header from token", async () => {
    localStorage.setItem("access_token", "abc123");
    mockOk({ id: 1, email: "me@me.com" });

    const result = await getMe();

    expect(result).toEqual({ id: 1, email: "me@me.com" });
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/me/",
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: "Bearer abc123",
          "Content-Type": "application/json",
        }),
      })
    );
  });

  it("does not include Authorization header when no token", async () => {
    mockOk({ id: 1 });

    await getMe();

    const callHeaders = global.fetch.mock.calls[0][1].headers;
    expect(callHeaders.Authorization).toBeUndefined();
  });
});

describe("api — updateMe", () => {
  it("calls PATCH /auth/me/ with provided data", async () => {
    localStorage.setItem("access_token", "tok");
    mockOk({ id: 1, email: "updated@me.com" });

    await updateMe({ email: "updated@me.com" });

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/auth/me/",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ email: "updated@me.com" }),
      })
    );
  });
});

describe("api — fetchProducts", () => {
  it("calls /products/ without query when search is empty", async () => {
    mockOk({ results: [] });

    await fetchProducts();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/products/",
      expect.any(Object)
    );
  });

  it("appends search query param when search string provided", async () => {
    mockOk({ results: [] });

    await fetchProducts("pulse");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/products/?search=pulse",
      expect.any(Object)
    );
  });

  it("URL-encodes special characters in search", async () => {
    mockOk({ results: [] });

    await fetchProducts("pulse oximeter");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/products/?search=pulse%20oximeter",
      expect.any(Object)
    );
  });
});

describe("api — fetchOffers", () => {
  it("calls /products/offers/", async () => {
    mockOk([]);

    await fetchOffers();

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/products/offers/",
      expect.any(Object)
    );
  });
});

describe("api — fetchProductById", () => {
  it("calls /products/:id/", async () => {
    mockOk({ id: 5, name: "Oximeter" });

    await fetchProductById(5);

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/products/5/",
      expect.any(Object)
    );
  });
});

describe("api — placeOrder", () => {
  it("calls POST /orders/ with correct payload", async () => {
    mockOk({ id: 1 });

    await placeOrder({
      customerEmail: "a@b.com",
      paymentMethod: "cod",
      deliveryAddress: "Cairo",
      phone: "01000000000",
      items: [{ product: 1, qty: 1 }],
    });

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/orders/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          customer_email: "a@b.com",
          payment_method: "cod",
          delivery_address: "Cairo",
          phone: "01000000000",
          items: [{ product: 1, qty: 1 }],
        }),
      })
    );
  });
});

describe("api — sendChatMessage", () => {
  it("calls POST /chat/ and returns reply and conversationId", async () => {
    mockOk({ reply: "Hello!", conversation_id: "conv-1" });

    const result = await sendChatMessage("Hi", null);

    expect(result).toEqual({ reply: "Hello!", conversationId: "conv-1" });
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/chat/",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ message: "Hi", conversation_id: null }),
      })
    );
  });

  it("passes existing conversationId in payload", async () => {
    mockOk({ reply: "OK", conversation_id: "conv-existing" });

    await sendChatMessage("Next message", "conv-existing");

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: JSON.stringify({ message: "Next message", conversation_id: "conv-existing" }),
      })
    );
  });
});
