const express = require('express');
const router = express.Router();
const {
  getCartItems,
  addCartItem,
  updateCartItem,
  removeCartItem,
} = require('../controllers/cartController');
const { protect } = require('../middleware/authMiddleware');

router.route('/')
  .get(protect, getCartItems)
  .post(protect, addCartItem);

router.route('/:id')
  .put(protect, updateCartItem)
  .delete(protect, removeCartItem);

module.exports = router;
