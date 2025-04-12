const express = require('express');
const router = express.Router();
const {
  getProducts,
  getProductById,
  createSampleProducts
} = require('../controllers/productController');
const { protect } = require('../middleware/authMiddleware');

router.route('/').get(protect, getProducts);
router.route('/sample').post(protect, createSampleProducts);
router.route('/:id').get(protect, getProductById);

module.exports = router;
