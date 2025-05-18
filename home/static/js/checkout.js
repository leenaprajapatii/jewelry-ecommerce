$(document).ready(function() {
    $('.paywithRazorpay').click(function(e) {
        e.preventDefault();
        
        var fname = $("[name='fname']").val();
        var lname = $("[name='lname']").val();
        var email = $("[name='email']").val();
        var phone = $("[name='phone']").val();
        var country = $("[name='country']").val();
        var city = $("[name='city']").val();
        var address = $("[name='address']").val();
        var state = $("[name='state']").val();
        var pincode = $("[name='pincode']").val();
        
        var token = $("[name='csrfmiddlewaretoken']").val(); // Fixed spelling mistake

        if (fname == "" || lname == "" || email == "" || phone == "" || address == "" || city == "" || state == "" || country == "" || pincode == "") {
            swal("Alert!", "All fields are mandatory!", "error");
            return false;
        } else {
            $.ajax({
                method: "GET",
                url: "/proceed-to-pay/",
                success: function(response) {
                    console.log(response);
                    
                    var options = {
                        "key": "rzp_test_jXjkX6CGEqnP8h", 
                        "amount": response.total_price, 
                        "currency": "INR",
                        "name": "Jewelry Store", 
                        "description": "Thank you",
                        "image": "https://example.com/your_logo",
                        "handler": function(response) {
                            alert(response.razorpay_payment_id);
                            
                            var data = {
                                "fname": fname,
                                "lname": lname,
                                "email": email,
                                "phone": phone,
                                "address": address,
                                "city": city,
                                "state": state,
                                "country": country,
                                "pincode": pincode,
                                "payment_mode": "Paid by Razorpay",
                                "payment_id": response.razorpay_payment_id, // Fixed incorrect variable
                                "csrfmiddlewaretoken": token // Send CSRF token here
                            };

                            $.ajax({
                                method: "POST",
                                url: "/placeorder/",
                                data: data,
                                success: function(response) {
                                    swal("Congratulations!", response.status, "success").then((value) => {
                                        window.location.href = response.redirect_url;
                                    });
                                }
                            });
                        },
                        "prefill": {
                            "name": fname + " " + lname, 
                            "email": email, 
                            "contact": phone 
                        },
                        "notes": {
                            "address": "Razorpay Corporate Office"
                        },
                        "theme": {
                            "color": "#3399cc"
                        }
                    };

                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                }
            });
        }
    });
});
