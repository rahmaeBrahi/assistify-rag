import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatWidget from "./ChatWidget";

const mockSendChatMessage = jest.fn();

jest.mock("../services/api", () => ({
  sendChatMessage: (...args) => mockSendChatMessage(...args),
}));

beforeAll(() => {
  window.HTMLElement.prototype.scrollIntoView = jest.fn();
});

afterAll(() => {
  window.HTMLElement.prototype.scrollIntoView = undefined;
});

describe("ChatWidget", () => {
  let user;

  beforeEach(() => {
    user = userEvent.setup();
    mockSendChatMessage.mockClear();
  });

  it("renders FAB button closed by default", () => {
    render(<ChatWidget />);

    expect(screen.getByRole("button", { name: /toggle chat/i })).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/اكتب رسالتك/i)).not.toBeInTheDocument();
  });

  it("opens chat panel when FAB is clicked", async () => {
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    expect(screen.getByPlaceholderText(/اكتب رسالتك/i)).toBeInTheDocument();
  });

  it("shows initial greeting message when opened", async () => {
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    expect(screen.getByText(/مرحباً/i)).toBeInTheDocument();
  });

  it("updates input value as user types", async () => {
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    const input = screen.getByPlaceholderText(/اكتب رسالتك/i);

    await user.type(input, "Hello there");

    expect(input).toHaveValue("Hello there");
  });

  it("sends message and shows bot reply", async () => {
    mockSendChatMessage.mockResolvedValueOnce({
      reply: "Hello back!",
      conversationId: "cid123",
    });

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));
    await user.type(screen.getByPlaceholderText(/اكتب رسالتك/i), "Hi");

    await user.click(screen.getByRole("button", { name: /➤/i }));

    await waitFor(() =>
      expect(screen.getByText("Hello back!")).toBeInTheDocument()
    );

    expect(mockSendChatMessage).toHaveBeenCalledWith("Hi", null);
  });

  it("sends message on Enter key press", async () => {
    mockSendChatMessage.mockResolvedValueOnce({
      reply: "Got it",
      conversationId: "cid1",
    });

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    const input = screen.getByPlaceholderText(/اكتب رسالتك/i);

    await user.type(input, "Hello{Enter}");

    await waitFor(() =>
      expect(mockSendChatMessage).toHaveBeenCalledWith("Hello", null)
    );
  });

  it("clears input after sending message", async () => {
    mockSendChatMessage.mockResolvedValueOnce({
      reply: "OK",
      conversationId: "cid1",
    });

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    const input = screen.getByPlaceholderText(/اكتب رسالتك/i);

    await user.type(input, "Test message");
    await user.click(screen.getByRole("button", { name: /➤/i }));

    await waitFor(() => expect(input).toHaveValue(""));
  });

  it("does not send empty message", async () => {
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));
    await user.click(screen.getByRole("button", { name: /➤/i }));

    expect(mockSendChatMessage).not.toHaveBeenCalled();
  });

  it("does not send whitespace-only input", async () => {
    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    await user.type(screen.getByPlaceholderText(/اكتب رسالتك/i), "   ");

    await user.click(screen.getByRole("button", { name: /➤/i }));

    expect(mockSendChatMessage).not.toHaveBeenCalled();
  });

  it("shows error message when API fails", async () => {
    mockSendChatMessage.mockRejectedValueOnce(new Error("Network error"));

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));
    await user.type(screen.getByPlaceholderText(/اكتب رسالتك/i), "Hi");
    await user.click(screen.getByRole("button", { name: /➤/i }));

    await waitFor(() =>
      expect(
        screen.getByText(/sorry, i encountered an error/i)
      ).toBeInTheDocument()
    );
  });

  it("disables input and button while loading", async () => {
    let resolve;
    mockSendChatMessage.mockReturnValueOnce(
      new Promise((r) => (resolve = r))
    );

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));
    await user.type(screen.getByPlaceholderText(/اكتب رسالتك/i), "Hi");
    await user.click(screen.getByRole("button", { name: /➤/i }));

    expect(screen.getByPlaceholderText(/اكتب رسالتك/i)).toBeDisabled();
    expect(screen.getByRole("button", { name: /➤/i })).toBeDisabled();

    resolve({ reply: "OK", conversationId: "c1" });
  });

  it("passes conversationId to next message", async () => {
    mockSendChatMessage
      .mockResolvedValueOnce({
        reply: "First reply",
        conversationId: "conv-abc",
      })
      .mockResolvedValueOnce({
        reply: "Second reply",
        conversationId: "conv-abc",
      });

    render(<ChatWidget />);

    await user.click(screen.getByRole("button", { name: /toggle chat/i }));

    const input = screen.getByPlaceholderText(/اكتب رسالتك/i);

    await user.type(input, "First");
    await user.click(screen.getByRole("button", { name: /➤/i }));

    await waitFor(() =>
      expect(screen.getByText("First reply")).toBeInTheDocument()
    );

    await user.type(input, "Second");
    await user.click(screen.getByRole("button", { name: /➤/i }));

    await waitFor(() =>
      expect(mockSendChatMessage).toHaveBeenLastCalledWith(
        "Second",
        "conv-abc"
      )
    );
  });
});