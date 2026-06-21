import { act, renderHook } from "@testing-library/react";
import { CartProvider, useCart } from "./CartContext";

describe("CartContext", () => {
  it("initializes with empty cart and zero totals", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    expect(result.current.cart).toEqual([]);
    expect(result.current.subtotal).toBe(0);
    expect(result.current.total).toBe(0);
  });

  it("addToCart adds a product with the given price", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, name: "Oximeter", price: 100 }, 100);
    });

    expect(result.current.cart).toHaveLength(1);
    expect(result.current.cart[0]).toMatchObject({ id: 1, name: "Oximeter", price: 100 });
  });

  it("addToCart uses the provided price over product.price", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 200 }, 150);
    });

    expect(result.current.cart[0].price).toBe(150);
  });

  it("addToCart falls back to product.price when price arg is not provided", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 200 });
    });

    expect(result.current.cart[0].price).toBe(200);
  });

  it("calculates subtotal correctly with one item", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 300 }, 300);
    });

    expect(result.current.subtotal).toBe(300);
  });

  it("adds shipping (50 EGP) to total when cart is non-empty", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 300 }, 300);
    });

    expect(result.current.total).toBe(350);
  });

  it("total equals 0 when cart is empty (no shipping added)", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    expect(result.current.total).toBe(0);
  });

  it("calculates subtotal and total with multiple items", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 100 }, 100);
      result.current.addToCart({ id: 2, price: 200 }, 200);
    });

    expect(result.current.subtotal).toBe(300);
    expect(result.current.total).toBe(350);
  });

  it("removeFromCart removes item at the given index", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 100 }, 100);
      result.current.addToCart({ id: 2, price: 200 }, 200);
    });

    act(() => {
      result.current.removeFromCart(0);
    });

    expect(result.current.cart).toHaveLength(1);
    expect(result.current.cart[0].id).toBe(2);
  });

  it("clearCart empties the cart", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 100 }, 100);
      result.current.addToCart({ id: 2, price: 200 }, 200);
    });

    act(() => {
      result.current.clearCart();
    });

    expect(result.current.cart).toHaveLength(0);
    expect(result.current.subtotal).toBe(0);
    expect(result.current.total).toBe(0);
  });

  it("setLastOrder stores last order data", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });
    const order = { orderNumber: "ORD-001", total: 350 };

    act(() => {
      result.current.setLastOrder(order);
    });

    expect(result.current.lastOrder).toEqual(order);
  });

  it("lastOrder is null initially", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    expect(result.current.lastOrder).toBeNull();
  });

  it("allows adding duplicate products (same id)", () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });

    act(() => {
      result.current.addToCart({ id: 1, price: 100 }, 100);
      result.current.addToCart({ id: 1, price: 100 }, 100);
    });

    expect(result.current.cart).toHaveLength(2);
    expect(result.current.subtotal).toBe(200);
  });
});
