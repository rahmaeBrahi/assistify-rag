import { act, renderHook, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "./AuthContext";

const mockGetMe = jest.fn();
const mockLogout = jest.fn();

jest.mock("../services/api", () => ({
  getMe: () => mockGetMe(),
  logout: () => mockLogout(),
}));

afterEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});

describe("AuthContext", () => {
  it("starts with user null and loading true, then finishes loading when no token", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.user).toBeNull();
    expect(mockGetMe).not.toHaveBeenCalled();
  });

  it("fetches user from token on mount when token exists", async () => {
    localStorage.setItem("access_token", "token123");
    mockGetMe.mockResolvedValueOnce({ name: "InitUser", email: "init@example.com" });

    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.user).toEqual({
      name: "InitUser",
      email: "init@example.com",
    });

    expect(mockGetMe).toHaveBeenCalledTimes(1);
  });

  it("calls apiLogout and leaves user null when getMe fails", async () => {
    localStorage.setItem("access_token", "bad-token");
    mockGetMe.mockRejectedValueOnce(new Error("Unauthorized"));

    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.user).toBeNull();
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it("loginUser sets the user", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      result.current.loginUser({ name: "Tester", email: "tester@example.com" });
    });

    expect(result.current.user).toEqual({
      name: "Tester",
      email: "tester@example.com",
    });
  });

  it("logoutUser sets user to null and calls apiLogout", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      result.current.loginUser({ name: "Tester" });
    });

    act(() => {
      result.current.logoutUser();
    });

    expect(result.current.user).toBeNull();
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it("updateUser merges partial data into existing user", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      result.current.loginUser({ name: "Tester", email: "old@example.com" });
    });

    act(() => {
      result.current.updateUser({ email: "new@example.com", phone: "123" });
    });

    expect(result.current.user).toEqual({
      name: "Tester",
      email: "new@example.com",
      phone: "123",
    });
  });

  it("updateUser does not erase unrelated user fields", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      result.current.loginUser({
        name: "Tester",
        role: "admin",
        email: "t@t.com",
      });
    });

    act(() => {
      result.current.updateUser({ email: "updated@t.com" });
    });

    expect(result.current.user.name).toBe("Tester");
    expect(result.current.user.role).toBe("admin");
  });

  it("exposes all auth methods and state", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(typeof result.current.loginUser).toBe("function");
    expect(typeof result.current.logoutUser).toBe("function");
    expect(typeof result.current.updateUser).toBe("function");
    expect(typeof result.current.user).toBeDefined();
    expect(typeof result.current.loading).toBe("boolean");
  });
});