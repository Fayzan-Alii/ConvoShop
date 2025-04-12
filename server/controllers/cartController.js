const asyncHandler = require('../utils/asyncHandler');
const CartItem = require('../models/cartItemModel');
const Product = require('../models/productModel');

// @desc    Get user cart items
// @route   GET /api/cart
// @access  Private
const getCartItems = asyncHandler(async (req, res) => {
  const cartItems = await CartItem.find({ user: req.user._id }).populate('product');
  res.json(cartItems);
});

// @desc    Add item to cart
// @route   POST /api/cart
// @access  Private
const addCartItem = asyncHandler(async (req, res) => {
  const { productId, quantity } = req.body;

  // Check if product exists
  const product = await Product.findById(productId);
  if (!product) {
    res.status(404);
    throw new Error('Product not found');
  }

  // Check if item already in cart
  let cartItem = await CartItem.findOne({
    user: req.user._id,
    product: productId,
  });

  if (cartItem) {
    // Update quantity
    cartItem.quantity = quantity || cartItem.quantity + 1;
    await cartItem.save();
  } else {
    // Create new cart item
    cartItem = await CartItem.create({
      user: req.user._id,
      product: productId,
      quantity: quantity || 1,
    });
  }

  res.status(201).json(await cartItem.populate('product'));
});

// @desc    Update cart item quantity
// @route   PUT /api/cart/:id
// @access  Private
const updateCartItem = asyncHandler(async (req, res) => {
  const { quantity } = req.body;

  const cartItem = await CartItem.findById(req.params.id);

  if (!cartItem) {
    res.status(404);
    throw new Error('Cart item not found');
  }

  // Check if this cart item belongs to the logged in user
  if (cartItem.user.toString() !== req.user._id.toString()) {
    res.status(401);
    throw new Error('Not authorized');
  }

  cartItem.quantity = quantity;
  const updatedCartItem = await cartItem.save();
  res.json(await updatedCartItem.populate('product'));
});

// @desc    Remove item from cart
// @route   DELETE /api/cart/:id
// @access  Private
const removeCartItem = asyncHandler(async (req, res) => {
  const cartItem = await CartItem.findById(req.params.id);

  if (!cartItem) {
    res.status(404);
    throw new Error('Cart item not found');
  }

  // Check if this cart item belongs to the logged in user
  if (cartItem.user.toString() !== req.user._id.toString()) {
    res.status(401);
    throw new Error('Not authorized');
  }

  await CartItem.deleteOne({ _id: req.params.id });
  res.json({ message: 'Item removed from cart' });
});

module.exports = {
  getCartItems,
  addCartItem,
  updateCartItem,
  removeCartItem,
};
