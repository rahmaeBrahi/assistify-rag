import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Cart from "./Cart";

const mockUseCart = jest.fn();
const mockNavigate = jest.fn();

jest.mock("../context/CartContext", () => ({
  useCart: () => mockUseCart(),
}));

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

function renderCart() {
  return render(
    <MemoryRouter>
      <Cart />
    </MemoryRouter>
  );
}

describe("Cart page", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    mockNavigate.mockClear();
  });

  it("renders the page title", () => {
    mockUseCart.mockReturnValue({
      cart: [],
      subtotal: 0,
      total: 0,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText("Shopping Cart")).toBeInTheDocument();
  });

  it("shows empty cart message when cart is empty", () => {
    mockUseCart.mockReturnValue({
      cart: [],
      subtotal: 0,
      total: 0,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText(/your cart is empty/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /shop now/i })).toBeInTheDocument();
  });

  it("navigates to /products when Shop Now is clicked", async () => {
    mockUseCart.mockReturnValue({
      cart: [],
      subtotal: 0,
      total: 0,
      removeFromCart: jest.fn(),
    });

    renderCart();

    await user.click(screen.getByRole("button", { name: /shop now/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/products");
  });

  it("renders cart items", () => {
    mockUseCart.mockReturnValue({
      cart: [
        { id: 1, name: "Pulse Oximeter", price: 450, emoji: "🩺" },
        { id: 2, name: "Thermometer", price: 120, emoji: "🌡️" },
      ],
      subtotal: 570,
      total: 620,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText("Pulse Oximeter")).toBeInTheDocument();
    expect(screen.getByText("Thermometer")).toBeInTheDocument();
  });

  it("renders item emojis", () => {
    mockUseCart.mockReturnValue({
      cart: [{ id: 1, name: "Oximeter", price: 450, emoji: "🩺" }],
      subtotal: 450,
      total: 500,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText("🩺")).toBeInTheDocument();
  });

  it("renders item price in EGP safely", () => {
    mockUseCart.mockReturnValue({
      cart: [{ id: 1, name: "Oximeter", price: 450, emoji: "🩺" }],
      subtotal: 450,
      total: 500,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getAllByText(/EGP\s*450/)[0]).toBeInTheDocument();
  });

  it("shows order summary when cart has items", () => {
    mockUseCart.mockReturnValue({
      cart: [{ id: 1, name: "Oximeter", price: 450, emoji: "🩺" }],
      subtotal: 450,
      total: 500,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText("Order Summary")).toBeInTheDocument();
    expect(screen.getAllByText(/EGP\s*450/)[0]).toBeInTheDocument();
    expect(screen.getByText(/EGP\s*500/)).toBeInTheDocument();
  });

  it("shows fixed shipping fee", () => {
    mockUseCart.mockReturnValue({
      cart: [{ id: 1, name: "Oximeter", price: 450, emoji: "🩺" }],
      subtotal: 450,
      total: 500,
      removeFromCart: jest.fn(),
    });

    renderCart();

    expect(screen.getByText("EGP 50")).toBeInTheDocument();
  });

  it("calls removeFromCart with correct index", async () => {
    const mockRemove = jest.fn();

    mockUseCart.mockReturnValue({
      cart: [
        { id: 1, name: "Oximeter", price: 450 },
        { id: 2, name: "Thermometer", price: 120 },
      ],
      subtotal: 570,
      total: 620,
      removeFromCart: mockRemove,
    });

    renderCart();

    const removeBtns = screen.getAllByRole("button", { name: /remove/i });

    await user.click(removeBtns[0]);

    expect(mockRemove).toHaveBeenCalledWith(0);
  });

  it("navigates to /payment on checkout", async () => {
    mockUseCart.mockReturnValue({
      cart: [{ id: 1, name: "Oximeter", price: 450 }],
      subtotal: 450,
      total: 500,
      removeFromCart: jest.fn(),
    });

    renderCart();

    await user.click(
      screen.getByRole("button", { name: /proceed to checkout/i })
    );

    expect(mockNavigate).toHaveBeenCalledWith("/payment");
  });
});