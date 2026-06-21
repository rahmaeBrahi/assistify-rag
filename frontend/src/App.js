import { BrowserRouter, Routes, Route } from "react-router-dom";
import { CartProvider } from "./context/CartContext";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ChatWidget from "./components/ChatWidget";

import Home from "./pages/Home";
import Products from "./pages/Products";
import Integrations from "./pages/Integrations";
import Cart from "./pages/Cart";
import Payment from "./pages/Payment";
import Confirmation from "./pages/Confirmation";
import Tracking from "./pages/Tracking";
import Review from "./pages/Review";
import Offers from "./pages/Offers";
import ChatPage from "./pages/ChatPage";
import Profile from "./pages/Profile";
import Orders from "./pages/Orders";

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/integrations" element={<Integrations />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/payment" element={<Payment />} />
          <Route path="/confirmation" element={<Confirmation />} />
          <Route path="/tracking" element={<Tracking />} />
          <Route path="/review" element={<Review />} />
          <Route path="/offers" element={<Offers />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/orders" element={<Orders />} />
        </Routes>
          <ChatWidget />
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}
