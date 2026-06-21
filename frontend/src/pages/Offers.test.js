import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import Offers from "./Offers";

const mockFetchOffers = jest.fn();
const mockNavigate = jest.fn();

jest.mock("../services/api", () => ({
  fetchOffers: () => mockFetchOffers(),
}));

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

jest.mock("../components/ProductCard", () => ({ product, discountedPrice, discountPercent }) => (
  <div data-testid="product-card">
    <span>{product.name}</span>
    <span>{discountedPrice}</span>
    <span>{discountPercent}%</span>
  </div>
));

function renderOffers() {
  return render(
    <MemoryRouter>
      <Offers />
    </MemoryRouter>
  );
}

let user;

beforeEach(() => {
  user = userEvent.setup();
  mockNavigate.mockClear();
  mockFetchOffers.mockClear();
});

const mockOfferData = [
  {
    id: 1,
    product: 10,
    product_name: "Pulse Oximeter",
    product_emoji: "🩺",
    original_price: "550.00",
    discounted_price: "450.00",
    discount_percent: 18,
  },
  {
    id: 2,
    product: 20,
    product_name: "Smart Thermometer",
    product_emoji: "🌡️",
    original_price: "200.00",
    discounted_price: "160.00",
    discount_percent: 20,
  },
];

describe("Offers page", () => {
  it("renders the page heading", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    expect(screen.getByText(/personalized offers/i)).toBeInTheDocument();
  });

  it("shows loading text while fetching", () => {
    mockFetchOffers.mockReturnValueOnce(new Promise(() => {}));
    renderOffers();

    expect(screen.getByText(/loading offers/i)).toBeInTheDocument();
  });

  it("renders offer cards after successful fetch", async () => {
    mockFetchOffers.mockResolvedValueOnce(mockOfferData);
    renderOffers();

    await waitFor(() =>
      expect(screen.getAllByTestId("product-card")).toHaveLength(2)
    );
  });

  it("passes correct product name to ProductCard", async () => {
    mockFetchOffers.mockResolvedValueOnce(mockOfferData);
    renderOffers();

    await waitFor(() =>
      expect(screen.getByText("Pulse Oximeter")).toBeInTheDocument()
    );
    expect(screen.getByText("Smart Thermometer")).toBeInTheDocument();
  });

  it("passes discountedPrice to ProductCard", async () => {
    mockFetchOffers.mockResolvedValueOnce(mockOfferData);
    renderOffers();

    await waitFor(() => expect(screen.getByText("450")).toBeInTheDocument());
  });

  it("passes discountPercent to ProductCard", async () => {
    mockFetchOffers.mockResolvedValueOnce(mockOfferData);
    renderOffers();

    await waitFor(() => expect(screen.getByText("18%")).toBeInTheDocument());
  });

  it("handles results wrapper from API response", async () => {
    mockFetchOffers.mockResolvedValueOnce({ results: mockOfferData });
    renderOffers();

    await waitFor(() =>
      expect(screen.getAllByTestId("product-card")).toHaveLength(2)
    );
  });

  it("renders empty grid (no cards) when fetch returns empty array", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );
    expect(screen.queryByTestId("product-card")).not.toBeInTheDocument();
  });

  it("renders empty grid gracefully when fetch fails", async () => {
    mockFetchOffers.mockRejectedValueOnce(new Error("Network error"));
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );
    expect(screen.queryByTestId("product-card")).not.toBeInTheDocument();
  });

  it("hides loading spinner after fetch completes", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );
  });

  it("renders Chat with Support button", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );

    expect(
      screen.getByRole("button", { name: /chat with support/i })
    ).toBeInTheDocument();
  });

  it("navigates to /chat when Chat with Support is clicked", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );

    await user.click(
      screen.getByRole("button", { name: /chat with support/i })
    );

    expect(mockNavigate).toHaveBeenCalledWith("/chat");
  });

  it("navigates to / when Back to Home is clicked", async () => {
    mockFetchOffers.mockResolvedValueOnce([]);
    renderOffers();

    await waitFor(() =>
      expect(screen.queryByText(/loading offers/i)).not.toBeInTheDocument()
    );

    await user.click(screen.getByRole("button", { name: /back to home/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/");
  });
});