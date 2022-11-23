var cartTotal = document.getElementById("cart-total");

document.querySelectorAll(".update-cart").forEach((btnUpd) => {
  btnUpd.addEventListener("click", () => {
    var productId = btnUpd.dataset.product;
    var productPrice = btnUpd.dataset.price;
    var action = btnUpd.dataset.action;

    if (user == "AnonymousUser") {
      addCookieItem(
        {
          id: productId,
          price: productPrice,
        },
        action
      );
    } else {
      updateUserOrder(productId, action);
    }
  });
});

const updateUserOrder = (productId, action) => {
  var url = "/update_item/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({
      productId: productId,
      action: action,
    }),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      cartTotal.innerHTML = data.cartTotal;
      var row = document.getElementById(`row${productId}`);
      var totalItems = document.getElementById(`totalItems`);
      var totalValue = document.getElementById(`totalValue`);

      if (row) {
        if (data.productQuantity <= 0) {
          row.remove();
        } else {
          var cartItemQuantity = document.getElementById(`q${productId}`);
          var cartItemTotalPrice = document.getElementById(`t${productId}`);

          cartItemQuantity.innerHTML = data.productQuantity;
          cartItemTotalPrice.innerHTML = `$${data.orderItemTotalValue.toFixed(
            2
          )}`;
        }
        totalItems.innerHTML = data.cartTotal;
        totalValue.innerHTML = `$${data.orderTotalValue.toFixed(2)}`;
      }
      if (action == "buyNow") {
        window.location.href = "/cart/";
      }
    });
};

function addCookieItem(product, action) {
  if (action == "add" || action == "buyNow") {
    if (cart[product.id] == undefined) {
      cart[product.id] = { quantity: 1, price: product.price };
    } else {
      cart[product.id]["quantity"] += 1;
    }
  }

  if (action == "remove") {
    cart[product.id]["quantity"] -= 1;

    if (cart[product.id]["quantity"] <= 0) {
      console.log("Item should be deleted");
      delete cart[product.id];
      row.remove();
    }
  }
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";

  totalItems = 0;
  totalValue = 0;

  Object.keys(cart).forEach((k) => {
    totalItems += cart[k]["quantity"];
    totalValue += parseFloat(cart[k]["price"]) * cart[k]["quantity"];
  });
  cartTotal.innerHTML = totalItems;

  var row = document.getElementById(`row${product.id}`);
  if (row) {
    var cartItemQuantity = document.getElementById(`q${product.id}`);
    var cartItemTotalPrice = document.getElementById(`t${product.id}`);
    var totalItemsE = document.getElementById(`totalItems`);
    var totalValueE = document.getElementById(`totalValue`);

    totalItemsE.innerHTML = totalItems;
    totalValueE.innerHTML = `$${totalValue.toFixed(2)}`;

    cartItemQuantity.innerHTML = cart[product.id]["quantity"];
    cartItemTotalPrice.innerHTML = `$${(
      product.price * parseFloat(cart[product.id]["quantity"])
    ).toFixed(2)}`;
  }

  if (action == "buyNow") {
    //buyNow action (redirects to cart)
    window.location.href = "/cart/";
  }
}
