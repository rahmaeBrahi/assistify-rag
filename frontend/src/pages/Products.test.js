import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Products from "./Products";

const mockFetchProducts = jest.fn();

jest.mock("../components/ProductCard", () => ({ product }) => (
  <div data-testid="product-card">{product.name}</div>
));

jest.mock("../services/api", () => ({
  fetchProducts: (...args) => mockFetchProducts(...args),
}));

let user;

beforeEach(() => {
  jest.useFakeTimers();
  user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
  mockFetchProducts.mockClear();
});

afterEach(() => {
  jest.runOnlyPendingTimers();
  jest.useRealTimers();
});

describe("Products page", () => {
  it("renders the page heading", () => {
    mockFetchProducts.mockResolvedValueOnce({ results: [] });
    render(<Products />);

    expect(screen.getByText("Our Products")).toBeInTheDocument();
  });

  it("renders the search input", () => {
    mockFetchProducts.mockResolvedValueOnce({ results: [] });
    render(<Products />);

    expect(screen.getByPlaceholderText(/search products/i)).toBeInTheDocument();
  });

  it("shows loading text initially", () => {
    mockFetchProducts.mockReturnValueOnce(new Promise(() => {}));
    render(<Products />);

    expect(screen.getByText(/loading products/i)).toBeInTheDocument();
  });

  it("renders product cards after successful fetch", async () => {
    mockFetchProducts.mockResolvedValueOnce({
      results: [
        { id: 1, name: "Pulse Oximeter" },
        { id: 2, name: "Thermometer" },
      ],
    });

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(screen.getAllByTestId("product-card")).toHaveLength(2)
    );
  });

  it("handles flat array response", async () => {
    mockFetchProducts.mockResolvedValueOnce([
      { id: 1, name: "Oximeter" },
    ]);

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(screen.getByTestId("product-card")).toBeInTheDocument()
    );
  });

  it("shows empty state when no products returned", async () => {
    mockFetchProducts.mockResolvedValueOnce({ results: [] });

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(screen.getByText(/no products found/i)).toBeInTheDocument()
    );
  });

  it("shows error message when fetch fails", async () => {
    mockFetchProducts.mockRejectedValueOnce(new Error("Network error"));

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(screen.getByText(/failed to load products/i)).toBeInTheDocument()
    );
  });

  it("debounces fetch — does not call API on every keystroke", async () => {
    mockFetchProducts.mockResolvedValue({ results: [] });

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    const input = screen.getByPlaceholderText(/search products/i);

    await user.type(input, "abc");

    expect(mockFetchProducts).toHaveBeenCalledTimes(1);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(mockFetchProducts).toHaveBeenCalledTimes(2)
    );
  });

  it("calls fetchProducts with search query after debounce", async () => {
    mockFetchProducts.mockResolvedValue({ results: [] });

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    const input = screen.getByPlaceholderText(/search products/i);

    await user.type(input, "oxygen");

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(mockFetchProducts).toHaveBeenCalledWith("oxygen")
    );
  });

  it("shows empty message including search term", async () => {
    mockFetchProducts.mockResolvedValue({ results: [] });

    render(<Products />);

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    const input = screen.getByPlaceholderText(/search products/i);

    await user.type(input, "xyz");

    await act(async () => {
      jest.advanceTimersByTime(300);
    });

    await waitFor(() =>
      expect(screen.getByText(/"xyz"/)).toBeInTheDocument()
    );
  });
});