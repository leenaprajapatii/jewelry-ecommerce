function updateTotalPrice(itemId) {
    let quantityInput = document.getElementById(`quantity_${itemId}`);
    let totalPriceElement = document.getElementById(`total_price_${itemId}`);
    let priceElement = document.getElementById(`price_${itemId}`);

    let quantity = parseInt(quantityInput.value);
    let price = parseFloat(priceElement.innerText.replace('₹', '').trim());

    if (quantity < 1) {
        quantity = 1;
        quantityInput.value = 1; // Prevent negative quantity
    }

    let totalPrice = price * quantity;
    totalPriceElement.innerText = `₹${totalPrice.toFixed(2)}`;

    updateCartSummary(); // Update subtotal & total dynamically
}

function updateCartSummary() {
    let totalElements = document.querySelectorAll('[id^="total_price_"]');
    let subtotal = 0;

    totalElements.forEach(element => {
        subtotal += parseFloat(element.innerText.replace('₹', '').trim());
    });

    document.getElementById('subtotal').innerText = `₹${subtotal.toFixed(2)}`;

    let discountElement = document.getElementById('discount');
    let discount = parseFloat(discountElement.innerText.replace('₹', '').trim()) || 0;

    let shippingCost = parseFloat(document.querySelector('input[name="shipping"]:checked')?.value || 0);

    let finalTotal = subtotal - discount + shippingCost;
    document.getElementById('total').innerText = `₹${finalTotal.toFixed(2)}`;
}
