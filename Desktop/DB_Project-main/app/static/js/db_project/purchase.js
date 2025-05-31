document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("purchaseForm");
  const message = document.getElementById("message");
  const username = localStorage.getItem("loggedInUsername");

  if (!username) {
    alert("You must be logged in to upgrade.");
    window.location.href = "/";
    return;
  }

  const cardNumberInput = document.getElementById("cardNumber");
  const expiryInput = document.getElementById("expiry");
  const cvvInput = document.getElementById("cvv");

  // کارت: فقط عدد و فاصله
  cardNumberInput.addEventListener("input", () => {
    let val = cardNumberInput.value.replace(/\D/g, "");
    if (val.length > 16) val = val.slice(0, 16);
    cardNumberInput.value = val.match(/.{1,4}/g)?.join("-") || "";
  });

  // تاریخ: فقط عدد و اسلش
  expiryInput.addEventListener("input", () => {
    let val = expiryInput.value.replace(/\D/g, "");
    if (val.length > 4) val = val.slice(0, 4);
    if (val.length > 2) val = val.slice(0, 2) + "/" + val.slice(2);
    expiryInput.value = val;
  });

  // CVV: فقط عدد، نهایت 4 رقم
  cvvInput.addEventListener("input", () => {
    cvvInput.value = cvvInput.value.replace(/\D/g, "").slice(0, 4);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const cardNumber = cardNumberInput.value.replace(/[\s-]/g, "");
    const expiry = expiryInput.value.trim();
    const cvv = cvvInput.value.trim();

    if (cardNumber.length !== 16) {
      message.textContent = "Card number must be 16 digits.";
      return;
    }

    if (!/^\d{2}\/\d{2}$/.test(expiry)) {
      message.textContent = "Invalid expiry format. Use MM/YY.";
      return;
    }

    if (cvv.length < 3 || cvv.length > 4) {
      message.textContent = "CVV must be 3 or 4 digits.";
      return;
    }

    const res = await fetch("/purchase-premium", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });

    const result = await res.json();
    if (res.ok) {
      message.textContent = "You are now a Premium user!";
      message.style.color = "green";
      setTimeout(() => {
        window.location.href = "/profile";
      }, 2000);
    } else {
      message.textContent = result.detail || "Upgrade failed.";
      message.style.color = "red";
    }
  });
});
