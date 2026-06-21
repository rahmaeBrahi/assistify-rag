import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ProductCard from "./ProductCard";

const mockAddToCart = jest.fn();

jest.mock("../context/CartContext", () => ({
  useCart: () => ({ addToCart: mockAddToCart }),
}));

const baseProduct = {
  id: 1,
  name: "Pulse Oximeter",
  description: "Wireless fingertip oximeter",
  price: 550,
  emoji: "🩺",
};

beforeEach(() => {
  mockAddToCart.mockClear();
  jest.spyOn(window, "alert").mockImplementation(() => {});
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe("ProductCard", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
  });

  it("renders product name, description, and emoji", () => {
    render(<ProductCard product={baseProduct} />);

    expect(screen.getByText("Pulse Oximeter")).toBeInTheDocument();
    expect(screen.getByText("Wireless fingertip oximeter")).toBeInTheDocument();
    expect(screen.getByText("🩺")).toBeInTheDocument();
  });

  it("renders regular price when no discount is provided", () => {
    render(<ProductCard product={baseProduct} />);

    expect(screen.getByText("EGP 550")).toBeInTheDocument();
    expect(screen.queryByText(/old/i)).not.toBeInTheDocument();
  });

  it("renders discounted price and original price when discount props are provided", () => {
    render(<ProductCard product={baseProduct} discountedPrice={450} discountPercent={18} />);

    expect(screen.getByText("EGP 550")).toBeInTheDocument();
    expect(screen.getByText("EGP 450")).toBeInTheDocument();
  });

  it("renders discount badge with correct percentage", () => {
    render(<ProductCard product={baseProduct} discountedPrice={450} discountPercent={18} />);

    expect(screen.getByText("-18%")).toBeInTheDocument();
  });

  it("does not render discount badge when discountPercent is not provided", () => {
    render(<ProductCard product={baseProduct} />);

    expect(screen.queryByText(/-\d+%/)).not.toBeInTheDocument();
  });

  it("renders Add to Cart button", () => {
    render(<ProductCard product={baseProduct} />);

    expect(screen.getByRole("button", { name: /add to cart/i })).toBeInTheDocument();
  });

  it("calls addToCart with product and regular price when no discount", async () => {
    render(<ProductCard product={baseProduct} />);

    await user.click(screen.getByRole("button", { name: /add to cart/i }));

    expect(mockAddToCart).toHaveBeenCalledWith(baseProduct, 550);
  });

  it("calls addToCart with discounted price when discount is provided", async () => {
    render(<ProductCard product={baseProduct} discountedPrice={450} discountPercent={18} />);

    await user.click(screen.getByRole("button", { name: /add to cart/i }));

    expect(mockAddToCart).toHaveBeenCalledWith(baseProduct, 450);
  });

  it("shows alert with product name when added to cart", async () => {
    render(<ProductCard product={baseProduct} />);

    await user.click(screen.getByRole("button", { name: /add to cart/i }));

    expect(window.alert).toHaveBeenCalledWith("Pulse Oximeter added to cart!");
  });

  it("formats large prices with locale separator", () => {
    const expensiveProduct = { ...baseProduct, price: 12000 };
    render(<ProductCard product={expensiveProduct} />);

    expect(screen.getByText("EGP 12,000")).toBeInTheDocument();
  });

  it("calls addToCart exactly once per click", async () => {
    render(<ProductCard product={baseProduct} />);

    await user.click(screen.getByRole("button", { name: /add to cart/i }));

    expect(mockAddToCart).toHaveBeenCalledTimes(1);
  });
});