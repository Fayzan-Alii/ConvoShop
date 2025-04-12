export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Product {
  id: string;
  title: string;
  price: number;
  image_url: string;
  store_url: string;
  description: string;
  created_at: string;
}

export interface Bookmark {
  id: string;
  user_id: string;
  product_id: string;
  price_threshold: number | null;
  created_at: string;
}

export interface CartItem {
  id: string;
  user_id: string;
  product_id: string;
  quantity: number;
  created_at: string;
}