import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Confirmation from "./Confirmation";

const mockUseCart = jest.fn();
const mockNavigate = jest.fn();

jest.mock("../context/CartContext", () => ({
  useCart: () => mockUseCart(),
}));

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

function renderConfirmation() {
  return render(
    <MemoryRouter>
      <Confirmation />
    </MemoryRouter>
  );
}

const mockOrder = {
  orderNumber: "ORD-2026-001",
  total: 500,
  cart: [
    { id: 1, name: "Pulse Oximeter", emoji: "🩺", price: 450 },
    { id: 2, name: "Thermometer", emoji: "🌡️", price: 50 },
  ],
};

describe("Confirmation page", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    mockNavigate.mockClear();
  });

  it("shows fallback message when no lastOrder exists", () => {
    mockUseCart.mockReturnValue({ lastOrder: null });
    renderConfirmation();

    expect(screen.getByText(/no order found/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /browse products/i })).toBeInTheDocument();
  });

  it("navigates to /products from fallback Browse Products button", async () => {
    mockUseCart.mockReturnValue({ lastOrder: null });
    renderConfirmation();

    await user.click(screen.getByRole("button", { name: /browse products/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/products");
  });

  it("shows Order Confirmed heading when lastOrder exists", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText("Order Confirmed!")).toBeInTheDocument();
  });

  it("renders the checkmark emoji", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText("✅")).toBeInTheDocument();
  });

  it("renders the order number", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText("ORD-2026-001")).toBeInTheDocument();
  });

  it("renders all cart items from lastOrder", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText(/pulse oximeter/i)).toBeInTheDocument();
    expect(screen.getByText(/thermometer/i)).toBeInTheDocument();
  });

  it("renders item emojis", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText(/🩺/)).toBeInTheDocument();
    expect(screen.getByText(/🌡️/)).toBeInTheDocument();
  });

  it("renders total amount", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText("EGP 500")).toBeInTheDocument();
  });

  it("renders estimated delivery text", () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    expect(screen.getByText(/5.7 business days/i)).toBeInTheDocument();
  });

  it("navigates to /tracking when Track Order is clicked", async () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    await user.click(screen.getByRole("button", { name: /track order/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/tracking");
  });

  it("navigates to /review when Leave Review is clicked", async () => {
    mockUseCart.mockReturnValue({ lastOrder: mockOrder });
    renderConfirmation();

    await user.click(screen.getByRole("button", { name: /leave review/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/review");
  });
});