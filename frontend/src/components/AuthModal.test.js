import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AuthModal from "./AuthModal";

const mockLogin = jest.fn();
const mockRegister = jest.fn();
const mockLoginUser = jest.fn();

jest.mock("../services/api", () => ({
  login: (...args) => mockLogin(...args),
  register: (...args) => mockRegister(...args),
}));

jest.mock("../context/AuthContext", () => ({
  useAuth: () => ({ loginUser: mockLoginUser }),
}));

describe("AuthModal", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();

    mockLogin.mockClear();
    mockRegister.mockClear();
    mockLoginUser.mockClear();

    jest.spyOn(window, "alert").mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("renders Sign In mode by default", () => {
    render(<AuthModal onClose={jest.fn()} />);

    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/your@email.com/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/johndoe/i)).not.toBeInTheDocument();
  });

  it("switches to register mode when toggle button clicked", async () => {
    render(<AuthModal onClose={jest.fn()} />);

    await user.click(
      screen.getByRole("button", { name: /new here\? create account/i })
    );

    expect(screen.getByRole("heading", { name: /create account/i })).toBeInTheDocument();
  });

  it("switches back to login mode from register mode", async () => {
    render(<AuthModal onClose={jest.fn()} />);

    await user.click(
      screen.getByRole("button", { name: /new here\? create account/i })
    );

    await user.click(
      screen.getByRole("button", { name: /already have an account\? sign in/i })
    );

    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
  });

  it("updates email and password inputs", async () => {
    render(<AuthModal onClose={jest.fn()} />);

    await user.type(screen.getByPlaceholderText(/your@email.com/i), "test@example.com");
    await user.type(screen.getByPlaceholderText(/••••••••/i), "secret123");

    expect(screen.getByPlaceholderText(/your@email.com/i)).toHaveValue("test@example.com");
    expect(screen.getByPlaceholderText(/••••••••/i)).toHaveValue("secret123");
  });

  it("calls onClose when Cancel button is clicked", async () => {
    const onClose = jest.fn();
    render(<AuthModal onClose={onClose} />);

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("logs in successfully", async () => {
    mockLogin.mockResolvedValueOnce({
      user: { email: "test@example.com", role: "customer" },
    });

    const onClose = jest.fn();

    render(<AuthModal onClose={onClose} />);

    await user.type(screen.getByPlaceholderText(/your@email.com/i), "test@example.com");
    await user.type(screen.getByPlaceholderText(/••••••••/i), "password");

    await user.click(screen.getByRole("button", { name: /^sign in$/i }));

    await waitFor(() =>
      expect(mockLoginUser).toHaveBeenCalledWith({
        email: "test@example.com",
        role: "customer",
      })
    );

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
    
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /^sign in$/i })).not.toBeDisabled()
    );

    expect(window.alert).toHaveBeenCalled();
  });

  it("shows error message when login fails", async () => {
    mockLogin.mockRejectedValueOnce({ detail: "Invalid credentials" });

    render(<AuthModal onClose={jest.fn()} />);

    await user.type(screen.getByPlaceholderText(/your@email.com/i), "bad@example.com");
    await user.type(screen.getByPlaceholderText(/••••••••/i), "wrong");

    await user.click(screen.getByRole("button", { name: /^sign in$/i }));

    await waitFor(() =>
      expect(screen.getByText("Invalid credentials")).toBeInTheDocument()
    );

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /^sign in$/i })).not.toBeDisabled()
    );
  });

  it("shows generic error when login fails with unknown error shape", async () => {
    mockLogin.mockRejectedValueOnce({});

    render(<AuthModal onClose={jest.fn()} />);

    await user.type(screen.getByPlaceholderText(/your@email.com/i), "a@b.com");
    await user.type(screen.getByPlaceholderText(/••••••••/i), "pass");

    await user.click(screen.getByRole("button", { name: /^sign in$/i }));

    await waitFor(() =>
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument()
    );

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /^sign in$/i })).not.toBeDisabled()
    );
  });

  it("registers successfully", async () => {
    mockRegister.mockResolvedValueOnce({});

    render(<AuthModal onClose={jest.fn()} />);

    await user.click(
      screen.getByRole("button", { name: /new here\? create account/i })
    );

    await user.type(screen.getByPlaceholderText(/johndoe/i), "john");
    await user.type(screen.getByPlaceholderText(/your@email.com/i), "john@example.com");

    const passwords = screen.getAllByPlaceholderText(/••••••••/i);
    await user.type(passwords[0], "pass123");
    await user.type(passwords[1], "pass123");

    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() =>
      expect(mockRegister).toHaveBeenCalled()
    );

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument()
    );

    await waitFor(() =>
      expect(screen.getByRole("button", { name: /^sign in$/i })).not.toBeDisabled()
    );
  });

  it("role select works", async () => {
    render(<AuthModal onClose={jest.fn()} />);

    await user.click(
      screen.getByRole("button", { name: /new here\? create account/i })
    );

    const roleSelect = screen.getByRole("combobox");

    expect(roleSelect).toHaveValue("customer");

    await act(async () => {
      await user.selectOptions(roleSelect, "admin");
    });

    expect(roleSelect).toHaveValue("admin");
  });
});