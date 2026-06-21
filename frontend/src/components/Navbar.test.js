import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Navbar from "./Navbar";

const mockUseCart = jest.fn();
const mockUseAuth = jest.fn();

jest.mock("../context/CartContext", () => ({
  useCart: () => mockUseCart(),
}));

jest.mock("../context/AuthContext", () => ({
  useAuth: () => mockUseAuth(),
}));

jest.mock("./AuthModal", () => ({ onClose }) => (
  <div data-testid="auth-modal">
    <button onClick={onClose}>Close</button>
  </div>
));

function renderNavbar(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Navbar />
    </MemoryRouter>
  );
}

describe("Navbar", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();

    mockUseCart.mockReturnValue({ cart: [] });
    mockUseAuth.mockReturnValue({ user: null });
  });

  it("renders all navigation links", () => {
    renderNavbar();

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText("Products")).toBeInTheDocument();
    expect(screen.getByText("Integrations")).toBeInTheDocument();
    expect(screen.getByText("Support")).toBeInTheDocument();
  });

  it("renders the MediCare AI logo", () => {
    renderNavbar();

    expect(screen.getByText("MediCare AI")).toBeInTheDocument();
  });

  it("renders cart icon link", () => {
    renderNavbar();

    expect(screen.getByText("🛒")).toBeInTheDocument();
  });

  it("shows no cart badge when cart is empty", () => {
    mockUseCart.mockReturnValue({ cart: [] });
    renderNavbar();

    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("shows cart badge with item count when cart has items", () => {
    mockUseCart.mockReturnValue({ cart: [{ id: 1 }, { id: 2 }, { id: 3 }] });
    renderNavbar();

    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("shows Sign In button when user is not authenticated", () => {
    mockUseAuth.mockReturnValue({ user: null });
    renderNavbar();

    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.queryByText(/profile/i)).not.toBeInTheDocument();
  });

  it("shows Profile link when user is authenticated", () => {
    mockUseAuth.mockReturnValue({ user: { name: "Test User" } });
    renderNavbar();

    expect(screen.getByText("👤 Profile")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /sign in/i })).not.toBeInTheDocument();
  });

  it("opens AuthModal when Sign In button is clicked", async () => {
    mockUseAuth.mockReturnValue({ user: null });
    renderNavbar();

    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByTestId("auth-modal")).toBeInTheDocument();
  });

  it("closes AuthModal when onClose is called", async () => {
    mockUseAuth.mockReturnValue({ user: null });
    renderNavbar();

    await user.click(screen.getByRole("button", { name: /sign in/i }));
    expect(screen.getByTestId("auth-modal")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /close/i }));
    expect(screen.queryByTestId("auth-modal")).not.toBeInTheDocument();
  });

  it("does not render AuthModal initially", () => {
    renderNavbar();

    expect(screen.queryByTestId("auth-modal")).not.toBeInTheDocument();
  });
});