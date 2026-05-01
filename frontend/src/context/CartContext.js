import { createContext, useContext, useState } from "react";

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);
  const [lastOrder, setLastOrder] = useState(null);

  const addToCart = (product, price) => {
    const numericPrice = parseFloat(price || product.price) || 0;
    setCart((prev) => [...prev, { ...product, price: numericPrice }]);
  };

  const removeFromCart = (index) => {
    setCart((prev) => prev.filter((_, i) => i !== index));
  };

  const clearCart = () => setCart([]);

  const subtotal = cart.reduce((sum, item) => sum + parseFloat(item.price), 0);
  const total = subtotal + (cart.length > 0 ? 50 : 0);

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        removeFromCart,
        clearCart,
        subtotal,
        total,
        lastOrder,
        setLastOrder,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}