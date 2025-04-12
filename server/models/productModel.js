const mongoose = require('mongoose');

const productSchema = mongoose.Schema(
  {
    title: {
      type: String,
      required: true,
    },
    price: {
      type: Number,
      required: true,
    },
    image_url: {
      type: String,
    },
    store_url: {
      type: String,
      required: true,
    },
    description: {
      type: String,
    },
    store: {
      type: String,
    }
  },
  {
    timestamps: true,
  }
);

const Product = mongoose.model('Product', productSchema);

module.exports = Product;
