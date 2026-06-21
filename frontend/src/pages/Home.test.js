import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "./Home";

const mockNavigate = jest.fn();

jest.mock("react-router-dom", () => ({
  useNavigate: () => mockNavigate,
}));

describe("Home page", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    mockNavigate.mockClear();
  });

  it("renders the hero section title", () => {
    render(<Home />);

    expect(screen.getByText(/your health, our/i)).toBeInTheDocument();
    expect(screen.getByText("Priority")).toBeInTheDocument();
  });

  it("renders the hero badge", () => {
    render(<Home />);

    expect(screen.getByText(/egypt's #1 medical devices platform/i)).toBeInTheDocument();
  });

  it("renders Shop Now and Talk to AI Support buttons", () => {
    render(<Home />);

    expect(screen.getAllByRole("button", { name: /shop now/i })).not.toHaveLength(0);
    expect(screen.getByRole("button", { name: /talk to ai support/i })).toBeInTheDocument();
  });

  it("navigates to /products when first Shop Now is clicked", async () => {
    render(<Home />);

    const shopBtns = screen.getAllByRole("button", { name: /shop now/i });
    await user.click(shopBtns[0]);

    expect(mockNavigate).toHaveBeenCalledWith("/products");
  });

  it("navigates to /chat when Talk to AI Support is clicked", async () => {
    render(<Home />);

    await user.click(screen.getByRole("button", { name: /talk to ai support/i }));

    expect(mockNavigate).toHaveBeenCalledWith("/chat");
  });

  it("renders Explore Products CTA button", async () => {
    render(<Home />);

    const exploreBtns = screen.getAllByRole("button", { name: /explore products/i });
    await user.click(exploreBtns[0]);

    expect(mockNavigate).toHaveBeenCalledWith("/products");
  });

  it("renders all four feature cards", () => {
    render(<Home />);

    expect(screen.getByText("Medical Grade")).toBeInTheDocument();
    expect(screen.getAllByText("AI Support")[0]).toBeInTheDocument();
    expect(screen.getByText("Fast Delivery")).toBeInTheDocument();
    expect(screen.getByText("Secure Payment")).toBeInTheDocument();
  });

  it("renders all four stat values", () => {
    render(<Home />);

    expect(screen.getByText("2,450+")).toBeInTheDocument();
    expect(screen.getByText("8,932")).toBeInTheDocument();
    expect(screen.getByText("98.5%")).toBeInTheDocument();
    expect(screen.getByText("24/7")).toBeInTheDocument();
  });

  it("renders floating card metrics", () => {
    render(<Home />);

    expect(screen.getByText("72 BPM")).toBeInTheDocument();
    expect(screen.getByText("120/80 mmHg")).toBeInTheDocument();
  });

  it("renders CTA section heading", () => {
    render(<Home />);

    expect(screen.getByText(/ready to take control of your health/i)).toBeInTheDocument();
  });
});