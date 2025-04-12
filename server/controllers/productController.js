const asyncHandler = require('../utils/asyncHandler');
const Product = require('../models/productModel');

// @desc    Get all products
// @route   GET /api/products
// @access  Private
const getProducts = asyncHandler(async (req, res) => {
  const products = await Product.find({});
  res.json(products);
});

// @desc    Get product by ID
// @route   GET /api/products/:id
// @access  Private
const getProductById = asyncHandler(async (req, res) => {
  const product = await Product.findById(req.params.id);
  
  if (product) {
    res.json(product);
  } else {
    res.status(404);
    throw new Error('Product not found');
  }
});

// @desc    Create sample products
// @route   POST /api/products/sample
// @access  Private
const createSampleProducts = asyncHandler(async (req, res) => {
  // Check if products already exist
  const productsCount = await Product.countDocuments();
  
  if (productsCount > 0) {
    res.status(400);
    throw new Error('Sample products already exist');
  }

  const sampleProducts = [
    {
      title: 'Premium Wireless Headphones',
      price: 199.99,
      image_url: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300',
      store_url: 'https://example.com/headphones',
      description: 'High-quality wireless headphones with noise cancellation',
      store: 'AudioTech'
    },
    {
      title: 'Smart Fitness Watch',
      price: 149.99,
      image_url: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300',
      store_url: 'https://example.com/watch',
      description: 'Fitness tracker with heart rate monitoring and GPS',
      store: 'TechGear'
    }
  ];

  await Product.insertMany(sampleProducts);
  
  res.status(201).json({ message: 'Sample products created' });
});

module.exports = {
  getProducts,
  getProductById,
  createSampleProducts
};
